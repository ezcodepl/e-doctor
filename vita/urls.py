from django.urls import path
from . import views



urlpatterns = [

    path('', views.home, name='home'),
    path('panel/terminarz', views.terminarz, name='terminarz'),
    # path('panel/', views.panel, name='panel'),
    path('news', views.news, name='news'),
    path('test', views.test, name='test'),
    path('laseroterapia', views.laseroterapia, name='laseroterapia'),
    path('', views.krioterapia, name='krioterapia'),
    path('news', views.elektroterapia, name='elektroterapia'),

    path('login', views.login_request, name='login_request'),
    path('logout', views.logout_request, name='logout_request'),
    path("register", views.register_user, name="register_user"),
    path("patient/profile", views.profile, name="profile"),
    path('patient/new-visit', views.new_visit, name='new_visit'),
    path('patient/appointments', views.appointments, name='appointments'),
    path('patient/history', views.history, name='history'),
]