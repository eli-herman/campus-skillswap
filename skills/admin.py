from django.contrib import admin

from .models import Booking, Favorite, Message, Profile, Report, Review, Skill


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'owner', 'price', 'is_active', 'featured', 'created_at')
    list_filter = ('category', 'is_active', 'featured', 'created_at')
    search_fields = ('title', 'description', 'owner__username')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('skill', 'reviewer', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')


admin.site.register(Profile)
admin.site.register(Favorite)
admin.site.register(Booking)
admin.site.register(Message)


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('skill', 'reporter', 'reason', 'status', 'created_at')
    list_filter = ('reason', 'status')
