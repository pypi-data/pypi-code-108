from django.shortcuts import render, redirect
from .forms import CreateUserForm
from django.contrib.auth import authenticate, login, logout
from django.views.generic import TemplateView

class index(TemplateView):
    template_name = 'app/index.html'

class about(TemplateView):
    template_name = 'app/about.html'

class signup(TemplateView):
    template_name = 'app/signup.html'
    def get(self, request):
        if request.user.is_authenticated:
            return render(request, "app/index.html")
        form = CreateUserForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return render(request, "app/thanks.html", {'form': form})

        return render(request, self.template_name, {'form': form})

class loginPage(TemplateView):
    template_name = 'app/login.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('index')
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            return render(request, self.template_name, {'error_message': 'Username or password is incorrect'})

class logoutPage(TemplateView):
    template_name = 'app/logout.html'

    def get(self, request):
        logout(request)
        return redirect('index')