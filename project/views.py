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


from django.db import transaction
@login_required
@transaction.atomic
def CreateNewProject(request):
    departments = Department.objects.all()
    try:
        if not request.user.is_superuser or not request.user.teachers:
            return HttpResponse("You must be a superuser or Teacher to create a project")
    except Exception as ex:
        print("first exception: ", ex)
        if request.method == 'GET':
            form = ProjectForm()
            # students = Student.objects.all()

            return render(request, "project/project_form.html",
                          context={'form':form,
                                   # 'students': students
                                   'departments':departments,
                                   })

        elif request.method == 'POST':
            project_form = ProjectForm(data=request.POST)

            if project_form.is_valid():
                instance = project_form.save()
                try:
                    selected_departments = request.POST.getlist("departments")
                except:
                    selected_departments = request.POST.getlist("departments")
                print(selected_departments)
                # print(instance.id)

                for department_id in selected_departments:
                    try:
                        DepartmentProject.objects.create(project=instance,
                                                         department_id=int(department_id))
                    except Exception as ex:
                        print("second exception: ",ex)
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
                            kwargs={"project_slug":instance.project_slug}))



class ProjectDetailView(SelectRelatedMixin, DetailView):

    model = Project
    context_object_name = 'project_details'
    template_name = 'project/project_detail.html'

    def get_object(self, **kwargs):
        return get_object_or_404(
            Project,
            project_slug=self.kwargs['project_slug']
            # access_key=self.kwargs['access_key'],
        )


def ProjectList(request):
    print("list")
    projects  = Project.objects.all()
    return render(request, "project/project_list.html", context={
        'projects':projects
    })
    # model = Project
    # context_object_name = "projects"
    # template_name = 'project/project_list.html'

    # def get_queryset(self):
    #     self.projects = Project.objects.all()
    #
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['projects'] = self.projects
    #     return context


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
