from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):

    ROLE_CHOICES = [
        ('citizen', 'Citizen'),
        ('authority', 'Authority'),
        ('worker', 'Haritha Karma Sena'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='citizen'
    )

    phone = models.CharField(
        max_length=15,
        blank=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.role}"


class Report(models.Model):

    STATUS_CHOICES = [
        ('Submitted', 'Submitted'),
        ('Under Inspection', 'Under Inspection'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
        ('Rejected', 'Rejected'),
    ]

    citizen = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reports'
    )

    title = models.CharField(max_length=200)

    description = models.TextField()

    location = models.CharField(max_length=255)

    # Incident photo
    image = models.ImageField(
        upload_to='reports/',
        blank=True,
        null=True
    )

    reported_date = models.DateTimeField(
        auto_now_add=True
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='Submitted'
    )

    def __str__(self):
        return self.title


class Notification(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )

    message = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    is_read = models.BooleanField(
        default=False
    )

    def __str__(self):
        return self.message


class Feedback(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='feedbacks'
    )

    message = models.TextField()

    submitted_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Feedback from {self.user.username}"
