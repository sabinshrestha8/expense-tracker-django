from django.urls import path, include
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('register', user_register, name='register'),
    path('login', user_login, name='login'),
    path('logout', user_logout, name='logout'),
    path('update_profile', update_profile, name='update_profile'),
    path('budget_profile', budget_profile, name='budget_profile'),
    path('update_budget_profile', update_budget_profile, name='update_budget_profile'),
    path('verify', verify_otp, name='verify_otp')
]