from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone
from functools import wraps

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

            return redirect('admin_dashboard')

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


def admin_required(view_func):

    @wraps(view_func)
    @login_required
    def wrapped_view(request, *args, **kwargs):

        if not request.user.is_superuser:

            messages.error(
                request,
                'Access denied.'
            )

            return redirect('login')

        return view_func(request, *args, **kwargs)

    return wrapped_view


def _create_managed_account(request, role):

    username = request.POST.get('username', '').strip()
    email = request.POST.get('email', '').strip()
    full_name = request.POST.get('full_name', '').strip()
    phone = request.POST.get('phone', '').strip()
    password = request.POST.get('password', '')
    confirm_password = request.POST.get('confirm_password', '')

    if not username or not password:
        return 'Username and password are required.'

    if password != confirm_password:
        return 'Passwords do not match.'

    if User.objects.filter(username=username).exists():
        return 'Username already exists.'

    if email and User.objects.filter(email=email).exists():
        return 'Email already exists.'

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=full_name
    )

    UserProfile.objects.create(
        user=user,
        role=role,
        phone=phone
    )

    return None


@admin_required
def admin_dashboard(request):

    total_reports = Report.objects.count()
    pending_reports = Report.objects.exclude(
        status__in=['Resolved', 'Rejected']
    ).count()
    total_authorities = UserProfile.objects.filter(
        role='authority'
    ).count()
    total_workers = UserProfile.objects.filter(
        role='worker'
    ).count()
    present_workers = Attendance.objects.filter(
        date=timezone.localdate(),
        status='Present',
        worker__userprofile__role='worker'
    ).count()
    available_workers = UserProfile.objects.filter(
        role='worker',
        availability='available',
        user__is_active=True
    ).count()
    completed_tasks = MaintenanceTask.objects.filter(
        status='Completed'
    ).count()

    return render(
        request,
        'admin_dashboard.html',
        {
            'total_reports': total_reports,
            'pending_reports': pending_reports,
            'total_authorities': total_authorities,
            'total_workers': total_workers,
            'present_workers': present_workers,
            'available_workers': available_workers,
            'completed_tasks': completed_tasks
        }
    )


@admin_required
def authority_management(request):

    if request.method == 'POST':

        if request.POST.get('action') == 'toggle':
            authority = get_object_or_404(
                User,
                id=request.POST.get('user_id'),
                userprofile__role='authority'
            )
            authority.is_active = not authority.is_active
            authority.save(update_fields=['is_active'])
            messages.success(request, 'Authority account status updated.')

        else:
            error = _create_managed_account(request, 'authority')
            if error:
                messages.error(request, error)
            else:
                messages.success(request, 'Authority account created successfully.')

        return redirect('authority_management')

    authority_users = UserProfile.objects.filter(
        role='authority'
    ).select_related('user').order_by('user__first_name', 'user__username')

    return render(
        request,
        'authority_management.html',
        {'authority_users': authority_users}
    )


@admin_required
def hks_management(request):

    if request.method == 'POST':

        error = _create_managed_account(request, 'worker')
        if error:
            messages.error(request, error)
        else:
            messages.success(request, 'HKS worker account created successfully.')

        return redirect('hks_management')

    hks_workers = UserProfile.objects.filter(
        role='worker'
    ).select_related('user').order_by('user__first_name', 'user__username')

    for worker in hks_workers:
        worker.current_task = worker.user.assigned_tasks.filter(
            status__in=['Assigned', 'In Progress']
        ).order_by('-assigned_date').first()
        worker.latest_attendance = worker.user.attendance_records.order_by(
            '-date'
        ).first()

    return render(
        request,
        'hks_management.html',
        {'hks_workers': hks_workers}
    )


@admin_required
def attendance_monitoring(request):

    attendance_records = Attendance.objects.filter(
        worker__userprofile__role='worker'
    ).select_related('worker').order_by('-date', 'worker__first_name')

    return render(
        request,
        'attendance_monitoring.html',
        {'attendance_records': attendance_records}
    )


