from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('', views.home, name='home'),  # Sử dụng view function cho trang chủ
    path('logout/', views.user_logout, name='user_logout'),
    path('change-password/', views.change_password, name='change_password'),
    path('profile/', views.user_profile, name='user_profile'),

    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('contests/', views.contest_list, name='contest_list'),
    path('contests/<int:competition_id>/', views.competition_detail, name='competition_detail'),
    path('competitions/register/<int:competition_id>/', views.register_competition, name='register_competition'),
    path('competitions/cancel/<int:competition_id>/', views.cancel_registration, name='cancel_registration'),
    path('contests/add/', views.add_competition, name='add_competition'),
    path('competition/<int:competition_id>/registrations/', views.registration_list, name='registration_list'),

    path('competition/<int:competition_id>/edit/', views.edit_competition, name='edit_competition'),
    path('competition/<int:competition_id>/delete/', views.delete_competition, name='delete_competition'),

    # URL cho notification_view
    path('notifications/', views.notification_view, name='notification'),

    # URL cho mark_as_read
    path('notifications/read/<int:notification_id>/', views.mark_as_read, name='mark_as_read'),
    path('results/', views.result_list, name='result_list'),
    path('results/<int:competition_id>/', views.result_detail, name='result_detail'),
    path('results/<int:competition_id>/add/', views.add_result, name='add_result'),
    path('edit_result/<int:result_id>/', views.edit_result, name='edit_result'),
    path('kits', views.kit_list, name='kit_list'),
    path('kits/add/', views.add_kit, name='add_kit'),
    path('kits/<int:kit_id>/', views.kit_detail, name='kit_detail'),
    path('kits/<int:kit_id>/edit/', views.edit_kit, name='edit_kit'),
    path('kits/<int:kit_id>/delete/', views.delete_kit, name='delete_kit'),

]
