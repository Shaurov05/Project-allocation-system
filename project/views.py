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


class CreateProject(CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'project/project_form.html'
    success_url = reverse_lazy('index')



class ProjectDetailView(SelectRelatedMixin, DetailView):
    context_object_name = 'project_detail'
    model = Teacher
    template_name = 'projects/project_detail.html'

    def get_object(self, **kwargs):
        return get_object_or_404(
            Project,
            project_slug=self.kwargs['project_slug']
            # access_key=self.kwargs['access_key'],
        )


class ProjectList(ListView):
    model = Project
    context_object_name = "projects"
    template_name = 'projects/all_projects.html'


class ProjectDeleteView(LoginRequiredMixin,SelectRelatedMixin, DeleteView):
    login_url = '/teacher/login/'
    template_name = 'teachers/teacher_confirm_delete.html'
    model = Project
    # select_related = ("user", "department")

    def get_object(self, **kwargs):
        return Project.objects.get(project_slug=self.kwargs['project_slug'])

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



class AllProjects(ListView):
    model = Teacher
    context_object_name = "projects"
    template_name = 'projects/all_projects.html'




#
