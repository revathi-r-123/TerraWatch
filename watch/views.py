from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User

from .models import UserProfile, Report, Notification, Feedback


# =========================
# REGISTER
# =========================

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
                {'error': 'Passwords do not match.'}
            )

        if User.objects.filter(username=username).exists():
            return render(
                request,
                'register.html',
                {'error': 'Username already exists.'}
            )

        if User.objects.filter(email=email).exists():
            return render(
                request,
                'register.html',
                {'error': 'Email already exists.'}
            )

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=full_name
        )

        # Public registration creates Citizen only
        UserProfile.objects.create(
            user=user,
            role='citizen',
            phone=phone
        )

        return render(
            request,
            'login_page.html',
            {'success': 'Registration successful. Please login.'}
        )

    return render(request, 'register.html')


# =========================
# LOGIN
# =========================
def login_view(request):


 if request.method == 'POST':

    username = request.POST.get('username')
    password = request.POST.get('password')

    user = authenticate(
        request,
        username=username,
        password=password
    )

    if user is None:
        return render(
            request,
            'login_page.html',
            {
                'error': 'Invalid username or password.'
            }
        )

    # Login successful
    login(request, user)

    # Superuser / Admin
    if user.is_superuser:
        return redirect('/admin/')

    # Find user profile
    try:
        profile = UserProfile.objects.get(user=user)

    except UserProfile.DoesNotExist:
        logout(request)

        return render(
            request,
            'login_page.html',
            {
                'error': 'User profile not found. Please contact the administrator.'
            }
        )

    # Redirect according to role
    if profile.role == 'citizen':
        return redirect('citizen_dashboard')

    elif profile.role == 'authority':
        return redirect('authority_dashboard')

    elif profile.role == 'worker':
        return redirect('worker_dashboard')

    else:
        logout(request)

        return render(
            request,
            'login_page.html',
            {
                'error': 'Invalid user role.'
            }
        )

 return render(request, 'login_page.html')




# =========================
# LOGOUT
# =========================

def logout_view(request):

    logout(request)

    return render(
        request,
        'login_page.html',
        {
            'success':
            'You have been logged out successfully.'
        }
    )


# =========================
# CITIZEN DASHBOARD
# =========================

@login_required
def citizen_dashboard(request):

    try:
        profile = UserProfile.objects.get(user=request.user)

        if profile.role != 'citizen':
            messages.error(request, 'Access denied.')
            return redirect('login')

    except UserProfile.DoesNotExist:
        return redirect('login')

    return render(
        request,
        'citizen_dashboard.html'
    )


# =========================
# REPORT AN ISSUE
# =========================

@login_required
def report_issue(request):

    try:
        profile = UserProfile.objects.get(user=request.user)

        if profile.role != 'citizen':
            messages.error(request, 'Access denied.')
            return redirect('login')

    except UserProfile.DoesNotExist:
        return redirect('login')

    if request.method == 'POST':

        title = request.POST.get('title')
        description = request.POST.get('description')
        location = request.POST.get('location')

        image = request.FILES.get('image')

        Report.objects.create(
            citizen=request.user,
            title=title,
            description=description,
            location=location,
            image=image
        )

        messages.success(
            request,
            'Your issue has been reported successfully.'
        )

        return redirect('my_reports')

    return render(
        request,
        'report_issue.html'
    )


# =========================
# MY REPORTS
# =========================

@login_required
def my_reports(request):

    reports = Report.objects.filter(
        citizen=request.user
    ).order_by('-reported_date')

    return render(
        request,
        'my_reports.html',
        {
            'reports': reports
        }
    )


# =========================
# REPORT DETAIL
# =========================

@login_required
def report_detail(request, report_id):

    report = Report.objects.get(
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


# =========================
# NOTIFICATIONS
# =========================

@login_required
def notifications(request):

    notification_list = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(
        request,
        'notifications.html',
        {
            'notifications': notification_list
        }
    )


# =========================
# FEEDBACK
# =========================

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

        return redirect('feedback')

    return render(
        request,
        'feedback.html'
    )


# =========================
# AUTHORITY DASHBOARD
# =========================

@login_required
def authority_dashboard(request):

    try:
        profile = UserProfile.objects.get(user=request.user)

        if profile.role != 'authority':
            messages.error(request, 'Access denied.')
            return redirect('login')

    except UserProfile.DoesNotExist:
        return redirect('login')

    return render(
        request,
        'authority_dashboard.html'
    )


# =========================
# HKS WORKER DASHBOARD
# =========================

@login_required
def worker_dashboard(request):

    try:
        profile = UserProfile.objects.get(user=request.user)

        if profile.role != 'worker':
            messages.error(request, 'Access denied.')
            return redirect('login')

    except UserProfile.DoesNotExist:
        return redirect('login')

    return render(
        request,
        'worker_dashboard.html'
    )
