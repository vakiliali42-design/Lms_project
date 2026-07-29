from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, LoginForm, ProfileUpdateForm

def register_view(request):
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "ثبت‌ نام موفق")
        return redirect('dashboard')
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    form = LoginForm(request.POST or None)
    if form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect("dashboard")
    return render(request, 'accounts/login.html' , {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def profile_view(request):
    form = ProfileUpdateForm(request.POST or None, request.FILES or None, instance=request.user)
    if form.is_valid():
        form.save()
        messages.success(request, "پروفایل آپدیت شد")
        return redirect("profile")
    return render(request, "accounts/profile.html", {"form":form})

@login_required
def dashboard_view(request):
    return render(request, "accounts/dashboard.html")