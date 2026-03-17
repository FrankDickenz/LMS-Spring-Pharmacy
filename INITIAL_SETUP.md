# Initial Setup Guide

## Purpose

This document explains the exact order to bring the LMS up from a fresh environment and the minimum records that must exist before the system behaves correctly.

It is based on the current codebase and covers:

- infrastructure prerequisites
- first-run Django setup
- required settings
- required seed records
- role and entity creation order
- minimal working bootstrap path
- optional subsystem setup

## What Must Exist Before the App Works

At a minimum, the system expects all of these to be true:

- Python dependencies are installed
- Redis is running
- database migrations have been applied
- at least one superuser exists
- `CourseStatus` rows exist for:
  - `draft`
  - `curation`
  - `published`
  - `archived`
- at least one `PricingType` exists
- at least one `Universiti` exists
- at least one `Category` exists
- at least one partner user and `Partner` record exist
- at least one instructor user and `Instructor` record exist
- at least one course exists with content underneath it

Without these, major parts of the LMS will either be empty or fail logically.

## Step 1. Prepare the Environment

Create and activate a virtual environment, then install dependencies.

Example:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Step 2. Start Required Services

### Redis

Redis is required by the current settings for:

- Django cache
- Django Channels
- Celery broker
- Celery result backend

The code expects Redis on:

- `127.0.0.1:6379`

That configuration is in:

- `mysite/settings.py`

If Redis is not running, cache, notifications, and task-related features may break.

## Step 3. Verify Core Django Settings

Before first real use, review these values in `mysite/settings.py`.

### Local development values

- `ALLOWED_HOSTS`
- `ALLOWED_REFERER`

The search flow depends on `ALLOWED_REFERER`, so if this is wrong, `/search/` can reject valid requests.

### Required email settings

