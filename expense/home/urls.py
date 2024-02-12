from django.urls import path, include
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('register', user_register, name='register'),
    path('login', user_login, name='login'),
    path('logout', user_logout, name='logout')
]