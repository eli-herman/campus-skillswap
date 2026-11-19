from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import (
    BookingForm,
    MessageForm,
    ProfileForm,
    ReportForm,
    ReviewForm,
    SignUpForm,
    SkillForm,
)
from .models import Booking, Favorite, Message, Profile, Review, Skill


def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Welcome to Campus SkillSwap!')
            return redirect('dashboard')
    else:
        form = SignUpForm()
    return render(request, 'skills/register.html', {'form': form})


MAX_PRICE = Decimal('999999.99')  # Largest value Skill.price (max_digits=8, 2 decimals) can hold.


def parse_price(value):
    """Return a price from a query-string value, or None if it isn't a usable one."""
    try:
        price = Decimal(value)
    except (InvalidOperation, TypeError):
        return None
    if not price.is_finite() or price < 0 or price > MAX_PRICE:
        return None
    return price


def skill_list(request):
    skills = Skill.objects.filter(is_active=True).annotate(
        rating_average=Avg('reviews__rating'),
        review_total=Count('reviews'),
    )
    search = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()
    min_price = request.GET.get('min_price', '').strip()
    max_price = request.GET.get('max_price', '').strip()
    sort = request.GET.get('sort', 'newest')

    if search:
        skills = skills.filter(
            Q(title__icontains=search)
            | Q(category__icontains=search)
            | Q(description__icontains=search)
            | Q(owner__username__icontains=search)
        )
    if category:
        skills = skills.filter(category__iexact=category)
    # Ignore anything that isn't a valid price instead of crashing the page.
    min_value = parse_price(min_price)
    max_value = parse_price(max_price)
    min_price = '' if min_value is None else min_price
    max_price = '' if max_value is None else max_price
    if min_value is not None:
        skills = skills.filter(price__gte=min_value)
    if max_value is not None:
        skills = skills.filter(price__lte=max_value)

    if sort == 'price_low':
        skills = skills.order_by('price')
    elif sort == 'price_high':
        skills = skills.order_by('-price')
    elif sort == 'rating':
        skills = skills.order_by('-rating_average', '-created_at')
    else:
        skills = skills.order_by('-featured', '-created_at')

    paginator = Paginator(skills, 9)
    page_obj = paginator.get_page(request.GET.get('page'))
    # One grouped query instead of one query per category.
    counted = dict(Skill.objects.filter(is_active=True).values_list('category').annotate(total=Count('id')).order_by())
    category_counts = {value: counted.get(value, 0) for value, label in Skill.CATEGORY_CHOICES}

    return render(
        request,
        'skills/skill_list.html',
        {
            'skills': page_obj,
            'page_obj': page_obj,
            'search': search,
            'category': category,
            'min_price': min_price,
            'max_price': max_price,
            'sort': sort,
            'categories': Skill.CATEGORY_CHOICES,
            'category_counts': category_counts,
        },
    )


def skill_detail(request, pk):
    skill = get_object_or_404(Skill, pk=pk)
    # Hidden (inactive) posts are only visible to their owner.
    if not skill.is_active and request.user != skill.owner:
        raise Http404
    existing_review = None
    review_form = None
    is_favorite = False
    booking_form = None
    report_form = None
    message_form = None

    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(user=request.user, skill=skill).exists()
        if request.user != skill.owner:
            report_form = ReportForm()
            message_form = MessageForm()
            booking_form = BookingForm()

    if request.user.is_authenticated and request.user != skill.owner:
        existing_review = Review.objects.filter(skill=skill, reviewer=request.user).first()
        if request.method == 'POST':
            review_form = ReviewForm(request.POST, instance=existing_review)
            if review_form.is_valid():
                review = review_form.save(commit=False)
                review.skill = skill
                review.reviewer = request.user
                review.save()
                messages.success(request, 'Your review was saved.')
                return redirect('skill_detail', pk=skill.pk)
        else:
            review_form = ReviewForm(instance=existing_review)

    return render(
        request,
        'skills/skill_detail.html',
        {
            'skill': skill,
            'review_form': review_form,
            'existing_review': existing_review,
            'is_favorite': is_favorite,
            'booking_form': booking_form,
            'report_form': report_form,
            'message_form': message_form,
        },
    )


