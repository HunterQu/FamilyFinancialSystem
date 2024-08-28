from django.urls import path
from . import views

from django.urls import path
from .views import register

urlpatterns = [
    path('', views.index, name='index'), #收支记账主页面
    path('login/', views.login, name='login'),
    path('register/', register, name='register'),
]