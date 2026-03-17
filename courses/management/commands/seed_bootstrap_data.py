from datetime import timedelta
from decimal import Decimal
import uuid

from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from django.db.models.signals import post_save
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django.utils.text import slugify

from authentication.models import CustomUser, Universiti
from blog.models import BlogComment, BlogPost, Tag
from courses.models import (
    Assessment,
    BlacklistedKeyword,
    Category,
    Certificate,
    Choice,
    Comment,
    CommentReaction,
    Course,
    CourseComment,
    CoursePrice,
    CourseProgress,
    CourseSessionLog,
    CourseStatus,
    CourseStatusHistory,
    Enrollment,
    GradeRange,
    Hashtag,
    Instructor,
    LastAccessCourse,
    Like,
    Material,
    MaterialRead,
    MicroCredential,
    MicroCredentialEnrollment,
    Partner,
    PricingType,
    Question,
    QuestionAnswer,
    Section,
    SosPost,
    UserActivityLog,
)
from licensing.models import Invitation, License
from notification.models import Notification
from notification.signals import send_real_time_notification
from payments.models import CartItem, Payment, Transaction, Voucher


SEED_PASSWORD = "SeedDemo123!"


class Command(BaseCommand):
    help = "Seed required bootstrap records and sample data for local development."

    @transaction.atomic
    def handle(self, *args, **options):
        now = timezone.now()
        today = now.date()
        self.stdout.write("Seeding bootstrap data...")

        site, _ = Site.objects.update_or_create(
            id=1,
            defaults={"domain": "127.0.0.1:8000", "name": "JakIja Local"},
        )

        admin_user = self.ensure_user(
            email="admin.seed@jakija.local",
            username="seed-admin",
            password=SEED_PASSWORD,
            first_name="System",
            last_name="Admin",
            phone="+15550000001",
            gender="male",
            birth=today - timedelta(days=365 * 35),
            is_superuser=True,
            is_staff=True,
            is_learner=False,
        )
        finance_user = self.ensure_user(
            email="finance.seed@jakija.local",
            username="seed-finance",
            password=SEED_PASSWORD,
            first_name="Finance",
            last_name="Manager",
            phone="+15550000002",
            gender="female",
            birth=today - timedelta(days=365 * 33),
            is_finance=True,
        )
        curation_user = self.ensure_user(
            email="curation.seed@jakija.local",
            username="seed-curation",
            password=SEED_PASSWORD,
            first_name="Content",
            last_name="Curator",
            phone="+15550000003",
            gender="female",
            birth=today - timedelta(days=365 * 31),
            is_curation=True,
        )
        subscription_user = self.ensure_user(
            email="subscription.seed@jakija.local",
            username="seed-subscription",
            password=SEED_PASSWORD,
            first_name="License",
            last_name="Owner",
            phone="+15550000004",
            gender="male",
            birth=today - timedelta(days=365 * 32),
            is_subscription=True,
        )
        partner_user = self.ensure_user(
            email="partner.seed@jakija.local",
            username="seed-partner",
            password=SEED_PASSWORD,
            first_name="Partner",
            last_name="Owner",
            phone="+15550000005",
            gender="male",
            birth=today - timedelta(days=365 * 34),
            is_partner=True,
        )
        instructor_user = self.ensure_user(
            email="instructor.seed@jakija.local",
            username="seed-instructor",
            password=SEED_PASSWORD,
            first_name="Lead",
            last_name="Instructor",
            phone="+15550000006",
            gender="female",
            birth=today - timedelta(days=365 * 29),
            is_instructor=True,
        )
        learner_user = self.ensure_user(
            email="learner.seed@jakija.local",
            username="seed-learner",
            password=SEED_PASSWORD,
            first_name="Sample",
            last_name="Learner",
            phone="+15550000007",
            gender="female",
            birth=today - timedelta(days=365 * 24),
            is_learner=True,
        )

        university, _ = Universiti.objects.get_or_create(
            slug="jakija-demo-university",
            defaults={
                "name": "JakIja Demo University",
                "location": "Kampala",
                "kode": "JDUx",
            },
        )

        for user in (
            finance_user,
            curation_user,
            subscription_user,
            partner_user,
            instructor_user,
            learner_user,
        ):
            if user.university_id != university.id:
                user.university = university
                user.save(update_fields=["university"])

        status_map = {
            status.status: status
            for status in [
                self.ensure_status("draft"),
                self.ensure_status("curation"),
                self.ensure_status("published"),
                self.ensure_status("archived"),
            ]
        }

        pricing_free = self.ensure_pricing_type("Free", "Free enrollment course", code="free")
        pricing_buy_first = self.ensure_pricing_type("Buy First", "Paid before enrollment", code="buy_first")
        pricing_subscription = self.ensure_pricing_type("Subscription", "License or subscription access", code="subscription")

        BlacklistedKeyword.objects.get_or_create(keyword="spamlink")

        category_pharmacy = self.ensure_category(admin_user, "Pharmacy")
        category_compliance = self.ensure_category(admin_user, "Compliance")

        partner, _ = Partner.objects.update_or_create(
            user=partner_user,
            defaults={
                "name": university,
                "phone": "+256700000001",
                "address": "Demo Partner Street, Kampala",
                "description": "Seeded partner organization for LMS bootstrap.",
                "tax": Decimal("18.00"),
                "iceiprice": Decimal("12.50"),
                "author": admin_user,
                "bank_name": "Seed Bank",
                "account_number": "0011223344",
                "account_holder_name": "JakIja Partner",
                "business_type": "institution",
                "payment_method": "bank_transfer",
                "currency": "IDR",
                "is_active": True,
                "is_verified": True,
                "partner_code": "SEED-PARTNER-001",
                "agreed_to_terms": True,
                "status": "approved",
                "verified_at": now,
                "updated_by": admin_user,
            },
        )

        instructor, _ = Instructor.objects.update_or_create(
            user=instructor_user,
            provider=partner,
            defaults={
                "bio": "Seed instructor profile for end-to-end platform testing.",
                "tech": "Django, Pharmacy Education, Assessment Design",
                "expertise": "Clinical pharmacy and compliance training",
                "experience_years": 8,
                "status": "Approved",
                "agreement": True,
            },
        )

        free_course = self.ensure_course(
            slug="seed-pharmacy-orientation",
            name="Pharmacy Orientation Essentials",
            partner=partner,
            instructor=instructor,
            category=category_pharmacy,
            author=admin_user,
            status=status_map["published"],
            payment_model=pricing_free,
            days_open=180,
            language="en",
            level="basic",
            hours="4",
            short_description="Foundational orientation course for new pharmacy learners.",
            description=(
                "A seeded introductory course covering onboarding, platform orientation, "
                "and essential pharmacy learning workflows."
            ),
        )
        paid_course = self.ensure_course(
            slug="seed-gxp-compliance",
            name="GxP Compliance for Pharmacy Teams",
            partner=partner,
            instructor=instructor,
            category=category_compliance,
            author=admin_user,
            status=status_map["published"],
            payment_model=pricing_buy_first,
            days_open=240,
            language="en",
            level="middle",
            hours="8",
            short_description="Paid compliance training with graded assessment.",
            description=(
                "A seeded paid course with assessments, pricing, payment records, and "
                "learner progress for compliance-related LMS testing."
            ),
        )
        draft_course = self.ensure_course(
            slug="seed-draft-pharmacovigilance",
            name="Pharmacovigilance Draft Program",
            partner=partner,
            instructor=instructor,
            category=category_pharmacy,
            author=admin_user,
            status=status_map["draft"],
            payment_model=pricing_subscription,
            days_open=120,
            language="en",
            level="advanced",
            hours="6",
            short_description="Draft course to exercise moderation workflow.",
            description="A seeded draft course for curation and publication workflow testing.",
        )

        self.ensure_status_history(free_course, "published", admin_user, "Seeded published course.")
        self.ensure_status_history(paid_course, "published", admin_user, "Seeded published paid course.")
        self.ensure_status_history(draft_course, "draft", admin_user, "Seeded draft course.")

        free_pass_grade, _ = GradeRange.objects.get_or_create(
            course=free_course,
            name="Pass",
            defaults={"min_grade": Decimal("60.00"), "max_grade": Decimal("100.00")},
        )
        GradeRange.objects.get_or_create(
            course=free_course,
            name="Fail",
            defaults={"min_grade": Decimal("0.00"), "max_grade": Decimal("59.99")},
        )
        paid_pass_grade, _ = GradeRange.objects.get_or_create(
            course=paid_course,
            name="Pass",
            defaults={"min_grade": Decimal("60.00"), "max_grade": Decimal("100.00")},
        )
        GradeRange.objects.get_or_create(
            course=paid_course,
            name="Fail",
            defaults={"min_grade": Decimal("0.00"), "max_grade": Decimal("59.99")},
        )

        free_assessment = self.ensure_course_structure(
            course=free_course,
            author=admin_user,
            grade_range=free_pass_grade,
        )
        paid_assessment = self.ensure_course_structure(
            course=paid_course,
            author=admin_user,
            grade_range=paid_pass_grade,
        )
        self.ensure_course_structure(
            course=draft_course,
            author=admin_user,
            grade_range=None,
        )

        CoursePrice.objects.update_or_create(
            course=free_course,
            price_type=pricing_free,
            partner=partner,
            defaults={
                "partner_price": Decimal("0.00"),
                "discount_percent": Decimal("0.00"),
            },
        )
        paid_price, _ = CoursePrice.objects.update_or_create(
            course=paid_course,
            price_type=pricing_buy_first,
            partner=partner,
            defaults={
                "partner_price": Decimal("150000.00"),
                "discount_percent": Decimal("10.00"),
            },
        )
        CoursePrice.objects.update_or_create(
            course=draft_course,
            price_type=pricing_subscription,
            partner=partner,
            defaults={
                "partner_price": Decimal("250000.00"),
                "discount_percent": Decimal("0.00"),
            },
        )

        transaction_obj, _ = Transaction.objects.update_or_create(
            merchant_ref="SEED-MERCHANT-001",
            defaults={
                "user": learner_user,
                "total_amount": paid_price.portal_price,
                "status": "completed",
                "description": "Seeded transaction for paid course enrollment",
                "platform_fee": paid_price.admin_fee,
                "voucher": paid_price.discount_amount,
                "transaction_id": "SEED-TX-001",
                "payment_method": "bank_transfer",
                "payment_url": "https://example.com/payments/seed-tx-001",
                "va_number": "1234567890",
                "bank_name": "Seed Bank",
                "expired_at": now + timedelta(hours=1),
            },
        )
        transaction_obj.courses.set([paid_course])

        payment_obj, _ = Payment.objects.update_or_create(
            transaction_id="SEED-PAY-001",
            defaults={
                "user": learner_user,
                "course": paid_course,
                "payment_model": "buy_first",
                "amount": paid_price.portal_price,
                "payment_date": now,
                "status": "completed",
                "payment_method": "bank_transfer",
                "payment_url": "https://example.com/payments/seed-pay-001",
                "access_granted": True,
                "access_granted_date": now,
                "snapshot_price": paid_price.normal_price,
                "snapshot_discount": paid_price.discount_amount,
                "snapshot_tax": Decimal("0.00"),
                "snapshot_ppn": paid_price.ppn,
                "snapshot_user_payment": paid_price.portal_price,
                "snapshot_partner_earning": paid_price.partner_price - paid_price.discount_amount,
                "snapshot_ice_earning": paid_price.admin_fee,
                "snapshot_platform_fee": paid_price.admin_fee,
                "snapshot_voucher": paid_price.discount_amount,
                "course_price": {
                    "portal_price": str(paid_price.portal_price),
                    "normal_price": str(paid_price.normal_price),
                    "discount_amount": str(paid_price.discount_amount),
                },
                "linked_transaction": transaction_obj,
            },
        )

        Enrollment.objects.get_or_create(user=learner_user, course=free_course)
        Enrollment.objects.update_or_create(
            user=learner_user,
            course=paid_course,
            defaults={"payment": payment_obj, "certificate_issued": True},
        )
        CartItem.objects.get_or_create(user=learner_user, course=draft_course)

        CourseProgress.objects.update_or_create(
            user=learner_user,
            course=free_course,
            defaults={"progress": 75, "progress_percentage": 75, "grade": free_pass_grade},
        )
        CourseProgress.objects.update_or_create(
            user=learner_user,
            course=paid_course,
            defaults={"progress": 100, "progress_percentage": 100, "grade": paid_pass_grade},
        )

        for material in free_course.sections.first().materials.all()[:1]:
            MaterialRead.objects.get_or_create(user=learner_user, material=material)
            LastAccessCourse.objects.update_or_create(
                user=learner_user,
                course=free_course,
                defaults={"material": material, "assessment": free_assessment},
            )

        QuestionAnswer.objects.get_or_create(
            user=learner_user,
            question=paid_assessment.questions.first(),
            defaults={"choice": paid_assessment.questions.first().choices.filter(is_correct=True).first()},
        )

        CourseSessionLog.objects.update_or_create(
            user=learner_user,
            course=paid_course,
            started_at=now - timedelta(minutes=45),
            defaults={
                "ended_at": now - timedelta(minutes=5),
                "user_agent": "Seed Browser",
                "ip_address": "127.0.0.1",
                "location_country": "Uganda",
                "location_city": "Kampala",
            },
        )

        Certificate.objects.get_or_create(
            user=learner_user,
            course=paid_course,
            defaults={
                "certificate_id": uuid.uuid4(),
                "issue_date": today,
                "total_score": Decimal("92.50"),
                "partner": partner,
                "verifiable_credential": {"issuer": site.domain, "status": "valid"},
            },
        )

        free_rating, _ = free_course.ratings.get_or_create(
            user=learner_user,
            defaults={"rating": 5, "comment": "Useful onboarding course with a clear structure."},
        )
        paid_course.ratings.get_or_create(
            user=learner_user,
            defaults={"rating": 4, "comment": "Strong compliance content with practical examples."},
        )

        course_comment, _ = CourseComment.objects.get_or_create(
            user=learner_user,
            course=paid_course,
            content="This seeded course comment is available for moderation testing.",
        )
        material_comment, _ = Comment.objects.get_or_create(
            user=learner_user,
            material=free_course.sections.first().materials.first(),
            content="Sample learner comment on a lesson material.",
        )
        CommentReaction.objects.get_or_create(
            user=instructor_user,
            comment=material_comment,
            defaults={"reaction_type": CommentReaction.REACTION_LIKE},
        )

        seeded_post, _ = SosPost.objects.get_or_create(
            user=learner_user,
            content="Working through the seeded LMS demo today. #jakija #pharmacy",
        )
        hashtag, _ = Hashtag.objects.get_or_create(name="jakija")
        hashtag.posts.add(seeded_post)
        Like.objects.get_or_create(user=instructor_user, post=seeded_post)

        microcredential, _ = MicroCredential.objects.update_or_create(
            slug="seed-pharmacy-track",
            defaults={
                "title": "Pharmacy Foundations Track",
                "description": "Seeded microcredential tying together the sample courses.",
                "status": "active",
                "start_date": today,
                "end_date": today + timedelta(days=365),
                "category": category_pharmacy,
                "min_total_score": 120.0,
                "author": admin_user,
            },
        )
        microcredential.required_courses.set([free_course, paid_course])
        MicroCredentialEnrollment.objects.get_or_create(user=learner_user, microcredential=microcredential)

        voucher, _ = Voucher.objects.update_or_create(
            code="SEED10",
            defaults={
                "amount": Decimal("10000.00"),
                "is_active": True,
                "start_date": today - timedelta(days=1),
                "end_date": today + timedelta(days=180),
                "usage_limit": 100,
                "used_count": 1,
                "one_time_per_user": False,
            },
        )

        license_obj, _ = License.objects.update_or_create(
            name="Seeded Annual Enterprise License",
            defaults={
                "license_type": "paid",
                "start_date": today,
                "expiry_date": today + timedelta(days=365),
                "status": True,
                "description": "Seeded license for subscription and invitation flows.",
                "university": university,
                "max_users": 25,
                "subscription_type": "paid",
                "subscription_frequency": "yearly",
                "owner": subscription_user,
            },
        )
        license_obj.users.add(subscription_user, learner_user)
        Invitation.objects.update_or_create(
            invitee_email="licensed.seed@jakija.local",
            license=license_obj,
            defaults={
                "inviter": subscription_user,
                "status": "pending",
                "expiry_date": now + timedelta(days=7),
                "token": "seed-license-invite-token",
            },
        )

        post_save.disconnect(send_real_time_notification, sender=Notification)
        try:
            Notification.objects.update_or_create(
                user=learner_user,
                notif_type="certificate_issued",
                title="Certificate ready",
                defaults={
                    "actor": instructor_user,
                    "priority": "high",
                    "message": "Your seeded course certificate is available for verification.",
                    "link": f"/verify/{Certificate.objects.filter(user=learner_user, course=paid_course).first().certificate_id}/",
                    "content_type": ContentType.objects.get_for_model(Course),
                    "object_id": paid_course.id,
                },
            )
            Notification.objects.update_or_create(
                user=learner_user,
                notif_type="enrollment_success",
                title="Enrollment successful",
                defaults={
                    "actor": admin_user,
                    "priority": "medium",
                    "message": "You have been enrolled into the seeded orientation course.",
                    "link": f"/course-detail/{free_course.id}/{free_course.slug}/",
                    "content_type": ContentType.objects.get_for_model(Course),
                    "object_id": free_course.id,
                },
            )
        finally:
            post_save.connect(send_real_time_notification, sender=Notification)

        pharmacy_tag, _ = Tag.objects.get_or_create(name="Pharmacy", slug="pharmacy")
        blog_post, _ = BlogPost.objects.update_or_create(
            slug="seed-platform-announcement",
            defaults={
                "title": "Seeded Platform Announcement",
                "content": "This is a seeded published blog post for content and analytics testing.",
                "author": admin_user,
                "category": category_pharmacy,
                "status": "published",
            },
        )
        blog_post.tags.add(pharmacy_tag)
        blog_post.related_courses.add(free_course, paid_course)
        BlogComment.objects.get_or_create(
            blogpost_connected=blog_post,
            author=learner_user,
            content="Seeded blog comment for moderation and analytics checks.",
        )

        for actor, activity_type in (
            (admin_user, "seed_setup"),
            (learner_user, "login_view"),
            (learner_user, "view_course"),
            (partner_user, "partner_dashboard"),
        ):
            UserActivityLog.objects.get_or_create(
                user=actor,
                activity_type=activity_type,
                defaults={
                    "ip_address": "127.0.0.1",
                    "location": "Kampala, Uganda",
                    "user_agent": "Seed Script",
                },
            )

        self.stdout.write(self.style.SUCCESS("Bootstrap data seeded successfully."))
        self.stdout.write("")
        self.stdout.write("Seeded accounts")
        self.stdout.write(f"  admin.seed@jakija.local / {SEED_PASSWORD}")
        self.stdout.write(f"  partner.seed@jakija.local / {SEED_PASSWORD}")
        self.stdout.write(f"  instructor.seed@jakija.local / {SEED_PASSWORD}")
        self.stdout.write(f"  learner.seed@jakija.local / {SEED_PASSWORD}")
        self.stdout.write(f"  finance.seed@jakija.local / {SEED_PASSWORD}")
        self.stdout.write(f"  curation.seed@jakija.local / {SEED_PASSWORD}")
        self.stdout.write(f"  subscription.seed@jakija.local / {SEED_PASSWORD}")

    def ensure_user(self, **kwargs):
        email = kwargs.pop("email")
        username = kwargs.pop("username")
        password = kwargs.pop("password")
        role_fields = {
            "is_superuser": kwargs.pop("is_superuser", False),
            "is_staff": kwargs.pop("is_staff", False),
            "is_partner": kwargs.pop("is_partner", False),
            "is_instructor": kwargs.pop("is_instructor", False),
            "is_curation": kwargs.pop("is_curation", False),
            "is_finance": kwargs.pop("is_finance", False),
            "is_subscription": kwargs.pop("is_subscription", False),
            "is_learner": kwargs.pop("is_learner", True),
        }
        user, _ = CustomUser.objects.get_or_create(
            email=email,
            defaults={"username": username, "is_active": True, **kwargs, **role_fields},
        )
        updated_fields = []
        if user.username != username:
            user.username = username
            updated_fields.append("username")
        for key, value in {**kwargs, **role_fields}.items():
            if getattr(user, key) != value:
                setattr(user, key, value)
                updated_fields.append(key)
        if not user.is_active:
            user.is_active = True
            updated_fields.append("is_active")
        user.set_password(password)
        user.save()
        return user

    def ensure_status(self, value):
        status, _ = CourseStatus.objects.get_or_create(
            status=value,
            defaults={"manual_message": ""},
        )
        if status.manual_message is None:
            status.manual_message = ""
            status.save(update_fields=["manual_message"])
        return status

    def ensure_pricing_type(self, name, description, code=None):
        code = code or slugify(name)
        pricing_type = PricingType.objects.filter(Q(name=name) | Q(code=code)).first()
        if pricing_type:
            changed = False
            if pricing_type.name != name:
                pricing_type.name = name
                changed = True
            if pricing_type.code != code:
                pricing_type.code = code
                changed = True
            if pricing_type.description != description:
                pricing_type.description = description
                changed = True
            if changed:
                pricing_type.save()
            return pricing_type
        return PricingType.objects.create(code=code, name=name, description=description)

    def ensure_category(self, user, name):
        return Category.objects.update_or_create(
            slug=slugify(name),
            defaults={"user": user, "name": name},
        )[0]

    def ensure_course(
        self,
        slug,
        name,
        partner,
        instructor,
        category,
        author,
        status,
        payment_model,
        days_open,
        language,
        level,
        hours,
        short_description,
        description,
    ):
        today = timezone.now().date()
        course, _ = Course.objects.update_or_create(
            slug=slug,
            defaults={
                "course_name": name,
                "course_number": slug.upper()[:12],
                "course_run": "2026A",
                "org_partner": partner,
                "instructor": instructor,
                "category": category,
                "level": level,
                "status_course": status,
                "description": description,
                "sort_description": short_description,
                "hour": hours,
                "author": author,
                "language": language,
                "start_date": today,
                "end_date": today + timedelta(days=days_open),
                "start_enrol": today - timedelta(days=7),
                "end_enrol": today + timedelta(days=days_open),
                "payment_model": payment_model,
            },
        )
        return course

    def ensure_status_history(self, course, status, changed_by, message):
        CourseStatusHistory.objects.get_or_create(
            course=course,
            status=status,
            manual_message=message,
            changed_by=changed_by,
        )

    def ensure_course_structure(self, course, author, grade_range):
        intro_section, _ = Section.objects.get_or_create(
            courses=course,
            parent=None,
            title="Introduction",
            defaults={"order": 1},
        )
        lesson_section, _ = Section.objects.get_or_create(
            courses=course,
            parent=None,
            title="Core Lesson",
            defaults={"order": 2},
        )
        Material.objects.get_or_create(
            section=intro_section,
            title=f"{course.course_name} Overview",
            defaults={"description": "Seeded overview material for learner navigation and comments."},
        )
        Material.objects.get_or_create(
            section=lesson_section,
            title=f"{course.course_name} Lesson 1",
            defaults={"description": "Seeded lesson content for progress, reads, and comment testing."},
        )
        assessment, _ = Assessment.objects.get_or_create(
            section=lesson_section,
            name=f"{course.course_name} Quiz",
            defaults={
                "weight": Decimal("100.00"),
                "description": "Seeded assessment for score and progress testing.",
                "duration_in_minutes": 15,
                "grade_range": grade_range,
            },
        )
        if assessment.questions.count() == 0:
            for index in range(1, 4):
                question = Question.objects.create(
                    assessment=assessment,
                    text=f"Seeded question {index} for {course.course_name}",
                    explanation="This is a seeded assessment explanation.",
                )
                for option in range(1, 5):
                    Choice.objects.create(
                        question=question,
                        text=f"Option {option}",
                        is_correct=option == 1,
                    )
        return assessment
