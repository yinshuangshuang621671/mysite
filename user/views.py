from django.shortcuts import render_to_response, render, redirect
from django.contrib import auth
from django.urls import reverse
# 用户登录使用django自带的forms表单类
from .forms import LoginForm, RegForm, ChangeNicknameForm, BindEmailForm, ChangePasswordForm, ForgotPasswordForm
from django.contrib.auth.models import User
from .models import Profile
from django.http import JsonResponse
# 向邮箱发送验证码的相关设置
from django.core.mail import send_mail
# 下面两个用于随机生成验证码
import string
import random

import time


# 未登录，进行登录操作
def login(request):
    # get函数：按字段获取，获取不到设置为返回空值
    # username = request.POST.get('username', '')
    # password = request.POST.get('password', '')
    # # django自带：未登录，进行登录操作，用户认证
    # user = auth.authenticate(request, username=username, password=password)
    #
    # # 获取到你是从哪个页面传递过来的请求，信息包含在request中
    # # 如果获取到就跳转到提交请求的页面，没有获取到就跳转到首页
    # referer = request.META.get('HTTP_REFERER', reverse('home'))
    # if user is not None:
    #     # 添加用户并登录,request信息中就会包含这个用户
    #     auth.login(request, user)
    #     # redirect :页面跳转方法，这里跳转到首页  home.html
    #     # 就可以直接跳转到你请求时候的页面
    #     return redirect(referer)
    # else:
    #     return render(request, 'error.html', {'message': '用户名或者密码不正确'})
    # 1. 用户登录 POST请求
    if request.method == 'POST':
        # 实例化表单，进行预先填充，先背吧
        login_form = LoginForm(request.POST)

        # 表单验证，默认先调用类中clean函数，返回验证后的数据
        if login_form.is_valid():
            # print("开始")
            user = login_form.cleaned_data['user']
            if user is not None:
                auth.login(request, user)
                return redirect(request.GET.get('from', reverse('home')))
    # 2. GET请求
    else:
        login_form = LoginForm()

    context = {}
    context['login_form'] = login_form
    return render(request, 'user/login.html', context)


# 点赞时未登录的时候弹出登录模态框，进行登录操作
def login_for_modal(request):
    login_form = LoginForm(request.POST)
    data = {}
    # 表单验证，默认先调用类中clean函数，返回验证后的数据
    if login_form.is_valid():
        user = login_form.cleaned_data['user']
        if user is not None:
            auth.login(request, user)
            data['status'] = 'SUCCESS'
        else:
            data['status'] = 'ERROR'
    return JsonResponse(data)


# 退出登录
def logout(request):
    auth.logout(request)
    # 重定向
    return redirect(request.GET.get('from', reverse('home')))


# 注册
def register(request):
    if request.method == 'POST':
        # 实例化表单，进行预先填充，先背吧
        reg_form = RegForm(request.POST, request=request)
        # 表单验证，默认先调用类中clean函数，返回验证后的数据
        if reg_form.is_valid():
            username = reg_form.cleaned_data['username']
            password = reg_form.cleaned_data['password']
            email = reg_form.cleaned_data['email']
            # 创建用户并保存（两种方法）
            user = User.objects.create_user(username, email, password)
            user.save()

            # 清除session
            del request.session['register_code']

            # 用户验证 并 进行登录
            user = auth.authenticate(username=username, password=password)
            auth.login(request, user)
            # 重定向到之前的页面
            return redirect(request.GET.get('from', reverse('home')))

    # 2. GET请求
    else:
        reg_form = RegForm()

    context = {}
    context['reg_form'] = reg_form
    return render(request, 'user/register.html', context)


# 个人信息展示
def user_info(request):
    context = {}
    return render(request, 'user/user_info.html', context)


# 修改昵称
def change_nickname(request):
    # 重定向地址，回到来的时候的页面
    redirect_to = request.GET.get('from', reverse('home'))

    if request.method == 'POST':
        form = ChangeNicknameForm(request.POST, user=request.user)
        if form.is_valid():
            nickname_new = form.cleaned_data['nickname_new']
            profile, created = Profile.objects.get_or_create(user=request.user)
            profile.nickname = nickname_new
            profile.save()
            return redirect(redirect_to)

    else:
        # 实例化表单
        form = ChangeNicknameForm()

    context = {}
    context['page_title'] = '修改昵称'
    context['form_title'] = '修改昵称'
    context['submit_text'] = '修改'
    context['form'] = form
    # 点击返回按钮，不修改直接返回上一个页面，地址从这里传入
    context['return_back_url'] = redirect_to
    return render(request, 'form.html', context)


