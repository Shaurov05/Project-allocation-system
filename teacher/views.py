from django.shortcuts import render, redirect,get_object_or_404

# Extra Imports for the Login and Logout Capabilities
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from PIL import Image
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

from django.views.generic import (TemplateView,ListView,View,
                                  DetailView,CreateView,
                                  UpdateView,DeleteView)

from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from braces.views import SelectRelatedMixin

from django.forms import ModelForm
from extra_views import CreateWithInlinesView, UpdateWithInlinesView, InlineFormSetFactory

from .forms import TeacherForm, TeacherProfileInfoForm
from .models import Teacher
from department.models import Department

@login_required
def TeacherLogoutView(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


def teacher_register(request):
    registered = False

    if request.method == 'POST':
        teacher_form = TeacherForm(data=request.POST)
        teacher_profile_form = TeacherProfileInfoForm(data=request.POST)

        if teacher_form.is_valid() and teacher_profile_form.is_valid():
            # Save User Form to Database
            user = teacher_form.save()

            # Hash the password
            user.set_password(user.password)

            # Now we deal with the extra info!
            # Can't commit yet because we still need to manipulate
            teacher_profile = teacher_profile_form.save(commit=False)
            # Set One to One relationship between
            # TeacherForm and TeacherProfileInfoForm
            teacher_profile.user = user

            if not request.user.is_anonymous:
                print(request.user)
                teacher_profile.created_by = request.user

            if 'profile_pic' in request.FILES:
                teacher_profile.profile_pic = request.FILES['profile_pic']

            # now saving the model
            user.save()
            teacher_profile.save()
            registered = True

            name = request.POST.get('username')
            dept_id=request.POST.get('department')
            # get_object_or_404(Group,slug=self.kwargs.get("slug"))
            department = get_object_or_404(Department, pk=dept_id)
            from django.utils.text import slugify
            teacher_slug = slugify(name)
            dept_slug = slugify(department.name)
            print("\n\n****department: {} and teacher: {}***/n/n".format(dept_slug, teacher_slug))

            return HttpResponseRedirect(reverse('teachers:teacher_detail',
                                kwargs={'department_slug': dept_slug,
                                        'teacher_slug': teacher_slug}))
        else:
            print(teacher_form.errors, teacher_profile_form.errors)
            return render(request, "teachers/teacher_registration.html",
                          { 'registered': registered,
                            'teacher_form': teacher_form,
                            'teacher_profile_form': teacher_profile_form,
                            'teacher_form_errors': teacher_form.errors,
                            'teacher_profile_form_errors': teacher_profile_form.errors})
    else:
        teacher_form = TeacherForm()
        teacher_profile_form = TeacherProfileInfoForm()

    return render(request, "teachers/teacher_registration.html", context={
                    'teacher_form':teacher_form,
                    'teacher_profile_form':teacher_profile_form,
                    'registered':registered})


def teacher_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        # Django's built-in authentication function:
        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('index'))
            else:
                # If account is not active:
                return HttpResponse("Your account is not active.")

        else :
            print('Invalid Username: {} and password: {} is provided'.format(username, password))
            return HttpResponse("Invalid username or password supplied!")
    else:
        return render(request, 'teachers/login.html',{})


@login_required
def change_password(request):
    if request.mathod == 'POST':
        form = PasswordChangeForm(request.user, request.POST)

        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Your password is changed!")
            logout(request)
            return redirect('teachers:teacher_login')
        else:
            messages.error(request, "Please provide valid information")
    else:
        form = PasswordChangeForm(request, request.user)
    return render(request, 'teachers/change_password.html',{
                            'form':form})


class TeacherDetailView(SelectRelatedMixin, DetailView):
    select_related = ("user", "department")
    context_object_name = 'teacher_detail'
    model = Teacher
    template_name = 'teachers/teacher_detail.html'

    def get_object(self, **kwargs):
        return get_object_or_404(
            Teacher,
            teacher_slug=self.kwargs['teacher_slug']
            # access_key=self.kwargs['access_key'],
        )


class TeacherList(SelectRelatedMixin, ListView):
    model = Teacher
    select_related = ("user", "department")

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['slug'] = self.kwargs['slug']
    #     # context['current_month'] = self.current_month
    #     return context


from student.views import getForms
from django.db import transaction
@login_required
@transaction.atomic
def update_teacher_profile(request, teacher_slug):

    if request.method == 'POST':
        user_form, teacher_profile_form, department_slug = getForms(request, model=Teacher,
                                                                slug_instance=teacher_slug, UserForm=TeacherForm,
                                                                UserProfileInfoForm=TeacherProfileInfoForm)

        if user_form.is_valid() and teacher_profile_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])

            teacher_profile_form.save(commit=False)
            teacher_profile_form.updated_by = request.user

            user.save()
            teacher_profile_form.save()

            messages.success(request, ('Your profile is successfully updated!'))
            return redirect(reverse('teachers:teacher_detail', kwargs={
                                    'teacher_slug': teacher_slug,
                                    'department_slug': department_slug}))
        else:
            messages.error(request, ('Please check the error below.'))
            user_form_errors = user_form.errors
            teacher_profile_form_errors = teacher_profile_form.errors
            return render(request, 'teachers/profileupdate_form.html', {
                'user_form': user_form,
                'profile_form': teacher_profile_form,
                'user_form_errors':user_form_errors,
                'teacher_profile_form_errors':teacher_profile_form_errors
            })
    else:
        user_form, ProfileInfoForm = getForms(request, model=Teacher,
                                                        slug_instance=teacher_slug, UserForm=TeacherForm,
                                                        UserProfileInfoForm=TeacherProfileInfoForm)

    return render(request, 'teachers/profileupdate_form.html', {
        'user_form': user_form,
        'profile_form': ProfileInfoForm,
    })


class TeacherDeleteView(LoginRequiredMixin,SelectRelatedMixin, DeleteView):
    login_url = '/teacher/login/'
    template_name = 'teachers/teacher_confirm_delete.html'
    model = Teacher
    select_related = ("user", "department")

    def get_object(self, **kwargs):
        return Teacher.objects.get(teacher_slug=self.kwargs['teacher_slug'])

    def get_success_url(self):
          # if you are passing 'slug' from 'urls' to 'DeleteView' for teacher
          # capture that 'slug' as dept_slug and pass it to 'reverse_lazy()' function
          dept_slug = self.kwargs['department_slug']
          teacher_slug = self.kwargs['teacher_slug']

          teacher = self.get_object()
          user = teacher.user
          logout(self.request)
          user.delete()
          return reverse_lazy('departments:department_teachers', kwargs={
                                    'department_slug': dept_slug, })



class AllTeachers(ListView):
    model = Teacher
    context_object_name = "teachers"
    template_name = 'teachers/all_teachers.html'




#
