from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# =========================
# USER PROFILE
# =========================

class UserProfile(models.Model):

    ROLE_CHOICES = [
        ('citizen', 'Citizen'),
        ('authority', 'Authority'),
        ('worker', 'Haritha Karma Sena'),
    ]

    AVAILABILITY_CHOICES = [
        ('available', 'Available'),
        ('busy', 'Busy'),
        ('off_duty', 'Off Duty'),
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

    # Used for HKS workers
    availability = models.CharField(
        max_length=20,
        choices=AVAILABILITY_CHOICES,
        default='available'
    )

    def __str__(self):
        return f"{self.user.username} - {self.role}"


# =========================
# REPORT
# =========================

class Report(models.Model):

    ISSUE_TYPE_CHOICES = [
        ('Waste Dumping', 'Illegal Waste Dumping'),
        ('Land Clearance', 'Overgrown Vegetation / Land Clearance'),
        ('Stagnant Water', 'Stagnant Water Removal'),
    ]

    STATUS_CHOICES = [
        ('Submitted', 'Submitted'),
        ('Under Inspection', 'Under Inspection'),
        ('Verified', 'Verified'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
        ('Rejected', 'Rejected'),
    ]

    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]

    citizen = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reports'
    )

    issue_type = models.CharField(
        max_length=30,
        choices=ISSUE_TYPE_CHOICES,
        default='Waste Dumping'
    )

    title = models.CharField(
        max_length=200,
        blank=True
    )

    description = models.TextField(blank=True)

    location = models.CharField(
        max_length=255
    )

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

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='Medium'
    )

    def __str__(self):
        return f"{self.id} - {self.title}"


# =========================
# INSPECTION
# =========================

class Inspection(models.Model):

    INSPECTION_STATUS_CHOICES = [
        ('Verified', 'Verified'),
        ('Not Verified', 'Not Verified'),
        ('Requires Action', 'Requires Action'),
    ]

    report = models.OneToOneField(
        Report,
        on_delete=models.CASCADE,
        related_name='inspection'
    )

    inspected_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inspections'
    )

    inspection_status = models.CharField(
        max_length=30,
        choices=INSPECTION_STATUS_CHOICES
    )

    remarks = models.TextField(
        blank=True
    )

    inspected_date = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Inspection - Report {self.report.id}"


# =========================
# MAINTENANCE TASK
# =========================

class MaintenanceTask(models.Model):

    TASK_TYPE_CHOICES = [
        ('Waste Removal', 'Waste Removal'),
        ('Land Clearance', 'Land Clearance'),
        ('Stagnant Water Removal', 'Stagnant Water Removal'),
    ]

    STATUS_CHOICES = [
        ('Pending Assignment', 'Pending Assignment'),
        ('Assigned', 'Assigned'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Rework', 'Rework'),
    ]

    report = models.ForeignKey(
        Report,
        on_delete=models.CASCADE,
        related_name='maintenance_tasks'
    )

    task_type = models.CharField(
        max_length=40,
        choices=TASK_TYPE_CHOICES
    )

    worker = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks'
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='Pending Assignment'
    )

    assigned_date = models.DateTimeField(
        auto_now_add=True
    )

    completed_date = models.DateTimeField(
        null=True,
        blank=True
    )

    remarks = models.TextField(
        blank=True
    )

    def __str__(self):
        return f"Task {self.id} - {self.task_type}"


# =========================
# WORKER ATTENDANCE
# =========================

class Attendance(models.Model):

    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Absent', 'Absent'),
    ]

    worker = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='attendance_records'
    )

    # Current date is automatically used when attendance is created
    date = models.DateField(
        default=timezone.localdate
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='Present'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['worker', 'date'],
                name='unique_worker_attendance_per_day'
            )
        ]

    def __str__(self):
        return f"{self.worker.username} - {self.date}"


# =========================
# LANDOWNER COMPLIANCE
# =========================

class Compliance(models.Model):

    STATUS_CHOICES = [
        ('Notice Issued', 'Notice Issued'),
        ('Pending', 'Pending'),
        ('Complied', 'Complied'),
        ('Non-Complied', 'Non-Complied'),
    ]

    report = models.OneToOneField(
        Report,
        on_delete=models.CASCADE,
        related_name='compliance'
    )

    landowner_name = models.CharField(
        max_length=200
    )

    landowner_contact = models.CharField(
        max_length=20,
        blank=True
    )

    notice_date = models.DateField(
        null=True,
        blank=True
    )

    deadline = models.DateField(
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='Notice Issued'
    )

    remarks = models.TextField(
        blank=True
    )

    def __str__(self):
        return f"Compliance - Report {self.report.id}"


# =========================
# NOTIFICATION
# =========================

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


# =========================
# FEEDBACK
# =========================

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
