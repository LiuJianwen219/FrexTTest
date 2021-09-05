from django.shortcuts import render, redirect
from Login import forms
from Login.models import User


# Create your views here.


def login(request):
    # if not request.session.get('is_login', None):
    #     return redirect('/home/introduce/') # 不允许重复登录
    if request.method == 'POST':
        login_form = forms.LoginForm(request.POST)
        # message = '请检查填写的内容！'
        # print(message)
        if login_form.is_valid():
            username = login_form.cleaned_data.get('username')
            password = login_form.cleaned_data.get('password')
            print(username, password)
            try:
                user = User.objects.get(name=username)
            except:
                message = '用户不存在'
                return render(request, "Login/login.html", locals())

            if user.password == password:
                user.login_count += 1
                user.save()
                request.session['is_login'] = True
                request.session['u_uid'] = str(user.uid)
                request.session['user_name'] = user.name
                request.session['role'] = user.role
                return redirect('/')
            else:
                message = '密码错误'
                return render(request, "Login/login.html", locals())
        else:
            return render(request, "Login/login.html", locals())
    login_form = forms.LoginForm()
    return render(request, "Login/login.html", locals())


def register(request):
    # if not request.session.get('is_login', None):
    #     return redirect('/home/introduce/') # 不允许重复登录
    if request.method == 'POST':
        register_form = forms.RegisterForm(request.POST)
        # message = "请检查填写的内容！"
        if register_form.is_valid():
            username = register_form.cleaned_data.get('username')
            password1 = register_form.cleaned_data.get('password1')
            password2 = register_form.cleaned_data.get('password2')
            email = register_form.cleaned_data.get('email')

            if password1 != password2:
                message = '两次输入的密码不同！'
                return render(request, 'Login/register.html', locals())
            else:
                same_name_user = User.objects.filter(name=username)
                if same_name_user:
                    message = '用户名已经存在'
                    return render(request, 'Login/register.html', locals())
                same_email_user = User.objects.filter(email=email)
                if same_email_user:
                    message = '该邮箱已经被注册了'
                    return render(request, 'Login/register.html', locals())

                new_user = User()
                new_user.name = username
                new_user.password = password1
                new_user.email = email
                new_user.role = 'undefined'
                new_user.save()
                return redirect('/login/')
        else:
            return render(request, 'Login/register.html', locals())
    register_form = forms.RegisterForm()
    return render(request, 'Login/register.html', locals())


def logout(request):
    request.session.flush()
    # 或者使用下面的方法
    # del request.session['is_login']
    # del request.session['user_name']
    # del request.session['role']
    return redirect("/")


def find_password(request):
    return render(request, "building.html")
