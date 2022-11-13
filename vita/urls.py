from django.urls import path
from . import views

urlpatterns = [

    path('', views.home, name='home'),
    path('news', views.news, name='news'),
    path('login', views.login_request, name='login_request'),
    path('logout', views.logout_request, name='logout_request'),
    path("register", views.register_user, name="register_user"),
    path("patient/profile", views.profile, name="profile"),
    path("patient/profile/update", views.update_profile, name="update_profile"),
]