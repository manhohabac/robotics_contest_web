from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


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
    path('edit_result/<int:competition_id>/<int:result_id>/', views.edit_result, name='edit_result'),
    path('kits/', views.kit_list, name='kit_list'),
    path('kits/new/', views.kit_create, name='kit_create'),
    path('kits/<int:pk>/edit/', views.kit_update, name='kit_update'),
    path('kits/<int:pk>/delete/', views.kit_delete, name='kit_delete'),
    path('kits/<int:pk>/', views.kit_detail, name='kit_detail'),  # Thêm dòng này
    path('kit/<int:kit_id>/add_image/', views.add_image, name='add_image'),
    path('sponsors/', views.sponsor_list, name='sponsor_list'),
    path('sponsors/add/', views.add_sponsor, name='add_sponsor'),
    path('sponsors/edit/<int:sponsor_id>/', views.edit_sponsor, name='edit_sponsor'),
    path('sponsors/delete/<int:sponsor_id>/', views.delete_sponsor, name='delete_sponsor'),
    path('feedback/submit/', views.submit_feedback, name='submit_feedback'),
    path('feedback/list/', views.feedback_list, name='feedback_list'),
    path('toggle-viewed/<int:feedback_id>/', views.toggle_viewed_status, name='toggle_viewed_status'),
    path('feedback/export/', views.export_feedback_to_excel, name='export_feedback_to_excel'),
    path('competition/<int:competition_id>/registrations/export/', views.export_registrations_to_excel,
         name='export_registrations_to_excel'),
    path('competition/<int:competition_id>/results/export/', views.export_results_to_excel,
         name='export_results_to_excel'),
    path('competition/<int:competition_id>/guide/', views.competition_guide, name='competition_guide'),
    path('guide-file/edit/<int:pk>/', views.edit_guide_file, name='edit_guide_file'),
    path('guide-file/delete/<int:pk>/', views.delete_guide_file, name='delete_guide_file'),
    path('competition/guide/confirm/<int:guide_file_id>/', views.confirm_guide_file, name='confirm_guide_file'),
    path('download_guide_file/<int:guide_file_id>/', views.download_guide_file, name='download_guide_file'),
    path('competition/<int:competition_id>/team/<int:team_id>/', views.team_detail, name='registration_info_detail'),
    path('registration/history/', views.registration_history, name='registration_history'),
    path('manage-users/', views.manage_users, name='manage_users'),

    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('competition/<int:competition_id>/edit/<int:team_id>/', views.edit_registration, name='edit_registration')
]
