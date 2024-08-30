from django.urls import path
from . import views

from django.urls import path
from .views import register

urlpatterns = [
    path('', views.index, name='index'), #收支记账主页面
    path('login/', views.login_in, name='login_in'),  # 登录
    path('register/', register, name='register'),
    path('charts/', views.charts_view, name='charts_view'),
    path('logout/', views.logout_, name='logout_'),
    path('retrieve_category/', views.retrieve_category, name='retrieve_category'),
    path('retrieve_subcategory/', views.retrieve_subcategory, name='retrieve_subcategory'),
    path('record_income_expense/', views.record_income_expense, name='record_income_expense'),
]