from django.urls import path
from . import views

urlpatterns = [
    path('', views.getRoutes),
    path('login/',views.user_login),
    path('logout/',views.logout),
    path('register-batch/', views.register_batch, name='register-batch'),
    path('update-batch/<str:pk>/', views.update_batch, name='update-batch'),
]