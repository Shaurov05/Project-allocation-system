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
    global instance
    departments = Department.objects.all()
    try:
        if request.user.is_superuser or request.user.teacher:
            if request.method == 'GET':
                form = ProjectForm()
                print("create - get method")

                return render(request, "project/project_form.html",
                              context={'form': form,
                                       'departments': departments,
                                       })

            elif request.method == 'POST':
                project_form = ProjectForm(data=request.POST)

                if project_form.is_valid():
                    instance = project_form.save()
                    try:
                        selected_departments = request.POST.getlist("departments")
                    except:
                        selected_departments = request.POST.get("departments")
                    print(selected_departments)
                    # print(instance.id)

                    for department_id in selected_departments:
                        try:
                            DepartmentProject.objects.create(project=instance,
                                                             department_id=int(department_id))
                        except Exception as ex:
                            print("second exception: ", ex)
                            # deleting the project
                            project = Project.objects.get(id=instance.id)
                            project.delete()
                            messages.error(request, ('Check these errors'))
                            return render(request, 'project/project_form.html', context={
                                'form': ProjectForm(data=request.POST),
                                'departments': departments,
                                'formErrors': ex})
                else:
                    messages.error(request, ('Check these errors'))
                    return render(request, 'project/project_form.html', context={
                        'form': ProjectForm(data=request.POST),
                        'departments': departments,
                        'formErrors': ProjectForm.errors})

            print(instance.project_slug)
            return redirect(reverse('projects:project_detail',
                                    kwargs={"project_slug": instance.project_slug}))
    except Exception as ex:
        print("first exception: ", ex)
        return HttpResponse("You must be a superuser or Teacher to create a project")


@transaction.atomic
def UpdateProject(request, project_slug):
    global instance
    departments = Department.objects.all()
    project = Project.objects.get(project_slug=project_slug)
    choosen_depts = DepartmentProject.objects.filter(project_id=project.id)
    choosen_depts_id = [dept.department.id for dept in choosen_depts]

    try:
        if request.user.is_superuser or request.user.teacher:
            if request.method == 'GET':
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
                project_form = ProjectForm(data=request.POST, instance=project)

                if project_form.is_valid():
                    instance = project_form.save()
                    try:
                        selected_departments = request.POST.getlist("departments")
                    except:
                        selected_departments = request.POST.get("departments")
                    print("selected_departments ", selected_departments)
                    # print(instance.id)
                    DepartmentProject.objects.filter(project=instance).delete()
                    for department_id in selected_departments:
                        try:

                            DepartmentProject.objects.create(project=instance,
                                                             department_id=int(department_id))
                        except Exception as ex:
                            print("second exception: ", ex)
                            # deleting the project
                            project = Project.objects.get(id=instance.id)
                            project.delete()
                            messages.error(request, ('Check these errors'))
                            return render(request, 'project/project_update.html', context={
                                'form': ProjectForm(data=request.POST),
                                'departments': departments,
                                'formErrors': ex})
                else:
                    print("else part")
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
        print(self.kwargs)
        project = Project.objects.get(
            project_slug=self.kwargs['project_slug']
        )
        print(project)
        return project


class AllProjects(ListView):
    model = Project
    context_object_name = "projects"
    template_name = 'project/project_list.html'


class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    login_url = '/user/login/'
    template_name = 'project/project_confirm_delete.html'
    model = Project

    def get_object(self, **kwargs):
        return Project.objects.get(project_slug=self.kwargs['project_slug'])

    def get_success_url(self):
          return reverse_lazy('projects:project_list')







#
