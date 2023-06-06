from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.home, name='home'),
    path('admin-login', views.adminLogin, name='admin-login'),
    path('admin-home', views.adminHome, name='admin-home'),
    path('admin-manage-cooperatives', views.adminCooperativesView, name='admin-manage-cooperatives'),
    path('admin-cooperative-registration', views.adminCooperativesRegistration, name='admin-cooperative-registration'),
    path('admin-exporter-registration', views.adminExportersRegistration, name='admin-exporter-registration'),
    path('admin-manage-exporters', views.adminExportersView, name='admin-manage-exporters'),
    path('cooperative-deletion/<str:pk>/', views.cooperativeDeletion, name = 'admin-delete-cooperative'),
    path('cooperative-login', views.cooperativeLogin, name='cooperative-login'),
    path('cooperative-home', views.cooperativeHome, name='cooperative-home'),
    path('farmer-registration', views.farmerRegistration, name='cooperative-farmer-registration'),
    path('cooperative-manage-farmers', views.cooperativeFarmersView, name='cooperative-manage-farmers'),
    path('farmer-deletion/<str:pk>/', views.farmerDeletion, name = 'cooperative-delete-farmer'),
    path('farmer-update/<str:pk>/', views.farmerUpdate, name = 'cooperative-update-farmer'),


    path('logout/', views.cooperativeLogout, name='logout'),
    path('logout-admin/', views.adminLogout, name='logout-admin'),


    # Other URL patterns
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='base/registration/custom_password_reset_form.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='base/registration/custom_password_reset_done.html'), name='password_reset_done'),    
    path('password-reset/confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='base/registration/custom_password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(template_name = 'base/registration/custom_password_reset_complete.html'), name='password_reset_complete'),

]

