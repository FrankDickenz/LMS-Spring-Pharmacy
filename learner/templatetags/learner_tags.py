from django import template
from django.db.models import Count
from django.urls import reverse
from courses.models import AssessmentResult,QuizResult,Quiz,PeerReview, LTIResult,Submission,Course, Section, Material, Assessment,MaterialRead, AssessmentRead, QuestionAnswer, Submission, AssessmentScore, GradeRange, CourseProgress
import random
import re
from decimal import Decimal
from django.urls import reverse
from decimal import Decimal, ROUND_HALF_UP
import logging
from django.db import models  # Tambah import ini untuk Prefetch
from django.db.models import Prefetch  # Import Prefetch secara eksplisit
from django.utils.safestring import mark_safe

register = template.Library()
@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def split_by_equal(value):
    """Split string by '=' and return list."""
    return value.split('=')

@register.filter
def split(value, key):
    return value.split(key)

@register.filter
def split_lines(value):
    return value.strip().splitlines()

@register.filter
def linepartition(value, separator="="):
    """Split string into (before, sep, after) like Python's str.partition()"""
    return value.partition(separator)

@register.filter
def make_iframes_responsive(value):
    """
    Bungkus iframe YouTube/Vimeo saja agar responsive.
    Canva iframe biarkan asli supaya tidak blank.
    """
    if not value:
        return value

    pattern = r'(<iframe[^>]*>.*?</iframe>)'

    def wrap_iframe(match):
        iframe_tag = match.group(1)

        # Cek src iframe
        if 'youtube.com' in iframe_tag or 'youtu.be' in iframe_tag or 'vimeo.com' in iframe_tag:
            # Tambahkan class & atribut
            if 'class=' not in iframe_tag:
                iframe_tag = iframe_tag.replace('<iframe', '<iframe class="absolute inset-0 w-full h-full"')
            if 'allowfullscreen' not in iframe_tag:
                iframe_tag = iframe_tag.replace('<iframe', '<iframe allowfullscreen')
            if 'loading=' not in iframe_tag:
                iframe_tag = iframe_tag.replace('<iframe', '<iframe loading="lazy"')
            # Bungkus div responsive
            return f'<div class="relative w-full overflow-hidden rounded-xl shadow-lg" style="padding-top: 56.25%;">{iframe_tag}</div>'
        else:
            # Canva / embed lain → tampilkan apa adanya
            return iframe_tag

    result = re.sub(pattern, wrap_iframe, value, flags=re.IGNORECASE | re.DOTALL)
    return mark_safe(result)

@register.filter
def shuffled(value):
    result = list(value)
    random.shuffle(result)
    return result

@register.filter
def dict_get(dictionary, key):
    """
    Safely get a value from a dictionary using a key.
    Returns None if the key doesn't exist.
    """
    return dictionary.get(key)

@register.filter
def get_question_answer(dictionary, question_id):
    """
    Get the answer object for a given question ID from the answered_questions dictionary.
    Returns None if no answer exists.
    """
    return dictionary.get(question_id)


@register.filter
def dict_get(dictionary, key):
    return dictionary.get(key)


@register.filter
def dict_get(d, key):
    return d.get(key)


@register.filter
def subtract(value, arg):
    return value - arg

@register.simple_tag
def get_review_progress(submission):
    total_participants = Submission.objects.filter(
        askora__assessment=submission.askora.assessment
    ).values('user').distinct().count()
    
    reviews_received = PeerReview.objects.filter(
        submission=submission
    ).aggregate(
        count=Count('id'),
        reviewers=Count('reviewer', distinct=True)
    )
    
    return {
        'received': reviews_received['count'] or 0,
        'reviewers': reviews_received['reviewers'] or 0,
        'total': total_participants - 1,  # exclude submitter
        'completed': reviews_received['reviewers'] >= (total_participants - 1)
    }