@login_required
def skill_create(request):
    if request.method == 'POST':
        form = SkillForm(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.owner = request.user
            skill.save()
            messages.success(request, 'Your skill post is live.')
            return redirect('skill_detail', pk=skill.pk)
    else:
        form = SkillForm()
    return render(request, 'skills/skill_form.html', {'form': form, 'action': 'Create'})


@login_required
def skill_edit(request, pk):
    skill = get_object_or_404(Skill, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = SkillForm(request.POST, instance=skill)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your skill post was updated.')
            return redirect('skill_detail', pk=skill.pk)
    else:
        form = SkillForm(instance=skill)
    return render(request, 'skills/skill_form.html', {'form': form, 'action': 'Edit', 'skill': skill})


@login_required
def skill_delete(request, pk):
    skill = get_object_or_404(Skill, pk=pk, owner=request.user)
    if request.method == 'POST':
        skill.delete()
        messages.success(request, 'Your skill post was deleted.')
        return redirect('dashboard')
    return render(request, 'skills/skill_confirm_delete.html', {'skill': skill})


@login_required
def dashboard(request):
    skills = Skill.objects.filter(owner=request.user)
    sent_requests = Booking.objects.filter(requester=request.user)
    received_requests = Booking.objects.filter(provider=request.user)
    unread_messages = Message.objects.filter(recipient=request.user, read_at__isnull=True).count()
    favorites = Skill.objects.filter(favorited_by__user=request.user)
    return render(
        request,
        'skills/dashboard.html',
        {
            'skills': skills,
            'sent_requests': sent_requests,
            'received_requests': received_requests,
            'unread_messages': unread_messages,
            'favorites': favorites,
        },
    )


def profile(request, username):
    user = get_object_or_404(User, username=username)
    profile, unused = Profile.objects.get_or_create(user=user)
    if request.user == user and request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile was updated.')
            return redirect('profile', username=user.username)
    else:
        form = ProfileForm(instance=profile) if request.user == user else None
    skills = Skill.objects.filter(owner=user, is_active=True)
    return render(
        request,
        'skills/profile.html',
        {
            'profile_user': user,
            'profile': profile,
            'profile_form': form,
            'skills': skills,
        },
    )


@login_required
@require_POST
def favorite_toggle(request, pk):
    skill = get_object_or_404(Skill, pk=pk)
    favorite = Favorite.objects.filter(user=request.user, skill=skill).first()
    if favorite:
        favorite.delete()
        messages.success(request, 'Removed from favorites.')
    else:
        Favorite.objects.create(user=request.user, skill=skill)
        messages.success(request, 'Saved to favorites.')
    return redirect('skill_detail', pk=skill.pk)


@login_required
def booking_create(request, pk):
    skill = get_object_or_404(Skill, pk=pk)
    if skill.owner == request.user:
        messages.error(request, 'You cannot request your own skill.')
        return redirect('skill_detail', pk=skill.pk)
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.skill = skill
            booking.requester = request.user
            booking.provider = skill.owner
            booking.save()
            messages.success(request, 'Your booking request was sent.')
            return redirect('dashboard')
    else:
        form = BookingForm()
    return render(request, 'skills/booking_form.html', {'skill': skill, 'form': form})


@login_required
@require_POST
def booking_update(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if request.user not in (booking.provider, booking.requester):
        raise Http404
    status = request.POST.get('status')
    if not booking.can_change_to(status, request.user):
        messages.error(request, 'That change is not allowed for this booking.')
    else:
        booking.status = status
        booking.save(update_fields=['status'])
        if status == 'cancelled':
            messages.success(request, 'The booking was cancelled.')
        else:
            messages.success(request, 'Booking status updated.')
    return redirect('dashboard')


@login_required
def inbox(request):
    messages_for_user = Message.objects.filter(recipient=request.user).select_related('sender', 'skill')
    sent = Message.objects.filter(sender=request.user).select_related('recipient', 'skill')
    unread = messages_for_user.filter(read_at__isnull=True)
    unread.update(read_at=timezone.now())
    return render(
        request,
        'skills/inbox.html',
        {
            'messages_received': messages_for_user,
            'messages_sent': sent,
        },
    )


@login_required
def message_create(request, username):
    recipient = get_object_or_404(User, username=username)
    skill_id = request.GET.get('skill')
    skill = Skill.objects.filter(pk=skill_id).first() if skill_id else None
    if recipient == request.user:
        messages.error(request, 'You cannot message yourself.')
        return redirect('dashboard')
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.recipient = recipient
            message.skill = Skill.objects.filter(pk=request.POST.get('skill')).first()
            message.save()
            messages.success(request, 'Message sent.')
            return redirect('inbox')
    else:
        form = MessageForm()
    return render(
        request,
        'skills/message_form.html',
        {
            'recipient': recipient,
            'skill': skill,
            'form': form,
        },
    )


@login_required
def report_create(request, pk):
    skill = get_object_or_404(Skill, pk=pk)
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user
            report.skill = skill
            report.save()
            messages.success(request, 'Thank you. Your report will be reviewed.')
            return redirect('skill_detail', pk=skill.pk)
    else:
        form = ReportForm()
    return render(request, 'skills/report_form.html', {'skill': skill, 'form': form})


@login_required
def review_delete(request, pk):
    review = get_object_or_404(Review, pk=pk, reviewer=request.user)
    skill_pk = review.skill.pk
    if request.method == 'POST':
        review.delete()
        messages.success(request, 'Your review was deleted.')
        return redirect('skill_detail', pk=skill_pk)
    return render(request, 'skills/review_confirm_delete.html', {'review': review})
