from django.contrib import admin
from .models import UserProfile, Report, Notification, Feedback


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        'role',
        'phone'
    )

    list_filter = (
        'role',
    )

    search_fields = (
        'user__username',
        'user__email',
        'phone'
    )


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'citizen',
        'location',
        'status',
        'reported_date'
    )

    list_filter = (
        'status',
    )

    search_fields = (
        'title',
        'description',
        'location',
        'citizen__username'
    )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        'message',
        'created_at',
        'is_read'
    )

    list_filter = (
        'is_read',
    )

    search_fields = (
        'user__username',
        'message'
    )


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        'message',
        'submitted_at'
    )

    search_fields = (
        'user__username',
        'message'
    )