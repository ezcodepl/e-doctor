from django.urls import path
from django.views.generic import TemplateView

from . import views
from django.conf import settings
from django.conf.urls.static import static
from datetime import date, datetime

from .views import ResetPasswordView, CustomPasswordChangeView, PasswordChangeDoneView
from django.contrib.auth import views as auth_views


urlpatterns = [

    path('', views.home, name='home'),
    path('panel/docschedule', views.docschedule, name='docschedule'),
    path('panel/fizschedule', views.fizschedule, name='fizschedule'),
    path('panel/patients', views.patients_list, name='patients_list'),
    path('panel/patients', views.patients_list, name='patients_list'),
#    path('panel/new_patient', views.new_patient, name='new_patient'),
    path('panel/create_news', views.create_news, name='create_news'),
    path('panel/news_list', views.news_list, name='news_list'),
    path('panel/create_templates', views.create_templates, name='create_templates'),
    path('panel/templates_list', views.templates_list, name='templates_list'),

    path('panel/create_patient', views.create_patient, name='create_patient'),
    path('panel/create_visit', views.create_visit, name='create_visit'),
    path('panel/create_new_visit', views.create_new_visit, name='create_new_visit'),

    path('panel/pause_visit', views.pause_visit, name='pause_visit'),
    path('panel/reserve_list', views.reserve_list, name='reserve_list'),
    path('panel/create_reserve_list', views.create_reserve_list, name='create_reserve_list'),
    path('panel/doctors_weekly_plan/', views.doctors_weekly_plan, name='doctors_weekly_plan'),
    path('panel/fiz_weekly_plan/', views.fiz_weekly_plan, name='fiz_weekly_plan'),



    path(f'panel', views.panel, name='panel'),
    path('news', views.news, name='news'),
    path('test', views.test, name='test'),
    path('laseroterapia', views.laseroterapia, name='laseroterapia'),
    path('', views.krioterapia, name='krioterapia'),
    path('news', views.elektroterapia, name='elektroterapia'),

    path('login', views.login_request, name='login_request'),
    path('logout', views.logout_request, name='logout_request'),
    path('login/', auth_views.LoginView.as_view(template_name='vita/login.html'), name='login'),

    path("register", views.register_user, name="register_user"),
    path('patient/password-reset/', ResetPasswordView.as_view(), name='password_reset'),
    path('patient/password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
                      template_name='vita/patient/password_reset_confirm.html'),
                       name='password_reset_confirm'),
    path('patient/password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='vita/patient/password_reset_complete.html'),
         name='password_reset_complete'),

    path('password_change/', CustomPasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', PasswordChangeDoneView.as_view(), name='password_change_done'),

    path("patient/profile", views.profile, name="profile"),
    path('patient/new-visit', views.new_visit, name='new_visit'),
    path('patient/appointments', views.appointments, name='appointments'),
    path('patient/history', views.history, name='history'),
    path('upcoming_appointments', views.upcoming_appointments, name='upcoming_appointments'),

    # path('appointments/', views.appointments, name='appointments'),
    path('appointments/cancel/<int:visit_id>/', views.cancel_appointment, name='cancel_appointment'),



] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)