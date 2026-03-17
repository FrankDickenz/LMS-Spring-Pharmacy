# System Flow Documentation

## Overview

This project is a Django LMS platform with all major app routes mounted at the root URL namespace. It combines:

- Public marketing and discovery pages
- Authentication and profile management
- Role-based dashboards
- Course authoring and publishing workflows
- Learner course consumption and assessment flows
- Payments and finance reporting
- Licensing and subscription management
- Partner analytics
- Blog CMS and content moderation
- LTI integration

The root URL configuration is defined in `mysite/urls.py`. The main product dashboard is custom and lives at `/dasbord/`. Django admin is mounted at `/kuruk/`.

## URL Mounting

All of these apps are included at the root:

- `authentication`
- `courses`
- `notification`
- `partner`
- `instructor`
- `learner`
- `blog`
- `licensing`
- `payments`
- `lti_consumer`

Additional third-party integrations:

- `/kuruk/` Django admin
- `/accounts/` allauth
- `/captcha/`
- `/select2/`
- `/ckeditor5/`

## Role Model

The custom user model is `authentication.CustomUser`. It uses Django auth plus custom role flags.

Important role fields:

- `is_superuser`
- `is_staff`
- `is_partner`
- `is_instructor`
- `is_curation`
- `is_finance`
- `is_subscription`
- `is_learner`

### Effective Access Semantics

- `superuser`: global platform access, course publishing, admin reporting, finance visibility
- `staff`: extra trusted access in selected areas, but not equivalent to superuser
- `partner`: organization-scoped course, learner, analytics, and moderation access
- `instructor`: instructor-scoped course authoring and reporting access
- `curation`: content moderation and review alongside superuser in several course flows
- `finance`: finance dashboard and exports
- `subscription`: license and participant management
- `learner`: default learning role

## End-to-End Product Flow

### 1. Public Entry and Discovery

Visitors land on the public home page:

- `/`

This page assembles:

- Popular categories
- Active microcredentials
- Approved instructors
- Active partners
- Latest published blog articles
- Platform summary counts

Supporting public pages:

- `/about/`
- `/faq/`
- `/contact/`
- `/terms/`
- `/privacy/`
- `/instructor-agreement/`
- `/partnership-agreement/`
- `/cookie-policy/`
- `/refund-policy/`
- `/security/`
- `/partner-info/`

Search:

- `/search/`

Search looks across:

- Courses
- Instructors
- Partners
- Blog posts

Notes:

- Search uses referer validation against `settings.ALLOWED_REFERER`
- Authenticated users get persistent search history
- Anonymous users get cached session-based search history

### 2. Authentication and Account Activation

Authentication endpoints:

- `/login/`
- `/logout/`
- `/register/`
- `/activate/<uidb64>/<token>/`

Password reset flow:

- `/password_reset/`
- `/password_reset/done/`
- `/reset/<uidb64>/<token>/`
- `/reset/done/`

Behavior:

- Login authenticates using email as the username field
- Registration creates an inactive account
- Activation is completed via email token
- Login redirects to `next` if provided, otherwise to home, not automatically to `/dasbord/`

### 3. Profile Completion Gate

Several protected flows enforce required profile fields before allowing full access.

Typical required fields:

- First name
- Last name
- Email
- Phone
- Gender
- Birth date

Profile endpoints:

- `/profile/<username>/`
- `/edit-profile/<pk>/`
- `/edit-photo/<pk>/`

This matters because an authenticated user may still be redirected to profile edit before reaching:

- `/dasbord/`
- `/mycourse/`

### 4. Role-Based Dashboard Entry

Main dashboard:

- `/dasbord/`

Role branching:

- `superuser` and `is_curation`: global counts and global course visibility
- `is_partner`: partner-owned courses and learners only
- `is_instructor`: instructor-owned courses and learners only

Dashboard output includes:

- Total enrollments
- Total courses
- Total instructors
- Total learners
- Total partners
- Total published courses
- Total certificates
- Recently created courses
- Online and offline user counts for privileged roles

### 5. User Administration and Learner Roster

User list and detail:

- `/all-user/`
- `/user-detail/<user_id>/id`

Access behavior:

- Superuser can see all users
- Partner can see users in the same university/org scope
- Other roles are denied or receive empty results

User detail includes enrollment and progress-derived course status.

### 6. Course Discovery and Catalog

Catalog and public browsing endpoints:

- `/courses/`
- `/course/tim/`
- `/category/<slug>/`
- `/course-detail/<id>/<slug>/`
- `/org-partner/<slug>/`
- `/partner-all/`
- `/instructor-all/`
- `/instructor/<id>/`
- `/instructor-profile/<username>/`

These pages expose:

- Course metadata
- Instructor and partner identity
- Ratings and review counts
- Enrollment counts
- Pricing
- Category filtering
- Language filtering
- Level filtering

