from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login

#注册
def register(request):
    if request.method == 'GET':
        return render(request, 'basic/register.html')

    elif request.method == 'POST':
        user_name = request.POST.get('username', '')
        email = request.POST.get('email', '')
        pwd = request.POST.get('password', '')

        if User.objects.filter(username=user_name).exists():
            return JsonResponse({'code': 200, 'msg': '用户已存在'})

        user = User.objects.create_user(username=user_name, password=pwd, email=email)
        user.save()

        return JsonResponse({'code': 200, 'msg': '用户注册成功'})

    return JsonResponse({'code': 403, 'msg': '被禁止的请求'})


def index(request):
    return  render(request, 'accounting/index.html')
def login(request):
    return  render(request, 'accounting/login.html')