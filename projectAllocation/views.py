from django.shortcuts import render

# Extra Imports for the Login and Logout Capabilities
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from django.views.generic import (TemplateView,ListView,View,
                                  DetailView,CreateView,
                                  UpdateView,DeleteView)

from django.contrib import messages


class ErrorTemplateView(TemplateView):

    def get_template_names(self):
        template_name = "error.html"
        return template_name


class RegistrationOptionsPage(TemplateView):
    template_name = 'registration_options.html'


class LogoutPage(TemplateView):
    template_name = 'thanks.html'


class IndexPage(TemplateView):
    template_name = 'index.html'


@login_required
def user_logout(request):
    # Log out the user.
    logout(request)
    # Return to homepage.
    return HttpResponseRedirect(reverse('thanks'))


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('index'))
            else:
                return HttpResponse("Your account is not active.")
        else:
            print('Someone tried to login and failed')
            print('He used username: {} and password : {}'.format(username, password))
            # return HttpResponse("Invalid login details supplied!")
            messages.success(request, "Invalid login details supplied!")
            return render(request, 'user_login.html')
    else:
        return render(request, 'user_login.html')
