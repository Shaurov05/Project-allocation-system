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
from teacher.models import Teacher
from department.models import Department


def student_register(request):
    registered = False

    if request.method == 'POST':
        # collecting the information sent
        student_form = StudentForm(data=request.POST)
        student_profile_form = StudentProfileInfoForm(data=request.POST)

        if student_form.is_valid() and student_profile_form.is_valid():
            # Save User Form to Database
            user = student_form.save()

            # Hash the password so that no one can see the password, not even the admin
            user.set_password(user.password)

            # Now we deal with the extra info!
            # Can't commit yet because we still need to manipulate
            student_profile = student_profile_form.save(commit=False)

            if not request.user.is_anonymous:
                student_profile.created_by = request.user
            # Set One to One relationship between
            # StudentForm and StudentProfileInfoForm
            student_profile.user = user

            if 'profile_pic' in request.FILES:
                student_profile.profile_pic = request.FILES['profile_pic']

            # now saving the models
            user.save()
            student_profile.save()

            name = request.POST.get('username')
            dept_id=request.POST.get('department')

            # getting the department where the student belongs
            department = get_object_or_404(Department, pk=dept_id)
            from django.utils.text import slugify
            student_slug = slugify(name)
            # converting the name into slug field, so that we can use this field to
            # generate url for student detail page
            dept_slug = slugify(department.name)

            return HttpResponseRedirect(reverse('students:student_detail', kwargs={'department_slug':dept_slug, 'student_slug':student_slug}))
        else:
            print(student_form.errors, student_profile_form.errors)
            # if the form is not valid, shows the error to the user
            return render(request, 'student/student_registration.html', {
                'student_form': student_form,
                'student_profile_form': student_profile_form,
                'user_form_errors': student_form.errors,
                'student_profile_form_errors': student_profile_form.errors
            })
    else:
        # if the requested method is get, then simply send empty forms to the user to fill those up.
        student_form = StudentForm()
        student_profile_form = StudentProfileInfoForm()

    return render(request, "student/student_registration.html",context={
                    'student_form':student_form,
                    'student_profile_form':student_profile_form,
                    'registered':registered})



class StudentDetailView(SelectRelatedMixin, DetailView):
    select_related = ("user", "department")
    # declaring the name of the object (student_detail) using which we can get student data.
    context_object_name = 'student_detail'
    model = Student
    template_name = 'student/student_detail.html'

    def get_object(self, **kwargs):
        # gets the particular student object, otherwise returns 404
        return get_object_or_404(
            Student,
            student_slug=self.kwargs['student_slug']
        )


from project.models import *
def student_detail_view(request, student_slug, department_slug):
    # gets the particular student object, otherwise returns 404
    student_detail = get_object_or_404(
            Student,
            student_slug=student_slug
        )

    assigned_project = student_detail.assigned_project_name
    try:
        # getting the project that is assigned to the particular student and
        # the project choices, selected by the student.
        project = Project.objects.get(name=student_detail.assigned_project_name)
        projectChoice = ProjectChoice.objects.filter(student_id=student_detail.id)
    except:
        # if no project is assigned to the student, then assign null
        project = ""
        projectChoice = ""

    try:
        requested_project = ProjectRequestProposal.objects.get(created_by=student_detail.id)
    except:
        requested_project = ""

    # print("requested_project : ", requested_project)
    return render(request, 'student/student_detail.html', context={
        'student_detail': student_detail,
        'assigned_project': assigned_project,
        'project':project,
        'projectChoice':projectChoice,
        'department_slug':department_slug,
        'student_slug':student_slug,
        'requested_project':requested_project,
    })


class StudentList(SelectRelatedMixin, ListView):
    # get all student object from database
    model = Student
    select_related = ("user", "department")


