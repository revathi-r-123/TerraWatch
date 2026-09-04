from django.urls import path
from . import views


urlpatterns = [

    # =========================================================
    # HOME
    # =========================================================

    path(
        '',
        views.home,
        name='home'
    ),


    # =========================================================
    # AUTHENTICATION
    # =========================================================

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


    # =========================================================
    # CITIZEN
    # =========================================================

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


    # =========================================================
    # NOTIFICATIONS
    # =========================================================

    path(
        'notifications/',
        views.notifications,
        name='notifications'
    ),


    # =========================================================
    # FEEDBACK
    # =========================================================

    path(
        'feedback/',
        views.feedback,
        name='feedback'
    ),


    # =========================================================
    # AUTHORITY
    # =========================================================

    path(
        'authority/dashboard/',
        views.authority_dashboard,
        name='authority_dashboard'
    ),

    path(
        'authority/manage-reports/',
        views.manage_reports,
        name='manage_reports'
    ),

    path(
        'authority/inspection/',
        views.inspection,
        name='inspection'
    ),

    path(
        'authority/maintenance-tasks/',
        views.maintenance_tasks,
        name='maintenance_tasks'
    ),

    path(
        'authority/compliance/',
        views.compliance,
        name='compliance'
    ),

    path(
        'authority/analytics/',
        views.analytics,
        name='analytics'
    ),


    # =========================================================
    # HKS WORKER
    # =========================================================

    path(
        'worker/dashboard/',
        views.worker_dashboard,
        name='worker_dashboard'
    ),

    path(
        'worker/assigned-tasks/',
        views.assigned_tasks,
        name='assigned_tasks'
    ),

    path(
        'worker/attendance/',
        views.attendance,
        name='attendance'
    ),

    path(
        'worker/availability/',
        views.worker_availability,
        name='worker_availability'
    ),
]

