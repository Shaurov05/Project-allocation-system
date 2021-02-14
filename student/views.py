from django.shortcuts import render, redirect, get_object_or_404

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
from django.utils.text import slugify

from .forms import StudentForm, StudentProfileInfoForm
from .models import Student
from department.models import Department

@login_required
def StudentLogoutView(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


def student_register(request):
    registered = False

    if request.method == 'POST':
        student_form = StudentForm(data=request.POST)
        student_profile_form = StudentProfileInfoForm(data=request.POST)

        if student_form.is_valid() and student_profile_form.is_valid():
            # Save User Form to Database
            user = student_form.save()

            # Hash the password
            user.set_password(user.password)
            # Update with Hashed password
            user.save()

            # Now we deal with the extra info!
            # Can't commit yet because we still need to manipulate
            student_profile = student_profile_form.save(commit=False)
            student_profile.created_by = request.user
            # Set One to One relationship between
            # StudentForm and StudentProfileInfoForm
            student_profile.user = user

            if 'profile_pic' in request.FILES:
                student_profile.profile_pic = request.FILES['profile_pic']

            # now saving the model
            student_profile.save()
            registered = True

            name = request.POST.get('username')
            dept_id=request.POST.get('department')
            # get_object_or_404(Group,slug=self.kwargs.get("slug"))
            department = get_object_or_404(Department, pk=dept_id)
            from django.utils.text import slugify
            student_slug = slugify(name)
            dept_slug = slugify(department.name)
            # print("\n\n****department: {} and student: {}***/n/n".format(dept_slug, student_slug))

            return HttpResponseRedirect(reverse('students:student_detail', kwargs={'department_slug':dept_slug, 'student_slug':student_slug}))
        else:
            print(student_form.errors, student_profile_form.errors)
            return render(request, 'student/student_registration.html', {
                'user_form': user_form,
                'profile_form': student_profile_form,
                'user_form_errors': student_form.errors,
                'student_profile_form_errors': student_profile_form.errors
            })
    else:
        student_form = StudentForm()
        student_profile_form = StudentProfileInfoForm()

    return render(request, "student/student_registration.html",context={
                    'student_form':student_form,
                    'student_profile_form':student_profile_form,
                    'registered':registered})


def student_login(request):
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
        return render(request, 'student/login.html',{})


@login_required
def change_password(request):
    if request.mathod == 'POST':
        form = PasswordChangeForm(request.user, request.POST)

        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Your password is changed!")
            logout(request)
            return redirect('user_login')
        else:
            messages.error(request, "Please provide valid information")
    else:
        form = PasswordChangeForm()
    return render(request, 'student/change_password.html',{
                            'form':form})


class StudentDetailView(SelectRelatedMixin, DetailView):
    select_related = ("user", "department")
    context_object_name = 'student_detail'
    model = Student
    template_name = 'student/student_detail.html'

    def get_object(self, **kwargs):
        return get_object_or_404(
            Student,
            student_slug=self.kwargs['student_slug']
        )


class StudentList(SelectRelatedMixin, ListView):
    model = Student
    select_related = ("user", "department")

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['slug'] = self.kwargs['slug']
    #     # context['current_month'] = self.current_month
    #     return context


def getForms(request, student_slug):
    if request.method == 'POST':
        if not request.user.is_superuser:
            user_form = StudentForm(request.POST, instance=request.user)
            student_profile_form = StudentProfileInfoForm(request.POST, instance=request.user.student)
            department_slug = request.user.student.department.department_slug
            return user_form, student_profile_form, department_slug
        else:
            print("admin")
            student = Student.objects.get(student_slug=student_slug)
            user_form = StudentForm(request.POST, instance=student.user)
            student_profile_form = StudentProfileInfoForm(request.POST, instance=student)
            department_slug = student.department.department_slug
            return user_form, student_profile_form, department_slug
    else:
        if not request.user.is_superuser:
            user_form = StudentForm( instance=request.user)
            student_profile_form = StudentProfileInfoForm(instance=request.user.student)
            return user_form, student_profile_form
        else:
            print("admin")
            student = Student.objects.get(student_slug=student_slug)
            user_form = StudentForm( instance=student.user)
            student_profile_form = StudentProfileInfoForm( instance=student)
            return user_form, student_profile_form


from django.db import transaction
@login_required
@transaction.atomic
def update_student_profile(request, student_slug):

    if request.method == 'POST':
        user_form, student_profile_form, department_slug = getForms(request, student_slug=student_slug)

        if user_form.is_valid() and student_profile_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])

            student_profile_form.save(commit=False)
            student_profile.updated_by = request.user

            user.save()
            student_profile.save()

            messages.success(request, ('Your profile is successfully updated!'))
            return redirect(reverse('students:student_detail', kwargs={
                                    'student_slug': student_slug,
                                    'department_slug': department_slug}))
        else:
            messages.error(request, ('Please check the error below.'))
            user_form, student_profile_form, department_slug = getForms(request, student_slug=student_slug)

            user_form_errors = user_form.errors
            student_profile_form_errors = student_profile_form.errors
            return render(request, 'student/profileupdate_form.html', {
                'user_form': user_form,
                'profile_form': student_profile_form,
                'user_form_errors':user_form_errors,
                'student_profile_form_errors':student_profile_form_errors
            })
    else:
        user_form, student_profile_form = getForms(request, student_slug=student_slug)

    return render(request, 'student/profileupdate_form.html', {
        'user_form': user_form,
        'profile_form': student_profile_form,
    })


class StudentDeleteView(LoginRequiredMixin,SelectRelatedMixin, DeleteView):
    login_url = '/login/options/'
    # redirect_field_name = 'blog/post_detail.html'
    model = Student

    def get_object(self, **kwargs):
        return Student.objects.get(student_slug=self.kwargs['student_slug'])

    def get_success_url(self):
          # if you are passing 'slug' from 'urls' to 'DeleteView' for student
          # capture that 'slug' as dept_slug and pass it to 'reverse_lazy()' function
          dept_slug = self.kwargs['department_slug']
          student = self.get_object()
          user = student.user
          logout(self.request)
          user.delete()
          # self.StudentLogoutView()
          return reverse('departments:department_students', kwargs={
                                    'department_slug': dept_slug,})



class all_students(ListView):
    model = Student
    context_object_name = 'students'
    template_name = 'student/all_students.html'
