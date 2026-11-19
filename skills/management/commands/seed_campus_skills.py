from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from skills.models import Booking, Message, Profile, Report, Review, Skill


class Command(BaseCommand):
    help = 'Adds repeatable Campus SkillSwap demo accounts and listings.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete demo users and all records owned by them.',
        )

    def handle(self, *args, **options):
        demo_usernames = [
            'maya',
            'jordan',
            'sofia',
            'liam',
            'aisha',
            'noah',
            'elena',
            'caleb',
        ]

        if options['reset']:
            User.objects.filter(username__in=demo_usernames).delete()
            self.stdout.write(self.style.WARNING('Removed existing demo users and their related records.'))

        users = {}
        profiles = [
            ('maya', 'Biology', 2027, 'Second-year biology student and patient study partner.', True),
            (
                'jordan',
                'Computer Science',
                2026,
                'Web developer who enjoys making technology less intimidating.',
                True,
            ),
            (
                'sofia',
                'Graphic Design',
                2027,
                'Designer for posters, presentations, and social content.',
                True,
            ),
            ('liam', 'Music', 2028, 'Guitarist and beginner-friendly music tutor.', False),
            ('aisha', 'Marketing', 2026, 'Resume reviewer and presentation coach.', True),
            ('noah', 'Pre-Calculus', 2028, 'Math peer tutor available for evening study sessions.', True),
            ('elena', 'Nutrition', 2027, 'Hosts approachable wellness and meal-planning sessions.', True),
            ('caleb', 'Psychology', 2026, 'Campus navigator and organization coach.', False),
        ]
        for username, major, year, bio, verified in profiles:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@example.edu',
                    'first_name': username.title(),
                },
            )
            if created:
                user.set_password('demo1234')
                user.save()
            profile, unused = Profile.objects.get_or_create(user=user)
            profile.major = major
            profile.graduation_year = year
            profile.bio = bio
            profile.campus_email_verified = verified
            profile.save()
            users[username] = user

        listings = [
            (
                'Calculus II Study Sessions',
                'Tutoring',
                'Clear, step-by-step help with integrals, series, and exam prep.',
                '18.00',
                'maya',
                'Sid Richardson 204',
                'Monday and Wednesday evenings',
                True,
            ),
            (
                'Build a Personal Website',
                'Technology',
                'Turn a blank page into a polished portfolio with beginner-friendly HTML and CSS.',
                '25.00',
                'jordan',
                'Online',
                'Weekends',
                True,
            ),
            (
                'Poster and Event Flyer Design',
                'Creative',
                'Campus-ready poster concepts for organizations, meetings, and social events.',
                '20.00',
                'sofia',
                'Student Union',
                'Tuesday and Thursday afternoons',
                True,
            ),
            (
                'Beginner Guitar Lessons',
                'Creative',
                'Learn a few songs, basic chords, and practice habits with an acoustic guitar.',
                '15.00',
                'liam',
                'Online',
                'Friday afternoons',
                True,
            ),
            (
                'Resume and LinkedIn Review',
                'Campus Life',
                'A practical review for first applications, internships, and campus jobs.',
                '12.00',
                'aisha',
                'Online',
                'Weekday evenings',
                True,
            ),
            (
                'Stats Homework Support',
                'Tutoring',
                'Friendly support for data sets, distributions, and using spreadsheets for assignments.',
                '17.00',
                'noah',
                'Baylor Library',
                'Sunday afternoons',
                True,
            ),
            (
                'Balanced Dorm Meal Planning',
                'Wellness',
                'Simple meal ideas for dining halls, small kitchens, and busy weeks.',
                '10.00',
                'elena',
                'Online',
                'Monday evenings',
                False,
            ),
            (
                'Time Management Reset',
                'Wellness',
                'Build a realistic weekly plan, color-coded calendar, and sustainable study routine.',
                '14.00',
                'caleb',
                'Online',
                'Weekdays',
                True,
            ),
            (
                'Python Debugging Help',
                'Technology',
                'Pair through an error, understand the fix, and leave with stronger debugging habits.',
                '22.00',
                'jordan',
                'Paul Foster Library',
                'Saturday mornings',
                True,
            ),
            (
                'Presentation Slide Makeover',
                'Creative',
                'Clarify a presentation story and make slides readable for a campus audience.',
                '19.00',
                'sofia',
                'Online',
                'Evenings',
                True,
            ),
            (
                'Organic Chemistry Review',
                'Tutoring',
                'Mechanisms and reaction practice using active recall and visual study plans.',
                '24.00',
                'maya',
                'Online',
                'Exam weeks',
                True,
            ),
            (
                'Student Org Recruitment Strategy',
                'Campus Life',
                'Plan welcome tables, event messaging, and a simple semester recruitment calendar.',
                '16.00',
                'aisha',
                'Student Union',
                'Weekday afternoons',
                True,
            ),
        ]

        skills = {}
        for title, category, description, price, owner, location, availability, featured in listings:
            skill, unused = Skill.objects.update_or_create(
                owner=users[owner],
                title=title,
                defaults={
                    'category': category,
                    'description': description,
                    'price': price,
                    'location': location,
                    'availability': availability,
                    'featured': featured,
                    'is_active': True,
                },
            )
            skills[title] = skill

        review_data = [
            (
                'Calculus II Study Sessions',
                'jordan',
                5,
                'Maya explained series in a way that finally clicked. I felt much more prepared for the exam.',
            ),
            (
                'Build a Personal Website',
                'maya',
                5,
                'Jordan gave clear explanations and never made me feel behind. My portfolio looks great now.',
            ),
            (
                'Poster and Event Flyer Design',
                'elena',
                5,
                'Sofia understood our club identity immediately and delivered a polished design.',
            ),
            (
                'Resume and LinkedIn Review',
                'caleb',
                4,
                'Very practical feedback and useful examples. The revised resume got more attention.',
            ),
            (
                'Stats Homework Support',
                'sofia',
                5,
                'Noah helped me understand the spreadsheet formulas instead of just giving answers.',
            ),
            (
                'Time Management Reset',
                'liam',
                4,
                'Caleb helped turn a very crowded week into a realistic schedule.',
            ),
            (
                'Python Debugging Help',
                'aisha',
                5,
                'We fixed the bug and I learned a debugging process I can use again.',
            ),
            (
                'Organic Chemistry Review',
                'noah',
                5,
                'Maya drew out every mechanism clearly and checked my understanding.',
            ),
        ]
        for title, reviewer, rating, comment in review_data:
            Review.objects.update_or_create(
                skill=skills[title],
                reviewer=users[reviewer],
                defaults={'rating': rating, 'comment': comment},
            )

        Booking.objects.get_or_create(
            skill=skills['Calculus II Study Sessions'],
            requester=users['jordan'],
            provider=users['maya'],
            defaults={
                'status': 'accepted',
                'requested_time': 'Wednesday at 6:00 PM',
                'note': 'Help reviewing improper integrals before the midterm.',
            },
        )
        Message.objects.get_or_create(
            sender=users['aisha'],
            recipient=users['jordan'],
            skill=skills['Build a Personal Website'],
            defaults={'body': 'Hi! Could you help me add a projects page to my student portfolio?'},
        )
        Report.objects.get_or_create(
            reporter=users['caleb'],
            skill=skills['Time Management Reset'],
            defaults={'reason': 'other', 'details': 'Demo moderation record.', 'status': 'open'},
        )

        self.stdout.write(self.style.SUCCESS(f'Seed complete: {len(users)} users and {len(skills)} skill listings.'))
