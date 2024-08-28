from django.shortcuts import render
from django.http import HttpResponse
from .models import *

def index(request):
    all_accounts = Account.objects.all()
    sub_categories = SubCategory.objects.all()
    context = {
        'accounts': all_accounts,
        'sub_categories': sub_categories
    }
    print(context)
    return  render(request, 'accounting/index.html', context)
def login(request):
    return  render(request, 'accounting/login.html')