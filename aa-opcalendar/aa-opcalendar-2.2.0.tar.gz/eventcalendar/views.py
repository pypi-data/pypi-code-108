from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from opcalendar.forms import SignupForm


def signup(request):
    forms = SignupForm()
    if request.method == "POST":
        forms = SignupForm(request.POST)
        if forms.is_valid():
            username = forms.cleaned_data["username"]
            password = forms.cleaned_data["password"]
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return redirect("opcalendar:calendar")
    context = {"form": forms}
    return render(request, "signup.html", context)


def user_logout(request):
    logout(request)
    return redirect("signup")