@register.filter
def mul(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''
    
logger = logging.getLogger(__name__)


@register.simple_tag(takes_context=True)
def get_course_completion_status(context):
    request = context['request']
    user = request.user
    course = context.get('course')

    if not course:
        return {
            'is_completed': False,
            'certificate_url': None,
            'assessments_completed_percentage': 0.0,
            'course_progress': 0.0,
            'overall_percentage': 0.0,
            'passing_threshold': 60.0
        }

    # Passing threshold
    grade_ranges = GradeRange.objects.filter(course=course).order_by('max_grade')
    if grade_ranges.exists():
        lowest_range = grade_ranges.first()
        passing_threshold = Decimal(lowest_range.max_grade) + Decimal(1)
    else:
        passing_threshold = Decimal('60')

    # Course progress
    course_progress_obj = CourseProgress.objects.filter(user=user, course=course).first()
    course_progress = Decimal(course_progress_obj.progress_percentage if course_progress_obj else 0).quantize(Decimal("0.01"))

    # Assessments
    assessments = Assessment.objects.filter(section__courses=course).prefetch_related(
        Prefetch('ltiresult_set', queryset=LTIResult.objects.filter(user=user).order_by('-id'), to_attr='prefetched_lti_results'),
        Prefetch('results', queryset=QuizResult.objects.filter(user=user).order_by('-created_at'), to_attr='prefetched_quiz_results'),
        Prefetch('assessmentresult_set', queryset=AssessmentResult.objects.filter(user=user).order_by('-submitted_at'), to_attr='prefetched_assessment_results')
    )

    total_score = Decimal('0')
    total_max_score = Decimal('0')
    assessments_completed = 0

    for a in assessments:
        weight = Decimal(a.weight or 0)
        score_value = Decimal('0')
        submitted = False

        # 1) LTI
        lti = getattr(a, 'prefetched_lti_results', [])
        if lti and lti[0].score is not None:
            lti_score = Decimal(lti[0].score)
            if lti_score > 1:
                lti_score /= 100
            score_value = min(lti_score * weight, weight)
            submitted = True

        else:
            # 2) Quiz
            qr = getattr(a, 'prefetched_quiz_results', [])
            if qr and qr[0].total_questions > 0:
                qr_frac = Decimal(qr[0].score) / Decimal(qr[0].total_questions)
                score_value = min(qr_frac * weight, weight)
                submitted = True
            else:
                # 3) MCQ
                ar = getattr(a, 'prefetched_assessment_results', [])
                if ar and ar[0].total_questions > 0:
                    ar_frac = Decimal(ar[0].correct_answers) / Decimal(ar[0].total_questions)
                    score_value = min(ar_frac * weight, weight)
                    submitted = True
                else:
                    # 4) Askora
                    sub = Submission.objects.filter(askora__assessment=a, user=user).order_by('-submitted_at').first()
                    if sub:
                        sc = AssessmentScore.objects.filter(submission=sub).first()
                        if sc and sc.final_score is not None:
                            score_value = min(Decimal(sc.final_score), weight)
                            submitted = True

        total_score += score_value
        total_max_score += weight
        if submitted:
            assessments_completed += 1

    overall_percentage = (total_score / total_max_score * 100).quantize(Decimal("0.01")) if total_max_score > 0 else Decimal('0')
    assessments_completed_percentage = (Decimal(assessments_completed)/Decimal(len(assessments))*100).quantize(Decimal("0.01")) if assessments else Decimal('0')

    is_completed = overall_percentage >= passing_threshold  # Status Pass/Fail sesuai reference

    certificate_url = reverse('courses:generate_certificate', kwargs={'course_id': course.id}) if is_completed else None

    return {
        'is_completed': bool(is_completed),
        'certificate_url': certificate_url,
        'assessments_completed_percentage': float(assessments_completed_percentage),
        'course_progress': float(course_progress),
        'overall_percentage': float(overall_percentage),
        'passing_threshold': float(passing_threshold)
    }







@register.simple_tag(takes_context=True)
def is_content_read(context, content_type, content_id):
    """
    Cek apakah konten sudah dibaca/selesai oleh user.
    Hanya return True jika ADA bukti nyata di database.
    """
    request = context.get('request')
    if not request or not request.user.is_authenticated:
        
        return False

    user = request.user

    if content_type == 'material':
        exists = MaterialRead.objects.filter(user=user, material_id=content_id).exists()
       
        return exists

    elif content_type == 'assessment':
        # Cek bukti penyelesaian nyata
        lti_exists = LTIResult.objects.filter(user=user, assessment_id=content_id, score__isnull=False).exists()
        qa_exists = QuestionAnswer.objects.filter(user=user, question__assessment_id=content_id).exists()
        sub_exists = Submission.objects.filter(user=user, askora__assessment_id=content_id).exists()
        ar_exists = AssessmentRead.objects.filter(user=user, assessment_id=content_id).exists()

        

        return lti_exists or qa_exists or sub_exists or ar_exists

    
    return False


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)