from django.urls import path
from . import views

urlpatterns = [

    # Authentication
    path(
        'login/',
        views.login_view,
        name='login'
    ),

    path(
        'register/',
        views.register_view,
        name='register'
    ),

    path(
        'logout/',
        views.logout_view,
        name='logout'
    ),

    # Citizen
    path(
        'citizen/dashboard/',
        views.citizen_dashboard,
        name='citizen_dashboard'
    ),

    path(
        'citizen/report-issue/',
        views.report_issue,
        name='report_issue'
    ),

    path(
        'citizen/my-reports/',
        views.my_reports,
        name='my_reports'
    ),

    path(
        'citizen/report/<int:report_id>/',
        views.report_detail,
        name='report_detail'
    ),

    # Notifications
    path(
        'notifications/',
        views.notifications,
        name='notifications'
    ),

    # Feedback
    path(
        'feedback/',
        views.feedback,
        name='feedback'
    ),

    # Authority
    path(
        'authority/dashboard/',
        views.authority_dashboard,
        name='authority_dashboard'
    ),

    # HKS Worker
    path(
        'worker/dashboard/',
        views.worker_dashboard,
        name='worker_dashboard'
    ),
]