@admin_required
def task_monitoring(request):

    tasks = MaintenanceTask.objects.select_related(
        'report',
        'worker'
    ).filter(
        Q(worker__isnull=True) | Q(worker__userprofile__role='worker')
    ).order_by('-assigned_date')

    return render(
        request,
        'task_monitoring.html',
        {'tasks': tasks}
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

    reports = Report.objects.filter(
        citizen=request.user
    ).order_by(
        '-reported_date'
    )

    context = {
        'reports': reports[:5],
        'total_reports': reports.count(),
        'pending_reports': reports.filter(status='Submitted').count(),
        'in_progress_reports': reports.filter(status='In Progress').count(),
        'completed_reports': reports.filter(status='Resolved').count(),
    }

    return render(
        request,
        'citizen_dashboard.html',
        context
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

        report = Report.objects.create(
            citizen=request.user,
            issue_type=issue_type,
            # The selected issue type is the report title; citizens do not
            # need to invent a separate title for a structured report.
            title=issue_types[issue_type],
            description=description,
            location=location,
            image=image
        )

        authority_users = User.objects.filter(
            userprofile__role='authority'
        )
        admin_users = User.objects.filter(
            is_superuser=True
        )
        notification_recipients = list(
            authority_users.union(admin_users)
        )

        Notification.objects.bulk_create([
            Notification(
                user=recipient,
                message=(
                    f'New citizen report #{report.id} received: '
                    f'{report.get_issue_type_display()} at {report.location}.'
                )
            )
            for recipient in notification_recipients
        ])

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

        inspection_status_map = {
            'verified': 'Verified',
            'not_verified': 'Not Verified',
            'requires_action': 'Requires Action'
        }

        if inspection_status not in inspection_status_map:
            messages.error(request, 'Please choose a valid inspection result.')
            return redirect('inspection')

        inspection_status = inspection_status_map[inspection_status]

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

        if inspection_status == 'Requires Action':
            return redirect(f'/authority/maintenance-tasks/?report_id={report.id}')

        return redirect('manage_reports')

    reports = Report.objects.all().order_by('-reported_date')
    selected_report_id = request.GET.get('report_id')
    selected_report = reports.filter(id=selected_report_id).first() if selected_report_id else None

    return render(
        request,
        'inspection.html',
        {
            'reports': reports,
            'selected_report': selected_report
        }
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

    if request.method == 'POST':

        report_id = request.POST.get('report_id')
        task_type = request.POST.get('task_type')
        worker_id = request.POST.get('worker_id')

        valid_task_types = dict(MaintenanceTask.TASK_TYPE_CHOICES)
        report = get_object_or_404(Report, id=report_id)
        worker_profile = UserProfile.objects.filter(
            user_id=worker_id,
            role='worker'
        ).select_related('user').first()

        if task_type not in valid_task_types or worker_profile is None:
            messages.error(request, 'Please choose a valid task type and worker.')
            return redirect(f'/authority/maintenance-tasks/?report_id={report.id}')

        MaintenanceTask.objects.create(
            report=report,
            task_type=task_type,
            worker=worker_profile.user,
            status='Assigned'
        )

        report.status = 'In Progress'
        report.save(update_fields=['status'])

        messages.success(request, 'Maintenance task assigned successfully.')
        return redirect('maintenance_tasks')

    tasks = MaintenanceTask.objects.all().order_by(
        '-assigned_date'
    )

    reports = Report.objects.filter(
        status__in=['Under Inspection', 'Verified', 'In Progress']
    ).order_by('-reported_date')
    workers = UserProfile.objects.filter(
        role='worker',
        availability='available'
    ).select_related('user').order_by('user__first_name', 'user__username')
    selected_report_id = request.GET.get('report_id')
    selected_report = reports.filter(id=selected_report_id).first() if selected_report_id else None

    return render(
        request,
        'maintenance_tasks.html',
        {
            'tasks': tasks,
            'reports': reports,
            'workers': workers,
            'selected_report': selected_report,
            'task_types': MaintenanceTask.TASK_TYPE_CHOICES
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

    if not request.user.is_superuser:

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

    other_status_reports = max(
        total_reports - submitted_reports - verified_reports - resolved_reports,
        0
    )
    other_issue_reports = max(
        total_reports - waste_reports - land_reports - water_reports,
        0
    )

    def chart_percent(value):
        if not total_reports:
            return 0
        return round(value * 100 / total_reports, 2)

    status_stop_1 = chart_percent(submitted_reports)
    status_stop_2 = chart_percent(
        submitted_reports + verified_reports
    )
    status_stop_3 = chart_percent(
        submitted_reports + verified_reports + resolved_reports
    )
    issue_stop_1 = chart_percent(waste_reports)
    issue_stop_2 = chart_percent(waste_reports + land_reports)
    issue_stop_3 = chart_percent(
        waste_reports + land_reports + water_reports
    )

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
            'water_reports': water_reports,
            'other_status_reports': other_status_reports,
            'other_issue_reports': other_issue_reports,
            'status_stop_1': status_stop_1,
            'status_stop_2': status_stop_2,
            'status_stop_3': status_stop_3,
            'issue_stop_1': issue_stop_1,
            'issue_stop_2': issue_stop_2,
            'issue_stop_3': issue_stop_3
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


@login_required
def upload_task_photo(request, task_id):

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

    if request.method != 'POST':

        return redirect('assigned_tasks')

    task = get_object_or_404(
        MaintenanceTask,
        id=task_id,
        worker=request.user
    )

    photo_type = request.POST.get('photo_type')
    photo = request.FILES.get('photo')

    if (
        photo_type not in ['before', 'after']
        or not photo
        or not photo.content_type.startswith('image/')
    ):

        messages.error(
            request,
            'Please choose a before or after photo to upload.'
        )

        return redirect('assigned_tasks')

    if photo_type == 'before':
        task.before_photo = photo
    else:
        task.after_photo = photo

    task.save(update_fields=[f'{photo_type}_photo'])

    messages.success(
        request,
        f'{photo_type.title()} photo uploaded for task {task.id}.'
    )

    return redirect('assigned_tasks')

