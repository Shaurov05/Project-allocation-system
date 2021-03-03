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


def teacher_register(request):
    registered = False

    if request.method == 'POST':
        # if the user submits forms, then we pass the informations
        # to those forms to check if the forms are valid or not
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
            # we assign the user to teacher model
            teacher_profile.user = user

            if not request.user.is_anonymous:
                # if the user is authenticated, then we assign the user as the creator
                print(request.user)
                teacher_profile.created_by = request.user

            if 'profile_pic' in request.FILES:
                # if a profile picture is uploaded by the user, we set the picture as profile picture
                teacher_profile.profile_pic = request.FILES['profile_pic']

            # at last we saving the information to the database
            user.save()
            teacher_profile.save()

            name = request.POST.get('username')
            dept_id=request.POST.get('department')

            # we get the department to get the department_slug
            # we user department slug to redirect the user to the profile page
            department = get_object_or_404(Department, pk=dept_id)
            from django.utils.text import slugify
            teacher_slug = slugify(name)
            dept_slug = slugify(department.name)
            print("\n\n****department: {} and teacher: {}***/n/n".format(dept_slug, teacher_slug))

            return HttpResponseRedirect(reverse('teachers:teacher_detail',
                                kwargs={'department_slug': dept_slug,
                                        'teacher_slug': teacher_slug}))
        else:
            # if any of the forms are not valid, we show the errors to the user
            print(teacher_form.errors, teacher_profile_form.errors)
            return render(request, "teachers/teacher_registration.html",
                          { 'registered': registered,
                            'teacher_form': teacher_form,
                            'teacher_profile_form': teacher_profile_form,
                            'teacher_form_errors': teacher_form.errors,
                            'teacher_profile_form_errors': teacher_profile_form.errors})
    else:
        # if the user wants to create a user, then we simply pass the forms
        teacher_form = TeacherForm()
        teacher_profile_form = TeacherProfileInfoForm()

    return render(request, "teachers/teacher_registration.html", context={
                    'teacher_form':teacher_form,
                    'teacher_profile_form':teacher_profile_form,
                    'registered':registered})


class TeacherDetailView(SelectRelatedMixin, DetailView):
    select_related = ("user", "department")
    context_object_name = 'teacher_detail'
    model = Teacher
    template_name = 'teachers/teacher_detail.html'

    # we get the particular teacher from the database
    def get_object(self, **kwargs):
        return get_object_or_404(
            Teacher,
            teacher_slug=self.kwargs['teacher_slug']
            # access_key=self.kwargs['access_key'],
        )


class TeacherList(SelectRelatedMixin, ListView):
    model = Teacher
    select_related = ("user", "department")


from student.views import getForms
from django.db import transaction
@login_required
@transaction.atomic
def update_teacher_profile(request, teacher_slug):

    if request.method == 'POST':
        # if the user submits forms, we get the data sent by the user
        user_form, teacher_profile_form, department_slug = getForms(request, model=Teacher,
                                                                slug_instance=teacher_slug, UserForm=TeacherForm,
                                                                UserProfileInfoForm=TeacherProfileInfoForm)

        # checking if the forms are valid or not.
        if user_form.is_valid() and teacher_profile_form.is_valid():
            # we don't save the user as we need to hash the password
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])

            teacher_profile_form.save(commit=False)
            # we save the user who is updating the profile
            teacher_profile_form.updated_by = request.user

            user.save()
            teacher_profile_form.save()

            # after saving information in database we send a success message
            messages.success(request, ('Your profile is successfully updated!'))
            return redirect(reverse('teachers:teacher_detail', kwargs={
                                    'teacher_slug': teacher_slug,
                                    'department_slug': department_slug}))
        else:
            # if the forms are not valid we send an error message
            # and show the errors to the user
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
        # if the user want to update his profile,
        # we send forms containing previous data
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

    # we get the teacher object from the database
    def get_object(self, **kwargs):
        return Teacher.objects.get(teacher_slug=self.kwargs['teacher_slug'])

    def get_success_url(self):
          # we pass 'department_slug' field from 'urls' to 'DeleteView' for teacher
          # we redirect the user to department teachers page
          # by passing the slug field to 'reverse_lazy()' function
          dept_slug = self.kwargs['department_slug']

          teacher = self.get_object()
          user = teacher.user
          logout(self.request)
          user.delete()
          return reverse_lazy('departments:department_teachers', kwargs={
                                    'department_slug': dept_slug, })


class AllTeachers(ListView):
    # gets all the teachers from the database
    model = Teacher
    context_object_name = "teachers"
    template_name = 'teachers/all_teachers.html'




#
