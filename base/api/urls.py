from django.urls import path
from . import views

urlpatterns = [
    path('', views.getRoutes),
    path('login/',views.user_login),
    path('get-user/',views.get_user),
    path('logout/',views.logout_user),
    path('register-batch/', views.register_batch, name='register-batch'),
    path('register-buyer/', views.register_buyer, name='register-buyer'),
    path('get-batch/<str:batch_string>/', views.get_batch, name='get-batch'),
    path('batch-exporter-update/', views.batch_exporter_update, name='batch-exporter-update'),
    path('batch-buyer-update/', views.batch_buyer_update, name='batch-buyer-update'),
]