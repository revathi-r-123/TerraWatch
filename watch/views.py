from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils import timezone

from .models import (
    UserProfile,
    Report,
    Inspection,
    MaintenanceTask,
    Attendance,
    Compliance,
    Notification,
    Feedback
)


# =========================================================
# HOME
# =========================================================

def home(request):

    return render(
        request,
        'home.html'
    )


# =========================================================
# REGISTER
# =========================================================

def register_view(request):

    if request.method == 'POST':

        full_name = request.POST.get('full_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:

            return render(
                request,
                'register.html',
                {
                    'error': 'Passwords do not match.'
                }
            )

        if User.objects.filter(username=username).exists():

            return render(
                request,
                'register.html',
                {
                    'error': 'Username already exists.'
                }
            )

        if User.objects.filter(email=email).exists():

            return render(
                request,
                'register.html',
                {
                    'error': 'Email already exists.'
                }
            )

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=full_name
        )

        UserProfile.objects.create(
            user=user,
            role='citizen',
            phone=phone
        )

        return render(
            request,
            'login_page.html',
            {
                'success': 'Registration successful. Please login.'
            }
        )

    return render(
        request,
        'register.html'
    )


# =========================================================
# LOGIN
# =========================================================

def login_view(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        # WRONG USERNAME OR PASSWORD
        if user is None:

            return render(
                request,
                'login_page.html',
                {
                    'error': 'Invalid username or password.',
                    'entered_username': username
                }
            )

        # LOGIN SUCCESSFUL
        login(request, user)

        # SUPERUSER / ADMIN
        if user.is_superuser:

            return redirect('/admin/')

        # GET USER PROFILE
        try:

            profile = UserProfile.objects.get(
                user=user
            )

        except UserProfile.DoesNotExist:

            logout(request)

            return render(
                request,
                'login_page.html',
                {
                    'error': 'User profile not found. Please contact the administrator.'
                }
            )

        # REDIRECT ACCORDING TO ROLE
        if profile.role == 'citizen':

            return redirect(
                'citizen_dashboard'
            )

        elif profile.role == 'authority':

            return redirect(
                'authority_dashboard'
            )

        elif profile.role == 'worker':

            return redirect(
                'worker_dashboard'
            )

        else:

            logout(request)

            return render(
                request,
                'login_page.html',
                {
                    'error': 'Invalid user role.'
                }
            )

    return render(
        request,
        'login_page.html'
    )


# =========================================================
# LOGOUT
# =========================================================

def logout_view(request):

    logout(request)

    return render(
        request,
        'login_page.html',
        {
            'success': 'You have been logged out successfully.'
        }
    )


# =========================================================
# CITIZEN DASHBOARD
# =========================================================

@login_required
def citizen_dashboard(request):

    try:

        profile = UserProfile.objects.get(
            user=request.user
        )

        if profile.role != 'citizen':

            messages.error(
                request,
                'Access denied.'
            )

            return redirect('login')

    except UserProfile.DoesNotExist:

        return redirect('login')

    return render(
        request,
        'citizen_dashboard.html'
    )


# =========================================================
# REPORT AN ISSUE
# =========================================================

@login_required
def report_issue(request):

    try:

        profile = UserProfile.objects.get(
            user=request.user
        )

        if profile.role != 'citizen':

            messages.error(
                request,
                'Access denied.'
            )

            return redirect('login')

    except UserProfile.DoesNotExist:

        return redirect('login')

    if request.method == 'POST':

        issue_type = request.POST.get('issue_type')
        description = request.POST.get('description', '').strip()
        location = request.POST.get('location', '').strip()
        image = request.FILES.get('image')

        issue_types = dict(Report.ISSUE_TYPE_CHOICES)

        if issue_type not in issue_types or not location:

            messages.error(
                request,
                'Please choose an issue type and enter the location.'
            )

            return render(
                request,
                'report_issue.html',
                {
                    'selected_issue_type': issue_type,
                    'description': description,
                    'location': location
                }
            )

        Report.objects.create(
            citizen=request.user,
            issue_type=issue_type,
            # The selected issue type is the report title; citizens do not
            # need to invent a separate title for a structured report.
            title=issue_types[issue_type],
            description=description,
            location=location,
            image=image
        )

        messages.success(
            request,
            'Your issue has been reported successfully.'
        )

        return redirect(
            'my_reports'
        )

    return render(
        request,
        'report_issue.html'
    )


# =========================================================
# MY REPORTS
# =========================================================

@login_required
def my_reports(request):

    reports = Report.objects.filter(
        citizen=request.user
    ).order_by(
        '-reported_date'
    )

    return render(
        request,
        'my_report.html',
        {
            'reports': reports
        }
    )


# =========================================================
# REPORT DETAIL
# =========================================================

@login_required
def report_detail(request, report_id):

    report = get_object_or_404(
        Report,
        id=report_id,
        citizen=request.user
    )

    return render(
        request,
        'report_detail.html',
        {
            'report': report
        }
    )


# =========================================================
# NOTIFICATIONS
# =========================================================

@login_required
def notifications(request):

    notification_list = Notification.objects.filter(
        user=request.user
    ).order_by(
        '-created_at'
    )

    try:

        profile = UserProfile.objects.get(
            user=request.user
        )

        role = profile.role

    except UserProfile.DoesNotExist:

        messages.error(
            request,
            'User profile not found.'
        )

        return redirect('login')

    return render(
        request,
        'notifications.html',
        {
            'notifications': notification_list,
            'role': role
        }
    )


# =========================================================
# FEEDBACK
# =========================================================

@login_required
def feedback(request):

    if request.method == 'POST':

        message = request.POST.get('message')

        Feedback.objects.create(
            user=request.user,
            message=message
        )

        messages.success(
            request,
            'Thank you for your feedback.'
        )

        return redirect(
            'feedback'
        )

    return render(
        request,
        'feedback.html'
    )


# =========================================================
# AUTHORITY DASHBOARD
# =========================================================

@login_required
def authority_dashboard(request):

    try:

        profile = UserProfile.objects.get(
            user=request.user
        )

        if profile.role != 'authority':

            messages.error(
                request,
                'Access denied.'
            )

            return redirect('login')

    except UserProfile.DoesNotExist:

        messages.error(
            request,
            'User profile not found.'
        )

        return redirect('login')

    return render(
        request,
        'authority_dashboard.html'
    )


# =========================================================
# MANAGE REPORTS
# =========================================================

@login_required
def manage_reports(request):

    try:

        profile = UserProfile.objects.get(
            user=request.user
        )

        if profile.role != 'authority':

            messages.error(
                request,
                'Access denied.'
            )

            return redirect('login')

    except UserProfile.DoesNotExist:

        return redirect('login')

    reports = Report.objects.all().order_by(
        '-reported_date'
    )

    return render(
        request,
        'manage_reports.html',
        {
            'reports': reports
        }
    )


# =========================================================
# INSPECTION
# =========================================================

@login_required
def inspection(request):

    try:

        profile = UserProfile.objects.get(
            user=request.user
        )

        if profile.role != 'authority':

            messages.error(
                request,
                'Access denied.'
            )

            return redirect('login')

    except UserProfile.DoesNotExist:

        return redirect('login')

    if request.method == 'POST':

        report_id = request.POST.get('report_id')
        inspection_status = request.POST.get(
            'inspection_status'
        )
        remarks = request.POST.get('remarks')

        report = get_object_or_404(
            Report,
            id=report_id
        )

        Inspection.objects.update_or_create(
            report=report,
            defaults={
                'inspected_by': request.user,
                'inspection_status': inspection_status,
                'remarks': remarks
            }
        )

        if inspection_status == 'Verified':

            report.status = 'Verified'

        elif inspection_status == 'Not Verified':

            report.status = 'Rejected'

        elif inspection_status == 'Requires Action':

            report.status = 'Under Inspection'

        report.save()

        messages.success(
            request,
            'Inspection recorded successfully.'
        )

        return redirect(
            'inspection'
        )

    return render(
        request,
        'inspection.html'
    )


# =========================================================
# MAINTENANCE TASKS
# =========================================================

@login_required
def maintenance_tasks(request):

    try:

        profile = UserProfile.objects.get(
            user=request.user
        )

        if profile.role != 'authority':

            messages.error(
                request,
                'Access denied.'
            )

            return redirect('login')

    except UserProfile.DoesNotExist:

        return redirect('login')

    tasks = MaintenanceTask.objects.all().order_by(
        '-assigned_date'
    )

    return render(
        request,
        'maintenance_tasks.html',
        {
            'tasks': tasks
        }
    )


# =========================================================
# LANDOWNER COMPLIANCE
# =========================================================

@login_required
def compliance(request):

    try:

        profile = UserProfile.objects.get(
            user=request.user
        )

        if profile.role != 'authority':

            messages.error(
                request,
                'Access denied.'
            )

            return redirect('login')

    except UserProfile.DoesNotExist:

        return redirect('login')

    compliance_list = Compliance.objects.all().order_by(
        '-notice_date'
    )

    return render(
        request,
        'compliance.html',
        {
            'compliance_list': compliance_list
        }
    )


# =========================================================
# ANALYTICS
# =========================================================

@login_required
def analytics(request):

    try:

        profile = UserProfile.objects.get(
            user=request.user
        )

        if profile.role != 'authority':

            messages.error(
                request,
                'Access denied.'
            )

            return redirect('login')

    except UserProfile.DoesNotExist:

        return redirect('login')

    total_reports = Report.objects.count()

    submitted_reports = Report.objects.filter(
        status='Submitted'
    ).count()

    verified_reports = Report.objects.filter(
        status='Verified'
    ).count()

    resolved_reports = Report.objects.filter(
        status='Resolved'
    ).count()

    waste_reports = Report.objects.filter(
        issue_type='Waste Dumping'
    ).count()

    land_reports = Report.objects.filter(
        issue_type='Land Clearance'
    ).count()

    water_reports = Report.objects.filter(
        issue_type='Stagnant Water'
    ).count()

    return render(
        request,
        'analytics.html',
        {
            'total_reports': total_reports,
            'submitted_reports': submitted_reports,
            'verified_reports': verified_reports,
            'resolved_reports': resolved_reports,
            'waste_reports': waste_reports,
            'land_reports': land_reports,
            'water_reports': water_reports
        }
    )


# =========================================================
# HKS WORKER DASHBOARD
# =========================================================

@login_required
def worker_dashboard(request):

    try:

        profile = UserProfile.objects.get(
            user=request.user
        )

        if profile.role != 'worker':

            messages.error(
                request,
                'Access denied.'
            )

            return redirect('login')

    except UserProfile.DoesNotExist:

        messages.error(
            request,
            'User profile not found.'
        )

        return redirect('login')

    return render(
        request,
        'worker_dashboard.html',
        {
            'profile': profile
        }
    )


# =========================================================
# WORKER AVAILABILITY
# =========================================================

@login_required
def worker_availability(request):

    try:

        profile = UserProfile.objects.get(
            user=request.user
        )

        if profile.role != 'worker':

            messages.error(
                request,
                'Access denied.'
            )

            return redirect('login')

    except UserProfile.DoesNotExist:

        messages.error(
            request,
            'User profile not found.'
        )

        return redirect('login')

    if request.method == 'POST':

        availability = request.POST.get(
            'availability'
        )

        if availability in [
            'available',
            'busy',
            'off_duty'
        ]:

            profile.availability = availability
            profile.save()

            messages.success(
                request,
                'Availability updated successfully.'
            )

        return redirect(
            'worker_availability'
        )

    return render(
        request,
        'worker_availability.html',
        {
            'profile': profile
        }
    )


# =========================================================
# WORKER ATTENDANCE
# =========================================================

@login_required
def attendance(request):

    try:

        profile = UserProfile.objects.get(
            user=request.user
        )

        if profile.role != 'worker':

            messages.error(
                request,
                'Access denied.'
            )

            return redirect('login')

    except UserProfile.DoesNotExist:

        messages.error(
            request,
            'User profile not found.'
        )

        return redirect('login')

    if request.method == 'POST':

        status = request.POST.get('status')

        if status in [
            'Present',
            'Absent'
        ]:

            today = timezone.localdate()

            attendance_record, created = (
                Attendance.objects.get_or_create(
                    worker=request.user,
                    date=today,
                    defaults={
                        'status': status
                    }
                )
            )

            if not created:

                attendance_record.status = status
                attendance_record.save()

            messages.success(
                request,
                'Attendance marked successfully.'
            )

        return redirect(
            'attendance'
        )

    attendance_records = Attendance.objects.filter(
        worker=request.user
    ).order_by(
        '-date'
    )

    return render(
        request,
        'attendance.html',
        {
            'attendance_records': attendance_records
        }
    )


# =========================================================
# HKS WORKER - ASSIGNED TASKS
# =========================================================

@login_required
def assigned_tasks(request):

    try:

        profile = UserProfile.objects.get(
            user=request.user
        )

        if profile.role != 'worker':

            messages.error(
                request,
                'Access denied.'
            )

            return redirect('login')

    except UserProfile.DoesNotExist:

        messages.error(
            request,
            'User profile not found.'
        )

        return redirect('login')

    tasks = MaintenanceTask.objects.filter(
        worker=request.user
    ).order_by(
        '-assigned_date'
    )

    return render(
        request,
        'assigned_tasks.html',
        {
            'tasks': tasks
        }
    )