# 绑定邮箱
def bind_email(request):
    redirect_to = request.GET.get('from', reverse('home'))

    if request.method == 'POST':
        form = BindEmailForm(request.POST, request=request)

        if form.is_valid():
            email = form.cleaned_data['email']
            request.user.email = email
            request.user.save()

            # 操作成功后，清除session
            del request.session['bind_email_code']
            return redirect(redirect_to)
    else:
        form = BindEmailForm()

    context = {}
    context['page_title'] = '绑定邮箱'
    context['form_title'] = '绑定邮箱'
    context['submit_text'] = '绑定'
    context['form'] = form
    # 不修改直接返回上一个页面，地址从这里传入
    context['return_back_url'] = redirect_to
    # 使用通用的form.html模板页面
    return render(request, 'user/bind_email.html', context)


# 发送验证码，处理方法
def send_verification_code(request):
    data = {}
    # 绑定邮箱及注册都需要发送验证码，从前端页面传递来区分是哪一种情况
    send_for = request.GET.get('send_for', '')
    # 获取到要绑定的邮箱
    email = request.GET.get('email', '')

    if email != '':
        # 生成验证码,string.ascii_letters:所有字母，string.digits：所有数字
        # 验证码为四个单个字符合成的字符串
        # 使用jion函数将四个单个字符变成一整个字符串
        code = ''.join(random.sample(string.ascii_letters + string.digits, 4))
        now = int(time.time())
        send_code_time = request.session.get('send_code_time', 0)

        if now - send_code_time < 30:
            data['status'] = 'ERROR'
        else:
            # 将验证码存储到session中，session默认有效期为两个星期，是存储在服务器端
            # 存储生成code的时间，两次生成的code之间间隔不能少于30秒
            request.session[send_for] = code
            request.session['send_code_time'] = now

            # 发送验证码邮件，使用django自带的函数send_email()
            send_mail(
                '绑定邮箱',  # 邮件主题
                '验证码: %s' % code,
                '2462971145@qq.com',  # 发件人邮箱
                [email],  # 收件人邮箱
                fail_silently=False,  # 是否忽略相关错误，默认否
            )
            data['status'] = 'SUCCESS'
    else:
        data['statue'] = 'ERROR'
    return JsonResponse(data)


# 修改密码
def change_password(request):
    redirect_to = reverse('home')
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST, user=request.user)
        if form.is_valid():
            user = request.user
            old_password = form.cleaned_data['old_password']
            new_password = form.cleaned_data['new_password']
            # 使用函数设置新密码，而不是直接赋值，不然无法加密！！
            user.set_password(new_password)
            user.save()
            # 修改完密码后，退出登录
            auth.logout(request)
            # 返回首页即可
            return redirect(redirect_to)
    else:
        # 实例化表单
        form = ChangePasswordForm()

    context = {}
    context['page_title'] = '修改密码'
    context['form_title'] = '修改密码'
    context['submit_text'] = '修改'
    context['form'] = form
    # 点击返回按钮，不修改直接返回上一个页面，地址从这里传入
    context['return_back_url'] = redirect_to
    # 使用通用模板页面
    return render(request, 'form.html', context)


# 重置密码，根据绑定过的邮箱
def forgot_password(request):
    redirect_to = reverse('home')
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST, request=request)

        if form.is_valid():
            email = form.cleaned_data['email']
            new_password = form.cleaned_data['new_password']

            user = User.objects.filter(email=email)
            user.set_password(new_password)
            user.save()

            # 操作成功后，清除session
            del request.session['forgot_password_code']
            return redirect(redirect_to)
    else:
        form = ForgotPasswordForm()

    context = {}
    context['page_title'] = '重置密码'
    context['form_title'] = '重置密码'
    context['submit_text'] = '重置'

    context['form'] = form
    # 返回按钮：不修改直接返回上一个页面，地址从这里传入
    context['return_back_url'] = redirect_to
    # 使用通用的form.html模板页面
    return render(request, 'user/forgot_password.html', context)


"""
1. session与cookie的区别
（1）
"""

"""
2. 在注册完成及邮箱绑定完成后，清除session，不然就只要你输入的验证码与
session中的一致（在forms表单中判断的），你就可以一直注册，这是个隐藏的bug
# 清除session
del request.session['register_code']

"""