### 7. Enrollment and Commercial Entry Points

Direct enrollment routes:

- `/course/<course_id>/enroll/`
- `/enroll/<course_id>/`

Learner-owned course views:

- `/mycourse/`
- `/course_list/`

Course enrollment roster management:

- `/course-list-enroll/<id>/`
- `/unenroll/<course_id>/<user_id>/`

### 8. Payments and Checkout

Cart and checkout:

- `/add-to-cart/<course_id>/course`
- `/cart/`
- `/cart/delete/<pk>/`
- `/checkout/`

Payment processing:

- `/course/<course_id>/payment/<payment_type>/`

Payment callback and return:

- `/payments/tripay-callback/`
- `/payments/return/`

Transaction and receipt views:

- `/transactions/`
- `/transaction/<pk>/user`
- `/transactions/<pk>/invoice/detail`
- `/transaction/<merchant_ref>/`
- `/invoices/`

Reporting:

- `/transactions/process_payment/`
- `/report/<pk>/detail`
- `/reports/per-course/`
- `/reports/per-course/<course_id>/`

Finance area:

- `/dashboard/finance`
- `/commissions/`
- `/export/`
- `/finance/export/`
- `/export-csv/`

Access:

- Finance dashboard and export endpoints are guarded for `superuser` or `is_finance`

Payment flow summary:

1. User adds a course to cart or goes to payment directly
2. User checks out
3. Payment is created and sent to Tripay
4. Tripay callback updates transaction state
5. User can return to the app and view transaction history, receipts, and reports

### 9. Learner Course Consumption

Core learner workspace routes:

- `/learner/<username>/`
- `/<username>/<id>/<slug>/`
- `/<username>/<id>/<slug>/<content_type>/<content_id>/`
- `/course-learn/<username>/<slug>/`
- `/self_course/<username>/<id>/<slug>/`

Progress and activity:

- `/<username>/<slug>/progress/`
- `/mark-progress/`
- `/my-activity/`
- `/analytics/users/`
- `/learner/<username>/<course_id>/score-summary/`
- `/course/<course_id>/scores/detail/`
- `/grade-distribution/<course_id>/`

Learner interactions:

- `/add-comment/`
- `/toggle-reaction/<comment_id>/<reaction_type>/`
- `/invite-learner/<course_id>/`
- `/<username>/<course_id>/section/<section_id>/report/`

### 10. Assessments, ORA, and Rich Learning Content

Learner assessment execution:

- `/start-assessment/<assessment_id>/courses`
- `/submit-assessment/<assessment_id>/new`
- `/submit-answer/`
- `/submit-answer-askora/<ask_ora_id>/new`
- `/submit-peer-review/<submission_id>/ora`
- `/video/<video_id>/save-result/<assessment_id>/`

Course app equivalents also exist:

- `/start-assessment/<assessment_id>/`
- `/submit_assessment/<assessment_id>/`
- `/submit-answer/<askora_id>/`
- `/submit-peer-review/<submission_id>/`

Advanced authoring endpoints:

- Askora creation and maintenance under:
  - `/course/<idcourse>/section/<idsection>/assessment/<idassessment>/create/`
  - `/edit-askora/...`
  - `/delete-askora/...`
- In-video quiz:
  - `/course/<idcourse>/section/<idsection>/assessment/<idassessment>/ivq/`
  - edit, delete, and question CRUD variants
- LTI 1.1-style tooling:
  - create, edit, delete, and launch under `/course/<idcourse>/section/<idsection>/lti/...`

### 11. Course Authoring and Internal Content Operations

Course creation and metadata:

- `/course-add/`
- `/course-profile/<id>/`
- `/draft-lms/<id>/`
- `/studio/<id>`
- `/studios/<id>/`

Section and material management:

- `/create-section/<idcourse>/`
- `/add-matrial/<idcourse>/<idsection>/`
- `/edit-matrial/<idcourse>/<idmaterial>`
- `/delete-matrial/<pk>`
- `/delete-section/<pk>/`
- `/update-section/<pk>/`
- `/reorder-section/`

Assessment management:

- `/create-assessment/<idcourse>/<idsection>/`
- `/edit-assessment/<idcourse>/<idsection>/<idassessment>/`
- `/delete-assessment/<idcourse>/<idsection>/<idassessment>/`

Question management:

- `/questions/create/<idcourse>/<idsection>/<idassessment>/`
- `/questions/edit/<idcourse>/<idquestion>/<idsection>/<idassessment>`
- `/questions/delete/<idcourse>/<idquestion>/<idsection>/<idassessment>`
- `/questions/view/<idcourse>/<idsection>/<idassessment>/`

Course structure support:

