from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib.auth import authenticate, login,logout
from django.shortcuts import redirect

# Create your views here.
def user_login(request):
    if request.method=='GET':
        try:
            next=request.GET['next']
        except:
            next=reverse('main:query')
        return render(request,'account/login.html',{'error_message':'','next':next})
    elif request.method=='POST':
        username=request.POST['username']
        password=request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request,user)
            return redirect(request.POST['next'])
        else:
            return render(request,'account/login.html',{'error_message':'登录失败，请重试','next':request.POST['next']})

@login_required
def user_logout(request):
    logout(request)
    return redirect(reverse('account:login'))

# Create your views here.
