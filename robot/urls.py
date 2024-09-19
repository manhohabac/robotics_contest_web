from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('', views.home, name='home'),  # Sử dụng view function cho trang chủ
    path('logout/', views.user_logout, name='user_logout'),
    path('notification/', views.notification, name='notification'),
    path('change-password/', views.change_password, name='change_password'),
    path('profile/', views.user_profile, name='user_profile'),

    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('contests/', views.contest_list, name='contest_list'),
    path('contests/<int:competition_id>/', views.competition_detail, name='competition_detail'),
    path('competitions/register/<int:competition_id>/', views.register_competition, name='register_competition'),
    path('competitions/cancel/<int:competition_id>/', views.cancel_registration, name='cancel_registration'),
    path('contests/add/', views.add_competition, name='add_competition'),
    path('competition/<int:competition_id>/registrations/', views.registration_list, name='registration_list'),

]