- `/course-team/<course_id>/`
- `/course/<course_id>/team/remove/<member_id>/`
- `/team-member/remove/<member_id>/`
- `/course-instructor/<id>/`
- `/add-price/<id>/`
- `/course/<course_id>/timeline/`

Autocomplete and supporting endpoints:

- `/user-autocomplete/`
- `/universiti-autocomplete/`
- `/partner-autocomplete/`
- `/instructor-autocomplete/`
- `/course-autocomplete/`

Rich editor image operations:

- `/upload-image/`
- `/ckeditor/delete-image/`

### 12. Course Governance and Publishing Workflow

This project uses a staged publishing workflow.

Instructor stage:

- `/instructor/course/<course_id>/submit-curation/`

Partner review stage:

- `/partner/course/<course_id>/review-curation/`

Final superuser publish stage:

- `/superuser/course/<course_id>/publish/`

Supporting moderation and reports:

- `/report/<report_id>/review/`
- `/report/<report_id>/resolve/`
- `/course/<course_id>/reports/`

The general effective flow is:

1. Instructor authors course
2. Instructor submits course for curation
3. Partner reviews and forwards or rejects
4. Superuser publishes or rejects
5. Published course appears in public catalog

### 13. Certificates

Course certificates:

- `/certificate/<course_id>/`
- `/verify/<uuid:certificate_id>/`

Instructor certificate operations:

- `/instructor/generate-certificates/`
- `/certificate/verify/<uuid:cert_id>/`

### 14. Microcredentials

Catalog and CRUD:

- `/microcredentials/`
- `/microcredentials/create/`
- `/microcredentials/<pk>/`
- `/microcredentials/<pk>/edit/`
- `/microcredentials/<pk>/delete/`

Public and learner flows:

- `/microcredential/<slug>/`
- `/microcredential/<slug>/enroll/`
- `/microcredential/<id>/<slug>/detail/`
- `/microcredential/<id>/certificate/`

Engagement and reporting:

- `/microcredential/<microcredential_id>/add-review/`
- `/microcredential/<microcredential_id>/<slug>/add_comment/`
- `/microcredential/<microcredential_id>/report/`
- `/microcredential/report/pdf/<microcredential_id>/`
- `/verify-micro/<uuid:certificate_id>/`

### 15. Comments, Social Layer, and Moderation

Comment moderation dashboard:

- `/message_comment/`
- `/reply-comment/<comment_id>/`
- `/comment/<comment_id>/delete/`

Course comment routes:

- `/add-comment/<material_id>/`
- `/add-comment-course/<course_id>/`
- `/comment/<comment_id>/reply/`

Partner moderation:

- `/course-detail/<course_id>/comment/reply/<comment_id>/`
- `/course-comments/`
- `/partner/comments/delete/<comment_id>/`

Social feed:

- `/sosial/`
- `/sosial/create/`
- `/sosial/like/<post_id>/`
- `/sosial/reply/<post_id>/`
- `/sosial/reply-form/<post_id>/`
- `/sosial/hashtag/<hashtag>/`
- `/sosial/load-more/`
- `/sosial/search/`

### 16. Notifications

Notification endpoints:

- `/notif`
- `/read/<notif_id>/`

These support listing and marking notifications as read.

### 17. Partner Operations and Analytics

Partner management and discovery:

- `/org-partner/`
- `/partner/update/<partner_id>/<universiti_slug>/`
- `/request-partner/`
- `/verify-partner/`
- `/verify-partner/<pk>/`

Partner learner and course reporting:

- `/partner/enrollments/`
- `/enrollments/export/`
- `/reports/course-ratings/`
- `/explore/`

Partner analytics suite:

- `/analytics/`
- `/analytics/heatmap/`
- `/analytics/login-trends/`
- `/analytics/duration/`
- `/analytics/geography/`
- `/analytics/device-usage/`
- `/analytics/popular-courses/`
- `/analytics/user-growth/`
- `/analytics/course-completion/`
- `/analytics/retention/`
- `/analytics/top-courses-rating/`
- `/analytics/enrollment-growth/`
- `/analytics/course-dropoff/`
- `/analytics/certificates/`
- `/analytics/active-partners/`
- `/transaction-trends/`
- `/analytics/top-transaction-partners/`
- `/top-courses-revenue/`
- `/analytics/partner/all/`
- `/ping-session/`

These routes indicate the system tracks:

- Enrollment growth
- Ratings
- Completion
- Retention
- Device usage
- Geography
- Revenue
- Transaction patterns

### 18. Licensing and Subscription Flow

Main licensing endpoints:

- `/dashboard/`
- `/learners/`
- `/license/analytics/`
- `/participant/dashboard/`
- `/course-participants-dashboard/`
- `/course-detail/<course_id>/`
- `/create/`
- `/update/license/<pk>/`
- `/manage/`

Invitation lifecycle:

