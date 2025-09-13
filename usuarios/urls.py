from django.urls import path
from . import views

app_name = "usuarios"

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_adoptante, name='register'),
    path('login/', views.login_adoptante, name='login'),
    path('logout/', views.logout_adoptante, name='logout'),
]