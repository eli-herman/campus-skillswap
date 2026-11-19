from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, max_length=500)
    major = models.CharField(blank=True, max_length=100)
    graduation_year = models.PositiveIntegerField(blank=True, null=True)
    campus_email_verified = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.username} profile'


class Skill(models.Model):
    CATEGORY_CHOICES = [
        ('Tutoring', 'Tutoring'),
        ('Technology', 'Technology'),
        ('Creative', 'Creative'),
        ('Wellness', 'Wellness'),
        ('Campus Life', 'Campus Life'),
        ('Other', 'Other'),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='skills')
    title = models.CharField(max_length=120)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    location = models.CharField(max_length=120, blank=True)
    availability = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if not reviews:
            return None
        return sum(review.rating for review in reviews) / reviews.count()

    @property
    def review_count(self):
        return self.reviews.count()


class Review(models.Model):
    RATING_CHOICES = [(number, str(number)) for number in range(1, 6)]

    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='skill_reviews')
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['skill', 'reviewer'],
                name='unique_review_per_skill_user',
            )
        ]

    def __str__(self):
        return f'{self.rating}/5 by {self.reviewer.username}'


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'skill')

    def __str__(self):
        return f'{self.user.username} saved {self.skill.title}'


class Booking(models.Model):
    STATUS_CHOICES = [
        ('requested', 'Requested'),
        ('accepted', 'Accepted'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='bookings')
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='booking_requests')
    provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='booking_offers')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='requested')
    requested_time = models.CharField(max_length=200)
    note = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    # Which status each status may move to, and who may make that move.
    TRANSITIONS = {
        'requested': {'accepted': 'provider', 'cancelled': 'either'},
        'accepted': {'completed': 'provider', 'cancelled': 'either'},
        'completed': {},
        'cancelled': {},
    }

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.requester.username} -> {self.skill.title} ({self.status})'

    def can_change_to(self, new_status, user):
        who = self.TRANSITIONS.get(self.status, {}).get(new_status)
        if who == 'either':
            return user in (self.provider, self.requester)
        if who == 'provider':
            return user == self.provider
        return False


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    skill = models.ForeignKey(Skill, on_delete=models.SET_NULL, null=True, blank=True, related_name='messages')
    body = models.TextField(max_length=2000)
    read_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Message from {self.sender.username} to {self.recipient.username}'


class Report(models.Model):
    REASON_CHOICES = [
        ('spam', 'Spam or misleading'),
        ('safety', 'Safety concern'),
        ('harassment', 'Harassment'),
        ('copyright', 'Copyright or intellectual property'),
        ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('reviewing', 'In review'),
        ('resolved', 'Resolved'),
    ]

    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_made')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='reports')
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    details = models.TextField(blank=True, max_length=1000)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.get_reason_display()} report on {self.skill.title}'