- `/invitation/send/`
- `/invitation/cancel/<invitation_id>/`
- `/invitation/resend/<invitation_id>/`
- `/invitation/accept/<uidb64>/<token>/`
- `/invitation/delete/<invitation_id>/`

Access rule:

- Licensing dashboards require `request.user.is_subscription`

License flow:

1. Subscription user creates or manages a license
2. Invitations are sent to participants
3. Invitee accepts through tokenized invitation URL
4. Participant activity and course enrollment are tracked under the license
5. Subscription dashboards show enrollment, pass rate, course usage, and expiry warnings

### 19. Blog CMS and Content Operations

Public blog:

- `/blog/`
- `/post/<slug>/`
- `/blog/category/<slug>/`
- `/tag/<slug>/`

Blog administration:

- `/admin/posts/all`
- `/admin/post/create/`
- `/admin/post/<pk>/update/`
- `/admin/post/<pk>/delete/`
- `/admin/post/<post_id>/comments/`
- `/admin/comment/<comment_id>/reply/`
- `/admin/comment/<comment_id>/delete/`
- `/blog/admin/analytics/`
- `/mark-read/`

Important note:

- These `/admin/...` routes are custom blog CMS routes
- Django admin remains `/kuruk/`

### 20. LTI Integration

Dedicated LTI consumer endpoints:

- `/lti13/launch/<link_id>/`
- `/lti13/launch/response/`
- `/lti13/.well-known/jwks.json`

Learner-side LTI course endpoints:

- `/lti/launch/<assessment_id>/`
- `/lti/grade-callback/`

The project therefore supports:

- LTI launch flow
- JWKS exposure for key distribution
- Grade callback handling
- Embedded LTI course tool launch from authored course content

### 21. REST API Surface from DRF Router

The `courses` app registers viewsets with `DefaultRouter` for:

- `sections`
- `materials`
- `assessments`

This produces standard REST-style endpoints such as:

- `/sections/`
- `/sections/<pk>/`
- `/materials/`
- `/materials/<pk>/`
- `/assessments/`
- `/assessments/<pk>/`

Exact allowed methods depend on the viewset implementation.

## Operational Notes and Caveats

### Root-Level URL Namespace

Every app is included at root. That keeps URLs short, but it also means route naming discipline matters. This project already mixes:

- Public routes
- Custom admin-like routes
- Django admin

### Admin Surfaces

There are multiple admin surfaces:

- `/kuruk/` for Django admin
- `/dasbord/` for the custom platform dashboard
- `/admin/...` for blog CMS routes

These are separate systems.

### Existing Superuser

The local database contains a superuser record. Access still depends on knowing or resetting the password.

### Common Protected Flow Pattern

The project often enforces this sequence:

1. User authenticates
2. Role is checked
3. Profile completeness is checked
4. Object ownership or organization scope is checked
5. The view renders or redirects

### Payment and Callback Safety

Tripay webhook processing validates:

- HTTP method
- Signature header
- HMAC digest
- JSON body structure
- Merchant reference lookup

### Search Restrictions

The `/search/` endpoint can reject requests if the referer is not accepted by the app configuration.

## Quick Reference by User Type

### Anonymous User

- Visit `/`
- Browse `/courses/`
- Open `/course-detail/<id>/<slug>/`
- Read `/blog/`
- Register via `/register/`

### Learner

- Login via `/login/`
- Visit `/mycourse/`
- Open learning page `/<username>/<id>/<slug>/`
- Submit assessments
- Track progress and scores
- Generate certificates when eligible

### Instructor

- Become instructor via `/instructor-add/`
- Build courses via `/course-add/`, `/studio/<id>`
- Manage sections, materials, assessments, ORA, IVQ, and LTI
- Submit for curation via `/instructor/course/<course_id>/submit-curation/`

### Partner

- Manage partner data and instructors
- Review curation
- Access analytics and enrollment reporting
- Moderate comments and inspect learner performance

### Superuser / Curation

- Access `/dasbord/`
- Use `/kuruk/`
- Publish or reject courses
- View all users and global platform reporting
- Access finance and partner verification flows

### Finance

- Access `/dashboard/finance`
- Export financial data
- Review course and transaction revenue reports

### Subscription Manager

- Access `/dashboard/`
- Create and manage licenses
- Invite participants
- Monitor participants and enrollment metrics

## Source of Truth

This document is derived from the current codebase URL maps and key access-control logic in:

- `mysite/urls.py`
- `authentication/urls.py`
- `courses/urls.py`
- `learner/urls.py`
- `partner/urls.py`
- `instructor/urls.py`
- `payments/urls.py`
- `licensing/urls.py`
- `blog/urls.py`
- `notification/urls.py`
- `lti_consumer/urls.py`
- `authentication/views.py`
- `authentication/models.py`
- `payments/views.py`
- `licensing/views.py`

