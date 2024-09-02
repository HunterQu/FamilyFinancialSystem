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
    path('transfer_between_accounts/', views.transfer_between_accounts, name='transfer_between_accounts'),
    path('retrieve_year_has_data/', views.retrieve_year_has_data, name='retrieve_year_has_data'),
    path('retrieve_month_has_data/', views.retrieve_month_has_data, name='retrieve_month_has_data'),
    path('filter_record_by_date/', views.filter_record_by_date, name='filter_record_by_date'),
    path('transfer-between-accounts/', views.transfer_between_accounts, name='transfer_between_accounts'),
    path('search_record/', views.search_record, name='search_record'),
]