from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Booking, Favorite, Message, Profile, Report, Review, Skill


class SkillSwapTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='student', password='test-password-123')
        self.skill = Skill.objects.create(
            owner=self.user,
            title='Calculus Tutoring',
            category='Tutoring',
            description='Help with derivatives and integrals.',
            price='15.00',
        )

    def test_skill_list_is_public(self):
        response = self.client.get(reverse('skill_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Calculus Tutoring')

    def test_search_matches_title_and_category(self):
        response = self.client.get(reverse('skill_list'), {'q': 'calculus'})
        self.assertContains(response, 'Calculus Tutoring')
        response = self.client.get(reverse('skill_list'), {'q': 'tutoring'})
        self.assertContains(response, 'Calculus Tutoring')

    def test_owner_can_edit_post(self):
        self.client.login(username='student', password='test-password-123')
        response = self.client.post(
            reverse('skill_edit', args=[self.skill.pk]),
            {
                'title': 'Updated Calculus Tutoring',
                'category': 'Tutoring',
                'description': 'Updated description',
                'price': '20.00',
            },
        )
        self.assertRedirects(response, reverse('skill_detail', args=[self.skill.pk]))

    def test_another_user_cannot_edit_post(self):
        User.objects.create_user(username='other', password='test-password-123')
        self.client.login(username='other', password='test-password-123')
        response = self.client.get(reverse('skill_edit', args=[self.skill.pk]))
        self.assertEqual(response.status_code, 404)

    def test_profile_page_is_available(self):
        Profile.objects.get_or_create(user=self.user)
        response = self.client.get(reverse('profile', args=['student']))
        self.assertEqual(response.status_code, 200)

    def test_owner_cannot_request_own_skill(self):
        self.client.login(username='student', password='test-password-123')
        response = self.client.get(reverse('booking_create', args=[self.skill.pk]))
        self.assertRedirects(response, reverse('skill_detail', args=[self.skill.pk]))

    def test_another_user_can_create_booking(self):
        other = User.objects.create_user(username='other', password='test-password-123')
        self.client.login(username='other', password='test-password-123')
        response = self.client.post(
            reverse('booking_create', args=[self.skill.pk]),
            {
                'requested_time': 'Tuesday at 6 PM',
                'note': 'Please help me review derivatives.',
            },
        )
        self.assertRedirects(response, reverse('dashboard'))
        self.assertTrue(Booking.objects.filter(requester=other, provider=self.user).exists())

    def test_favorite_toggle(self):
        self.client.login(username='student', password='test-password-123')
        response = self.client.post(reverse('favorite_toggle', args=[self.skill.pk]))
        self.assertRedirects(response, reverse('skill_detail', args=[self.skill.pk]))


class BaseCase(TestCase):
    """Two students: `owner` posts a skill, `buyer` interacts with it."""

    password = 'test-password-123'

    def setUp(self):
        self.owner = User.objects.create_user(username='owner', password=self.password)
        self.buyer = User.objects.create_user(username='buyer', password=self.password)
        self.skill = Skill.objects.create(
            owner=self.owner,
            title='Guitar Lessons',
            category='Creative',
            description='Beginner chords.',
            price='20.00',
        )

    def login(self, user):
        self.client.login(username=user.username, password=self.password)


class SkillListFilterTests(BaseCase):
    def test_invalid_price_is_ignored_not_a_crash(self):
        for bad in ('abc', '-5', 'NaN', 'Infinity', '1e999999'):
            response = self.client.get(reverse('skill_list'), {'min_price': bad, 'max_price': bad})
            self.assertEqual(response.status_code, 200, bad)
            self.assertContains(response, 'Guitar Lessons')

    def test_price_range_filters(self):
        Skill.objects.create(owner=self.owner, title='Essay Review', category='Tutoring', description='x', price='5.00')
        response = self.client.get(reverse('skill_list'), {'min_price': '10', 'max_price': '25'})
        self.assertContains(response, 'Guitar Lessons')
        self.assertNotContains(response, 'Essay Review')

    def test_result_count_is_total_not_page_size(self):
        for number in range(11):  # 12 skills total, 9 per page
            Skill.objects.create(
                owner=self.owner, title=f'Extra {number}', category='Other', description='x', price='1.00'
            )
        response = self.client.get(reverse('skill_list'), {'page': 2})
        self.assertContains(response, '12 skills')

    def test_inactive_skills_hidden_from_list(self):
        self.skill.is_active = False
        self.skill.save()
        response = self.client.get(reverse('skill_list'))
        self.assertNotContains(response, 'Guitar Lessons')

    def test_category_counts_use_constant_queries(self):
        # One grouped query for counts, regardless of how many categories exist.
        with self.assertNumQueries(4):  # sessions-free anonymous request
            self.client.get(reverse('skill_list'))


class SkillDetailVisibilityTests(BaseCase):
    def test_inactive_skill_is_404_for_others(self):
        self.skill.is_active = False
        self.skill.save()
        self.login(self.buyer)
        response = self.client.get(reverse('skill_detail', args=[self.skill.pk]))
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "couldn't find that page", status_code=404)

    def test_inactive_skill_visible_to_owner(self):
        self.skill.is_active = False
        self.skill.save()
        self.login(self.owner)
        response = self.client.get(reverse('skill_detail', args=[self.skill.pk]))
        self.assertEqual(response.status_code, 200)


