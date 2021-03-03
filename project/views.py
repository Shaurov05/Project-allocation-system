from django.shortcuts import render, redirect,get_object_or_404

# Extra Imports for the Login and Logout Capabilities
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages

from django.views.generic import (TemplateView,ListView,View,
                                  DetailView,CreateView,
                                  UpdateView,DeleteView)

from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from braces.views import SelectRelatedMixin

from django.forms import ModelForm
from extra_views import CreateWithInlinesView, UpdateWithInlinesView, InlineFormSetFactory

from .forms import *
from .models import *
from department.models import Department

from django.db import transaction


@login_required
@transaction.atomic
def CreateNewProject(request):
    # declaring a glocal variable
    global instance
    # gets all objects of department model
    departments = Department.objects.all()
    try:
        # check if the user is superuser or the user is teacher
        if request.user.is_superuser or request.user.teacher:
            if request.method == 'GET':
                form = ProjectForm()
                print("create - get method")

                return render(request, "project/project_form.html",
                              context={'form': form,
                                       'departments': departments,
                                       })

            elif request.method == 'POST':
                # we get the information sent by the user using request.POST
                project_form = ProjectForm(data=request.POST)

                if project_form.is_valid():
                    # if the information sent by the user is valid, then we save info to the database.
                    instance = project_form.save()

                    # check if user selects multiple projects or not
                    try:
                        # get the list of ids of departments
                        selected_departments = request.POST.getlist("departments")
                    except:
                        # get a single id of department
                        selected_departments = request.POST.get("departments")

                    print(selected_departments)
                    # print(instance.id)

                    for department_id in selected_departments:
                        try:
                            # create DepartmentProject object for every if in selected_departments
                            DepartmentProject.objects.create(project=instance,
                                                             department_id=int(department_id))
                        except Exception as ex:
                            print("second exception: ", ex)
                            # deleting the project
                            # if any exception occurs, delete the project object
                            project = Project.objects.get(id=instance.id)
                            project.delete()
                            messages.error(request, ('Check these errors'))
                            return render(request, 'project/project_form.html', context={
                                'form': ProjectForm(data=request.POST),
                                'departments': departments,
                                'formErrors': ex})
                else:
                    # if the form is not valid, it show the errors to the user
                    messages.error(request, ('Check these errors'))
                    return render(request, 'project/project_form.html', context={
                        'form': ProjectForm(data=request.POST),
                        'departments': departments,
                        'formErrors': ProjectForm.errors})

            print(instance.project_slug)
            # if everything is okay, then redirect the user to the project details page.
            return redirect(reverse('projects:project_detail',
                                    kwargs={"project_slug": instance.project_slug}))
    except Exception as ex:
        print("first exception: ", ex)
        return HttpResponse("You must be a superuser or Teacher to create a project")


@transaction.atomic
def UpdateProject(request, project_slug):
    global instance
    # getting the project and all departments from the database
    departments = Department.objects.all()
    project = Project.objects.get(project_slug=project_slug)
    # filtering departments under that particular project and getting ids of those departments.
    choosen_depts = DepartmentProject.objects.filter(project_id=project.id)
    choosen_depts_id = [dept.department.id for dept in choosen_depts]

    try:
        if request.user.is_superuser or request.user.teacher:
            if request.method == 'GET':
                # getting the project form and passing the instance to get the previous data from the database
                form = ProjectForm(instance=project)
                print("create - get method")

                return render(request, "project/project_update.html",
                              context={'form': form,
                                       'project':project,
                                       'departments': departments,
                                       "choosen_depts_id": choosen_depts_id,
                                       })

            elif request.method == 'POST':
                print("post ")
                # getting the values sent by the user
                project_form = ProjectForm(data=request.POST, instance=project)

                if project_form.is_valid():
                    # after checking the form validation, we save the updates to the database
                    instance = project_form.save()

                    try:
                        # getting the list of ids sent by the user
                        selected_departments = request.POST.getlist("departments")
                    except:
                        # getting a single id sent by the user
                        selected_departments = request.POST.get("departments")
                    print("selected_departments ", selected_departments)
                    # print(instance.id)

                    # getting the previous departments added under the particular project and
                    # delete those before saving updates.
                    DepartmentProject.objects.filter(project=instance).delete()
                    for department_id in selected_departments:
                        try:
                            # creating new object/ saving departments under the particular project
                            DepartmentProject.objects.create(project=instance,
                                                             department_id=int(department_id))
                        except Exception as ex:
                            print("second exception: ", ex)

                            # deleting the project
                            # if exception occurs, delete the project
                            project = Project.objects.get(id=instance.id)
                            project.delete()

                            messages.error(request, ('Check these errors'))
                            return render(request, 'project/project_update.html', context={
                                'form': ProjectForm(data=request.POST),
                                'departments': departments,
                                'formErrors': ex})
                else:
                    print("else part")
                    # if the form is not valid, show the errors to the user
                    messages.error(request, ('Check these errors'))
                    return render(request, 'project/project_update.html', context={
                        'form': ProjectForm(data=request.POST, instance=project),
                        'departments': departments,
                        'formErrors': ProjectForm.errors})

                print("project_slug ", instance.project_slug)
                return HttpResponseRedirect(reverse('projects:project_detail',
                                        kwargs={"project_slug": instance.project_slug}))
        else:
            raise Exception
    except Exception as ex:
        print("first exception: ", ex)
        return HttpResponse("You must be a superuser or Teacher to create a project")


class ProjectDetailView(DetailView):
    model = Project
    context_object_name = 'project_details'
    template_name = 'project/project_detail.html'

    def get_object(self, **kwargs):
        # gets the particular object from the database to show it to the user
        print(self.kwargs)
        project = Project.objects.get(
            project_slug=self.kwargs['project_slug']
        )
        print(project)
        return project


class AllProjects(ListView):
    # ListView collects all projects from the database
    model = Project
    context_object_name = "projects"
    template_name = 'project/project_list.html'


class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    login_url = '/user/login/'
    template_name = 'project/project_confirm_delete.html'
    model = Project

    # get the particular project to delete
    def get_object(self, **kwargs):
        return Project.objects.get(project_slug=self.kwargs['project_slug'])

    # shows the list of projects page, after successfully deleting the project from the database
    def get_success_url(self):
          return reverse_lazy('projects:project_list')







#
