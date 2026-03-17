# Seed Data Guide

## Purpose

This project now includes a bootstrap seed command that creates:

- required reference data
- sample users for each main role
- partner and instructor entities
- sample free, paid, and draft courses
- sections, materials, assessments, questions, and choices
- enrollments, progress, ratings, comments, and a certificate
- a microcredential and related enrollment
- a completed payment, transaction, voucher, and cart item
- a sample license and invitation
- notifications, activity logs, social content, and a blog post

## Command

Run:

```bash
python manage.py seed_bootstrap_data
```

The command is designed to be idempotent:

- it updates or reuses deterministic seed records
- it does not wipe the database
- re-running it should not create uncontrolled duplicates

## Seeded Accounts

All seeded accounts use the same password:

```text
SeedDemo123!
```

Accounts created:

- `admin.seed@jakija.local`
- `partner.seed@jakija.local`
- `instructor.seed@jakija.local`
- `learner.seed@jakija.local`
- `finance.seed@jakija.local`
- `curation.seed@jakija.local`
- `subscription.seed@jakija.local`

## What It Seeds

### Reference data

- `CourseStatus`
  - `draft`
  - `curation`
  - `published`
  - `archived`
- `PricingType`
  - `Free`
  - `Buy First`
  - `Subscription`
- one `Universiti`
- two `Category` rows
- one blacklisted keyword

### Users and entities

- one superuser
- partner, instructor, learner, finance, curation, and subscription users
- one approved `Partner`
- one approved `Instructor`

### LMS content

- one published free course
- one published paid course
- one draft course
- sections and materials on each course
- one quiz assessment per course structure
- seeded questions and choices
- grade ranges

### Learner sample data

- enrollment into free and paid courses
- progress records
- comments
- ratings
- a course certificate
- a last-access record

### Commerce sample data

- one completed transaction
- one completed payment
- one voucher
- one cart item

### Licensing sample data

- one license
- one invitation

### Extra surface data

- notifications
- user activity logs
- one social post
- one published blog post and comment
- one active microcredential

## What It Does Not Fully Provision

The command does not fully wire real external integrations.

These still require real environment-specific configuration:

- SMTP credentials
- Tripay credentials
- social login provider credentials
- live LTI provider registration values
- Redis runtime availability

## Recommended Usage

1. Run migrations
2. Run the seed command
3. Start the server
4. Log in with one of the seeded accounts
5. Verify:
   - `/kuruk/`
   - `/dasbord/`
   - `/courses/`
   - `/mycourse/`
   - `/dashboard/`
   - `/dashboard/finance`