global user_profile_form
def getForms(request, model, slug_instance, UserForm, UserProfileInfoForm):
    if request.method == 'POST':
        if not request.user.is_superuser:
            # if user is student then we pass that user as the instance
            user_form = UserForm(request.POST, instance=request.user)
            if model == Student:
                # print("student")
                user_profile_form = UserProfileInfoForm(request.POST, instance=request.user.student)
                department_slug = request.user.student.department.department_slug
            else:
                # print("teacher")
                # if user is teacher then we pass that user as the instance
                user_profile_form = UserProfileInfoForm(request.POST, instance=request.user.teacher)
                department_slug = request.user.teacher.department.department_slug

            return user_form, user_profile_form, department_slug
        else:
            print("admin")
            # if the user is superuser, then we get the student and teacher model using slug field
            # collected from the url
            if model == Student:
                instance = model.objects.get(student_slug=slug_instance)
            else:
                instance = model.objects.get(teacher_slug=slug_instance)

            # now, we pass the Student/Teacher (instance.user) as instance
            user_form = UserForm(request.POST, instance=instance.user)
            profile_form = UserProfileInfoForm(request.POST, instance=instance)
            department_slug = instance.department.department_slug
            return user_form, profile_form, department_slug
    else:
        if not request.user.is_superuser:
            # if the method is get and the user is not superuser, we pass the user as instance
            user_form = UserForm(instance=request.user)
            if model == Student:
                user_profile_form = UserProfileInfoForm(instance=request.user.student)
            else:
                user_profile_form = UserProfileInfoForm(instance=request.user.teacher)

            return user_form, user_profile_form
        else:
            print("admin")
            # if the user is superuser, then we get the student and teacher model using slug field
            # collected from the url
            if model == Student:
                instance = model.objects.get(student_slug=slug_instance)
            else:
                instance = model.objects.get(teacher_slug=slug_instance)
            # now, we pass the Student/Teacher as instance
            user_form = UserForm(instance=instance.user)
            profile_form = UserProfileInfoForm(instance=instance)
            return user_form, profile_form


from django.db import transaction
@login_required
@transaction.atomic
def update_student_profile(request, student_slug):

    if request.method == 'POST':
        # collecting forms using getForms function
        user_form, student_profile_form, department_slug = getForms(request, model=Student,
                                                                    slug_instance=student_slug,
                                                                    UserForm=StudentForm,
                                                                    UserProfileInfoForm=StudentProfileInfoForm)

        if user_form.is_valid() and student_profile_form.is_valid():
            # checking the forms are valid or not
            # we do not save the user as we need to manipulate some data
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])

            student_profile_form.save(commit=False)
            student_profile_form.updated_by = request.user

            # after manipulating the data we save the information to the database
            user.save()
            student_profile_form.save()

            # we send a a success message
            messages.success(request, ('Your profile is successfully updated!'))
            return redirect(reverse('students:student_detail', kwargs={
                                    'student_slug': student_slug,
                                    'department_slug': department_slug}))
        else:
            # if the forms are not valid, we send an error message and show the errors to the user
            messages.error(request, ('Please check the error below.'))
            user_form_errors = user_form.errors
            student_profile_form_errors = student_profile_form.errors
            return render(request, 'student/profileupdate_form.html', {
                'user_form': user_form,
                'profile_form': student_profile_form,
                'user_form_errors':user_form_errors,
                'student_profile_form_errors':student_profile_form_errors
            })
    else:
        # if the method is get, we send the forms to the user so that they can fill those up
        user_form, student_profile_form = getForms(request, model=Student,
                                                        slug_instance=student_slug,
                                                        UserForm=StudentForm,
                                                        UserProfileInfoForm=StudentProfileInfoForm)

    return render(request, 'student/profileupdate_form.html', {
        'user_form': user_form,
        'profile_form': student_profile_form,
    })


class StudentDeleteView(LoginRequiredMixin,SelectRelatedMixin, DeleteView):
    login_url = '/login/options/'
    # redirect_field_name = 'blog/post_detail.html'
    model = Student

    def get_object(self, **kwargs):
        # we get the student object from database to delete that studnet
        return Student.objects.get(student_slug=self.kwargs['student_slug'])

    def get_success_url(self):
        # here, we define the page, which will be shown after deleting the student
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
    # get all students from database
    model = Student
    context_object_name = 'students'
    template_name = 'student/all_students.html'


def check_authority(request, student):
    if request.user.is_superuser:
        return True
    elif request.user.id == student.user.id:
        return True
    elif request.user.teacher == student.supervisor:
        return True
    else:
        return False


@login_required
@transaction.atomic
def distributeProjects(request, student_slug):
    student = Student.objects.get(student_slug=student_slug)
    projects = Project.objects.filter(departments__in=[student.department])

    try:
        # check if the user is admin or the teacher or the student himself
        # if the user is among them, then we let the user to choose project
        if check_authority(request=request, student=student):
            if request.method == 'GET':
                print(projects)
                return render(request, 'student/project_choice.html', context={
                    'projects': projects,
                    'student': student,
                    'Choices': ""
                })
    except Exception as ex:
        print(ex)
        return HttpResponse("You are not authorized to make changes!")