class ReviewTests(BaseCase):
    def test_buyer_can_review_and_resubmit_updates(self):
        self.login(self.buyer)
        url = reverse('skill_detail', args=[self.skill.pk])
        self.client.post(url, {'rating': 4, 'comment': 'Good'})
        self.client.post(url, {'rating': 5, 'comment': 'Great'})
        review = Review.objects.get(skill=self.skill, reviewer=self.buyer)
        self.assertEqual((review.rating, review.comment), (5, 'Great'))

    def test_owner_cannot_review_own_skill(self):
        self.login(self.owner)
        self.client.post(reverse('skill_detail', args=[self.skill.pk]), {'rating': 5, 'comment': 'Me!'})
        self.assertFalse(Review.objects.exists())

    def test_only_reviewer_can_delete_review(self):
        review = Review.objects.create(skill=self.skill, reviewer=self.buyer, rating=3, comment='ok')
        self.login(self.owner)
        response = self.client.post(reverse('review_delete', args=[review.pk]))
        self.assertEqual(response.status_code, 404)
        self.login(self.buyer)
        self.client.post(reverse('review_delete', args=[review.pk]))
        self.assertFalse(Review.objects.exists())


class FavoriteTests(BaseCase):
    def test_get_does_not_change_favorites(self):
        self.login(self.buyer)
        response = self.client.get(reverse('favorite_toggle', args=[self.skill.pk]))
        self.assertEqual(response.status_code, 405)
        self.assertFalse(Favorite.objects.exists())

    def test_post_toggles_on_and_off(self):
        self.login(self.buyer)
        url = reverse('favorite_toggle', args=[self.skill.pk])
        self.client.post(url)
        self.assertTrue(Favorite.objects.filter(user=self.buyer).exists())
        self.client.post(url)
        self.assertFalse(Favorite.objects.exists())


class BookingStatusTests(BaseCase):
    def setUp(self):
        super().setUp()
        self.booking = Booking.objects.create(
            skill=self.skill,
            requester=self.buyer,
            provider=self.owner,
            requested_time='Friday',
            note='Hi',
        )
        self.url = reverse('booking_update', args=[self.booking.pk])

    def status(self):
        self.booking.refresh_from_db()
        return self.booking.status

    def test_provider_accepts_then_completes(self):
        self.login(self.owner)
        self.client.post(self.url, {'status': 'accepted'})
        self.assertEqual(self.status(), 'accepted')
        self.client.post(self.url, {'status': 'completed'})
        self.assertEqual(self.status(), 'completed')

    def test_requester_cannot_accept(self):
        self.login(self.buyer)
        response = self.client.post(self.url, {'status': 'accepted'}, follow=True)
        self.assertEqual(self.status(), 'requested')
        self.assertContains(response, 'alert-danger')

    def test_cannot_skip_straight_to_completed(self):
        self.login(self.owner)
        self.client.post(self.url, {'status': 'completed'})
        self.assertEqual(self.status(), 'requested')

    def test_cancelled_booking_cannot_be_reopened(self):
        self.login(self.buyer)
        self.client.post(self.url, {'status': 'cancelled'})
        self.client.post(self.url, {'status': 'requested'})
        self.assertEqual(self.status(), 'cancelled')

    def test_outsider_gets_404(self):
        outsider = User.objects.create_user(username='outsider', password=self.password)
        self.login(outsider)
        response = self.client.post(self.url, {'status': 'cancelled'})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.status(), 'requested')

    def test_get_is_rejected(self):
        self.login(self.owner)
        self.assertEqual(self.client.get(self.url).status_code, 405)


class MessageTests(BaseCase):
    def test_send_message_and_mark_read(self):
        self.login(self.buyer)
        self.client.post(reverse('message_create', args=['owner']), {'body': 'Hello', 'skill': self.skill.pk})
        message = Message.objects.get()
        self.assertEqual((message.sender, message.recipient, message.skill), (self.buyer, self.owner, self.skill))
        self.assertIsNone(message.read_at)
        self.login(self.owner)
        self.client.get(reverse('inbox'))
        message.refresh_from_db()
        self.assertIsNotNone(message.read_at)

    def test_cannot_message_yourself(self):
        self.login(self.buyer)
        self.client.post(reverse('message_create', args=['buyer']), {'body': 'Me'})
        self.assertFalse(Message.objects.exists())

    def test_inbox_only_shows_own_messages(self):
        third = User.objects.create_user(username='third', password=self.password)
        Message.objects.create(sender=third, recipient=self.owner, body='Secret for owner')
        self.login(self.buyer)
        self.assertNotContains(self.client.get(reverse('inbox')), 'Secret for owner')


class ReportAndAuthTests(BaseCase):
    def test_report_is_saved(self):
        self.login(self.buyer)
        self.client.post(reverse('report_create', args=[self.skill.pk]), {'reason': 'spam', 'details': 'x'})
        self.assertTrue(Report.objects.filter(reporter=self.buyer, skill=self.skill).exists())

    def test_login_required_pages_redirect(self):
        for name, args in [
            ('dashboard', []),
            ('inbox', []),
            ('skill_create', []),
            ('report_create', [self.skill.pk]),
        ]:
            response = self.client.get(reverse(name, args=args))
            self.assertEqual(response.status_code, 302, name)
            self.assertIn(reverse('login'), response['Location'])

    def test_other_user_cannot_delete_skill(self):
        self.login(self.buyer)
        response = self.client.post(reverse('skill_delete', args=[self.skill.pk]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Skill.objects.filter(pk=self.skill.pk).exists())

    def test_register_logs_in(self):
        response = self.client.post(
            reverse('register'),
            {
                'username': 'newstudent',
                'email': 'new@example.edu',
                'password1': 'a-Strong-pass-981',
                'password2': 'a-Strong-pass-981',
            },
        )
        self.assertRedirects(response, reverse('dashboard'))
