from django.urls import path
from . import views

from django.urls import path
from .views import register

urlpatterns = [
    path('', views.index, name='index'), #收支记账主页面
    path('login/', views.login_in, name='login_in'),  # 登录
    path('register/', register, name='register'),
    path('logout/', views.logout_, name='logout_'),
    path('retrieve_category/', views.retrieve_category, name='retrieve_category'),
]