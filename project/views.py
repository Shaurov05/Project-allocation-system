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
import xlrd

from django.forms import ModelForm
from extra_views import CreateWithInlinesView, UpdateWithInlinesView, InlineFormSetFactory

from .forms import *
from .models import *
from department.models import Department

from department.views import SuperUserCheck
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
                # print("create - get method")

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


class ProjectDeleteView(LoginRequiredMixin, DeleteView, SuperUserCheck):
    login_url = '/user/login/'
    template_name = 'project/project_confirm_delete.html'
    model = Project

    # get the particular project to delete
    def get_object(self, **kwargs):
        return Project.objects.get(project_slug=self.kwargs['project_slug'])

    # shows the list of projects page, after successfully deleting the project from the database
    def get_success_url(self):
          return reverse_lazy('projects:project_list')


@login_required
def upload_project_lists(request):
    if request.method == 'GET':
        return render(request, 'project/upload_project_lists.html', {})
    elif request.method == 'POST':
        try:
            blFileData = request.FILES['projectLists']
            countreturn = 0

            if str(blFileData).lower().endswith(('.xl', '.xls', '.xlsx')):
                xlrd.xlsx.ensure_elementtree_imported(False, None)
                xlrd.xlsx.Element_has_iter = True
                book = xlrd.open_workbook(file_contents=blFileData.read())

                for sheet in book.sheets():
                    number_of_rows = sheet.nrows

                    try:
                        for row in range(1, number_of_rows):
                            # print(row)
                            # print(sheet.cell(row, 2).value)
                            # reading rows from the excel file

                            if sheet.cell(row, 2).value:
                                name = str((sheet.cell(row, 0).value)).strip()
                                project_details = str(sheet.cell(row, 1).value).strip()
                                can_be_taken_by = int(sheet.cell(row, 2).value)
                                software_required = str(sheet.cell(row, 3).value).strip()
                                lab = str(sheet.cell(row, 4).value).strip()
                                choosen_dept = str(sheet.cell(row, 5).value).split(',')

                                choosen_dept = [dept.strip() for dept in choosen_dept]
                                # print(return_transactionid)

                                print("name: {}, detail: {}, taken_by: {}, "
                                      "software: {}, lab: {}, dept:  {}".format(name, project_details,
                                                                                can_be_taken_by, software_required, lab,
                                                                                choosen_dept))
                                # creating new object depending on the provided information
                                project = Project.objects.create(name=name, project_details=project_details,
                                                                 can_be_taken_by=can_be_taken_by, software_required=software_required,
                                                                 lab=lab)
                                countreturn += 1
                                failed_attempts = 0

                                # create new instance for DepartmentProject model, for each
                                # department listed in chosen Divisions column of the excel file
                                # as Department table has many-to-many relationship with Project table.
                                for department_name in choosen_dept:
                                    try:
                                        department = Department.objects.get(name=department_name)
                                        print("name: ", department.name)
                                        # create DepartmentProject object for every department in choosen_dept
                                        DepartmentProject.objects.create(project=project,
                                                                         department_id=department.id)
                                    except Exception as ex:
                                        failed_attempts += 1
                                        messages.error(request, str(ex))
                                        print("department exception: ", ex)

                                if failed_attempts == len(choosen_dept):
                                    # deleting the project
                                    # if any of the departments is not listed in the database,
                                    # then we delete the project.
                                    project.delete()
                                    countreturn -= 1

                        messages.success(request, str(countreturn) + ' Projects Successfully enlisted in database')
                        return redirect('projects:project_list')
                    except Exception as ex:
                        messages.error(request, str(ex))
                        return redirect('projects:upload_project_lists')
        except Exception as ex:
            messages.error(request, str(ex))
            return redirect('projects:upload_project_lists')


@login_required
def request_form(request):
    if request.method == 'GET':
        try:
            instance = ProjectRequestProposal.objects.filter(created_by=request.user.student)
            print("instance: ", instance)

            if request.user.student and instance:
                messages.error(request, "Cannot request more than once")
                return redirect(reverse('students:student_detail',
                                        kwargs={
                                            'department_slug':request.user.student.department.department_slug,
                                            'student_slug':request.user.student.student_slug}))
        except Exception as ex:
            print("request form exception: ", ex)

        form = ProjectRequestProposalForm()
        return render(request, 'project/request_form.html', context={'form': form})

    elif request.method == 'POST':
        # we get the information sent by the user using request.POST
        project_request_form = ProjectRequestProposalForm(data=request.POST)

        if project_request_form.is_valid():
            # if the information sent by the user is valid, then we save info to the database.
            instance = project_request_form.save(commit=False)
            instance.created_by_id = request.user.student.id
            instance.supervisor_id = request.user.student.supervisor.id
            instance.save()

        return redirect(reverse('students:student_detail',
                                        kwargs={
                                            'department_slug':request.user.student.department.department_slug,
                                            'student_slug':request.user.student.student_slug}))


def RequestedProjectList(request):
    try:
        requested_projects = ProjectRequestProposal.objects.filter(supervisor_id=request.user.teacher.id)
    except :
        requested_projects = ""

    return render(request, 'project/requested_project_list.html',
                  context={'requested_projects': requested_projects})




#
