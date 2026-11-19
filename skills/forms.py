from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Booking, Message, Profile, Report, Review, Skill


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')


class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ('title', 'category', 'description', 'price', 'location', 'availability', 'is_active')
        widgets = {
            'title': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'e.g. Calculus tutoring',
                }
            ),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 5,
                    'placeholder': 'Describe what you offer, when you are available, and how students can contact you.',
                }
            ),
            'price': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.01',
                    'min': '0',
                }
            ),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Student Union or Online'}),
            'availability': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Weekday evenings'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('bio', 'major', 'graduation_year')
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'major': forms.TextInput(attrs={'class': 'form-control'}),
            'graduation_year': forms.NumberInput(attrs={'class': 'form-control', 'min': '2026', 'max': '2035'}),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('rating', 'comment')
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-select'}),
            'comment': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': 'Share what worked well and how this skill helped you.',
                }
            ),
        }


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ('requested_time', 'note')
        widgets = {
            'requested_time': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Tuesday at 6 PM'}),
            'note': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'What would you like help with?'}
            ),
        }


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('body',)
        widgets = {
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Write a message...'})
        }


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ('reason', 'details')
        widgets = {
            'reason': forms.Select(attrs={'class': 'form-select'}),
            'details': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