@login_required
@transaction.atomic
def editDistributedProjects(request, student_slug):
    student = Student.objects.get(student_slug=student_slug)
    projects = Project.objects.filter(departments__in=[student.department])

    # we get the projects the user chose before
    projectChoices = ProjectChoice.objects.values('project_id').filter(student_id=student.id).order_by('id')
    # getting the ids of each project the user chose
    projectChoices = [value['project_id'] for value in projectChoices]

    try:
        # check if the user is admin or the teacher or the student himself
        # if the user is among them, then we let the user to edit project choices
        if check_authority(request=request, student=student):
            if request.method == 'GET':
                print(projects)
                # print(projectChoices)

                return render(request, 'student/edit_project_choice.html', context={
                    'projects': projects,
                    'student':student,
                    'Choices':projectChoices
                })
    except Exception as ex:
        print(ex)
        return HttpResponse("You are not authorized to make changes!")


from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
@transaction.atomic
def getSelectedList(request):
    # we collect the projects selected by the user using ajax
    data = json.loads(request.body)
    selected_projects = data['selected_options']
    student_slug = data['student_slug']
    print("selected ", selected_projects)
    print("student_slug ", student_slug)

    # getting the particular student who's choices we are manipulating
    student = Student.objects.get(student_slug=student_slug)
    # projects = Project.objects.filter(available=True)

    # checking if the user has choosen 3 projects or not.
    # if len(selected_projects) != 3:
    #     return JsonResponse('You must select 3 projects!', safe=False)

    assigned = False
    rank = 1
    try:
        try:
            # we get the project that is assigned to the student
            # we minus one from project.taken before we assign new project
            # we set available=True as one more student can choose this project
            # at last we save project info to the database
            project_instance = Project.objects.get(id=student.assigned_project_id)
            print('project, ', project_instance)
            project_instance.taken -= 1
            project_instance.available = True
            project_instance.save()

            # we delete previous choices of projects the student has made
            ProjectChoice.objects.filter(student_id=student.id).delete()
        except Exception as ex:
            print(ex)

        for project in selected_projects:
            object = Project.objects.get(id=project)

            # we check if the project is available or not and if this project is not assigned
            if object.available and not assigned:
                # if the project is available and not assigned to the user, then we assign the
                # project id and project name to student table of the database.
                # we set assigned = True, to make sure that a project is assigned only once.
                student.assigned_project_id = object.id
                student.assigned_project_name = object.name
                assigned = True

                # we increase one (taken = taken + 1), as new student is assigned this project
                # saving project and student model
                object.taken += 1
                object.save()
                student.save()

                # we check if the number of projects taken by equals to the number of times
                # it can be taken. If the condition is true, we set available=False,
                # which means the project is not available to choose
                if object.taken == object.can_be_taken_by:
                    object.available = False
                    object.save()

            # we save the choice made by the student to ProjectChoice table of the database
            ProjectChoice.objects.create(
                project_id=project,
                student_id=student.id,
                rank=rank,
            )
            rank+=1

        # if any of the 3 projects choosen by the student is not assigned bacause of some error,
        # then we sugguest the student to again choose 3 projects which are available
        if assigned==False:
            return JsonResponse('Could not assign projects! Please select again. ', safe=False)

        return JsonResponse('successful', safe=False)

    except Exception as ex:
        print(ex)
        import sys
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(ex).__name__, ex)
        return JsonResponse(str(ex), safe=False)


def genereteList(request):
    students = Student.objects.all()
    context = {}
    student_projects = []

    # if get each student and the project assigned to that student
    for student in students:
        try:
            project = Project.objects.get(pk=student.assigned_project_id)
            # print(project.departments.all()[0].name)
            context = {
                'student': student,
                'project': project,
                'divisions': project.departments.all()
            }
        # if no project is assigned to the student, we set null value to project
        except Exception as ex:
            print(ex)
            context = {
                'student': student,
                'project': "",
                'divisions': ""
            }

        # at last, we append this context dictionary to the list student_projects
        student_projects.append(context)

    return render(request, 'student/distributed_list.html', context={
        "student_projects":student_projects
    })