- `EMAIL_HOST`
- `EMAIL_PORT`
- `EMAIL_USE_TLS`
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`
- `DEFAULT_FROM_EMAIL`

Email is used for:

- account activation
- password reset
- invitation flows
- some notification flows

### Optional integration settings

Only configure these if you need the related subsystem:

- allauth social login credentials
- Tripay keys
- LTI issuer and client ID

## Step 4. Initialize the Database

Apply migrations first.

```bash
python manage.py migrate
```

Then create a superuser.

```bash
python manage.py createsuperuser
```

Notes:

- the project uses `authentication.CustomUser`
- login is email-based
- Django admin is mounted at `/kuruk/`

## Step 5. Start the App Once

Run:

```bash
python manage.py runserver
```

Then verify:

- home page loads at `/`
- Django admin loads at `/kuruk/`
- login page loads at `/login/`

## Step 6. Create Mandatory Seed Records

Create these records before you try to operate the LMS from the UI.

You can do this in Django admin at `/kuruk/`.

### 6.1 CourseStatus

Model:

- `courses.CourseStatus`

Create exactly these statuses:

1. `draft`
2. `curation`
3. `published`
4. `archived`

Why this matters:

- many views explicitly query these status names
- public course visibility depends on `published`
- authoring and moderation depend on `draft`, `curation`, and `archived`

### 6.2 PricingType

Model:

- `courses.PricingType`

Create at least one pricing type.

Recommended minimum set:

1. `Free`
2. `Buy First`
3. `Subscription`

These become slug codes automatically if omitted:

- `free`
- `buy-first`
- `subscription`

### 6.3 Universiti

Model:

- `authentication.Universiti`

Create at least one university or organization record.

Why this matters:

- partner records depend on it
- some user and partner scoping depends on university relationship

### 6.4 Category

Model:

- `courses.Category`

Create at least one category.

Why this matters:

- course catalog filtering depends on categories
- course creation becomes incomplete without one

## Step 7. Create Core Users in This Order

Create actual user accounts before creating business entities that point to them.

Recommended order:

1. superuser admin
2. partner user
3. instructor user
4. learner test user
5. optional finance user
6. optional curation user
7. optional subscription manager user

### Required role flags

Set these on the right users:

- partner user: `is_partner=True`
- instructor user: `is_instructor=True`
- learner user: keep `is_learner=True`
- finance user: `is_finance=True`
- curation user: `is_curation=True`
- subscription manager: `is_subscription=True`

These flags are defined on `authentication.CustomUser`.

## Step 8. Create Partner and Instructor Entities

After user accounts exist, create the business-side records.

### 8.1 Partner

Model:

- `courses.Partner`

Required links:

- `user`
- `name` pointing to `Universiti`
- `author`

Recommended minimum data:

- user
- university
- phone
- address
- description
- agreed to terms
- status

Recommended initial state:

- `is_active=True`
- `is_verified=True` if you want to skip approval friction in dev
- `status='approved'`

### 8.2 Instructor

Model:

- `courses.Instructor`

Required fields:

- `user`
- `bio`
- `tech`
- `expertise`
- `experience_years`
- `provider` pointing to `Partner`

Recommended initial state:

- `agreement=True`
- `status='Approved'`

Without an approved instructor profile, the instructor discovery and some course flows will not behave like production.

## Step 9. Create the First Course

Before course creation, confirm all of these already exist:

- one `Category`
- one `PricingType`
- one approved `Partner`
- one approved `Instructor`
- `CourseStatus` rows

Then create a `Course`.

Recommended minimum course data:

- course name
- slug
- partner
- instructor
- category
- language
- level
- description
- short description
- start date
- end date
- start enrollment
- end enrollment
- payment model
- status course

Recommended initial status:

- `draft`

## Step 10. Build the Course Content Tree

Create course content in this order:

1. `Section`
2. nested `Section` records if needed
3. `Material`
4. `Assessment`
5. `Question`
6. `Choice`
7. `GradeRange`

This is the core learning structure the learner flows expect.

### Recommended minimum viable course

For the first working course, create:

- 1 course
- 1 top-level section
- 1 lesson material
- 1 assessment
- 3 to 5 questions
- 2 grade ranges

Recommended grade ranges:

1. Fail: `0` to `59.99`
2. Pass: `60` to `100`

## Step 11. Publish Workflow Setup

The content lifecycle in the code follows this pattern:

1. instructor creates draft
2. instructor submits for curation
3. partner reviews
4. superuser publishes

Relevant endpoints:

- instructor submit: `/instructor/course/<course_id>/submit-curation/`
- partner review: `/partner/course/<course_id>/review-curation/`
- superuser publish: `/superuser/course/<course_id>/publish/`

For local bootstrap, you can either:

- use the full workflow
- or directly set up the course so it can become published quickly in admin

If you want the course visible on the public catalog, it must end up with:

- `status_course = published`

## Step 12. Create a Learner and Enroll Them

Create one normal learner user for testing.

Then:

1. log in as learner
2. complete the learner profile if redirected
3. enroll into the course
4. open the learner course workspace
5. test lesson access, progress, comments, and assessment submission

This verifies the end-to-end learning path.

## Step 13. Minimal Working Bootstrap Checklist

Use this if your goal is simply to get a locally usable LMS.

### Infrastructure

1. install dependencies
2. start Redis
3. run migrations
4. create superuser
5. run the server

### Seed data

6. create `CourseStatus`: `draft`, `curation`, `published`, `archived`
7. create `PricingType`: at least `Free`
8. create one `Universiti`
9. create one `Category`

### Users and entities

10. create partner user with `is_partner=True`
11. create instructor user with `is_instructor=True`
12. create learner user
13. create one `Partner`
14. create one approved `Instructor`

### Course and content

15. create one course in `draft`
16. create one section
17. create one material
18. create one assessment
19. create questions and choices
20. create grade ranges
21. publish the course
22. enroll learner

If these 22 steps are complete, the system is operational for the main LMS path.

## Step 14. Recommended Extended Setup

After the minimal setup works, configure optional subsystems.

### Finance and payments

Configure:

- `TRIPAY_API_KEY`
- `TRIPAY_PRIVATE_KEY`
- `TRIPAY_MERCHANT_CODE`

Then test:

- cart
- checkout
- callback
- transaction history
- finance dashboard

### Email flows

Verify:

- account activation
- password reset
- invitation emails

### Licensing

To enable license/subscription management:

1. create subscription manager user with `is_subscription=True`
2. create `License`
3. assign users to license
4. send invitation
5. accept invitation

### Blog CMS

To enable content operations:

1. create blog content
2. test public blog list and detail
3. test custom blog admin routes

### LTI

To enable LTI:

1. set `LTI_ISSUER`
2. set `LTI_CLIENT_ID`
3. configure platform/tool side
4. test launch and response endpoints

## Step 15. Admin UI Creation Order

If you are doing setup entirely through Django admin, use this order:

1. `CustomUser`
2. `Universiti`
3. `CourseStatus`
4. `PricingType`
5. `Category`
6. `Partner`
7. `Instructor`
8. `Course`
9. `Section`
10. `Material`
11. `Assessment`
12. `Question`
13. `Choice`
14. `GradeRange`
15. `Enrollment`
16. optional `License`
17. optional `Invitation`

This order minimizes foreign key and workflow issues.

## Step 16. Common First-Run Failures

### Search returns access denied

Cause:

- `ALLOWED_REFERER` does not match the actual host

### Course list is empty even though course exists

Possible causes:

- course is not `published`
- enrollment window is closed
- required `CourseStatus` rows are missing

### Dashboard redirects to profile edit

Cause:

- required user profile fields are missing

### Finance checkout cannot complete

Cause:

- Tripay keys are missing

### Email flows do nothing or fail

Cause:

- SMTP credentials are placeholders

### Notifications or cache-related features fail

Cause:

- Redis is not running

## Step 17. Suggested Dev Test Sequence

After setup, test the system in this order:

1. login as superuser
2. open `/kuruk/`
3. open `/dasbord/`
4. create seed data
5. create partner and instructor
6. create and publish one course
7. login as learner
8. enroll learner
9. open learner course
10. complete one assessment
11. verify score and progress
12. verify certificate path if applicable

## Source of Truth

This guide is derived from the current application logic in:

- `mysite/settings.py`
- `authentication/models.py`
- `authentication/views.py`
- `courses/models.py`
- `courses/views.py`
- `courses/tes.py`
- `payments/views.py`
- `licensing/models.py`
- `licensing/views.py`
- `instructor/views.py`

