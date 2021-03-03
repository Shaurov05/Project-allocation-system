from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone

# Extra Imports for the Login and Logout Capabilities
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from PIL import Image
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

from django.views.generic import (TemplateView,ListView,View,
                                  DetailView,CreateView,
                                  UpdateView,DeleteView)

from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from braces.views import SelectRelatedMixin
from django.forms import modelformset_factory
from django.contrib import messages

from . models import DepartmentImages, Department
from . forms import DepartmentForm, DepartmentImageForm
from django.contrib.auth.mixins import UserPassesTestMixin


# checks if the user requesting the page is superuser or not
class SuperUserCheck(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_superuser


@login_required
def CreateDepartment(request):
    # using modelformset_factory, we can specify how many fields we want to add in the form
    # here, using extra=3, we are enabling the user to upload 3 images of department.
    ImageFormSet = modelformset_factory(model=DepartmentImages,
                                form=DepartmentImageForm, extra=3 )

    if request.method == 'POST':
        # if a user submits the form we get the items sent by the user by (request.user)
        departmentForm = DepartmentForm(request.POST)
        formset = ImageFormSet(request.POST, request.FILES,
                            queryset=DepartmentImages.objects.none())

        # checking the form is valid or not. (Checking different type of validation declared in models.py file)
        if departmentForm.is_valid() and formset.is_valid():
            # here, we prevent the system to save details sent by user to the database as we need to manipulate the data.
            department_form = departmentForm.save(commit=False)
            department_form.created_by = request.user

            # collecting department name and established date from POST request
            dept_name = request.POST.get('name')
            established_date = request.POST.get('established_date')
            if established_date:
                print(established_date)
                department_form.established_date = established_date

            # after manipulating data, we save the information to database.
            department_form.save()

            from django.utils.text import slugify
            dept_slug = slugify(dept_name)

            for form in formset.cleaned_data:
                # this helps to not crash if the user
                # do not upload all the photos
                # we check that whether the user adds image of the particular department or not!
                if form:
                    image = form['image']
                    department_image = DepartmentImages(department=department_form, image=image)
                    department_image.save()

            # sending a success message to the user
            messages.success(request,
                        "Photos has been uploaded to departments section of media!")
            print("\n\n****dept: {}***/n/n".format(dept_slug))
            # redirecting the user to the department details page.
            return HttpResponseRedirect(reverse("departments:department_detail", kwargs={
                                                                "department_slug":dept_slug}))
        else:
            # if the form is not valid, then we show the user the errors.
            print(departmentForm.errors, formset.errors)
            departmentForm_errors = departmentForm.errors
            formset_errors = formset.errors
            return render(request, 'student/profileupdate_form.html', {
                'department_form': DepartmentForm,
                "formset":formset,
                'departmentForm_errors': departmentForm_errors,
                'formset_errors': formset_errors
            })
    else:
        # if user method is get, we simply send the forms to the user to fill them up
        departmentForm = DepartmentForm()
        formset = ImageFormSet(queryset=DepartmentImages.objects.none())
    return render(request, 'department/department_form.html', {
                            "department_form":departmentForm,
                            "formset":formset
                        })


class DepartmentDetail(DetailView):
    model = Department

    # gets the particular department and return it to the user
    def get_object(self, **kwargs):
        return get_object_or_404(
            Department,
            department_slug__iexact=self.kwargs['department_slug'],
        )


class DepartmentStudents(DetailView):
    # find the students admitted to that department
    model = Department
    slug_field = 'department_slug'
    slug_url_kwarg = 'department_slug'
    template_name = 'department/department_students.html'


class DepartmentTeachers(DetailView):
    # find the teachers belong to that department
    model = Department
    slug_field = 'department_slug'
    slug_url_kwarg = 'department_slug'
    template_name = 'department/department_teachers.html'


class UpdateDepartment(SuperUserCheck, UpdateView):
    model = Department
    fields = ('chairman', 'detail')
    template_name = 'department/department_update.html'

    def get_object(self, **kwargs):
        return get_object_or_404(
            Department,
            department_slug__iexact=self.kwargs['department_slug'],
            # access_key=self.kwargs['access_key'],
        )


class DepartmentDelete(SuperUserCheck, DeleteView):
    # declaring the model
    model = Department

    # after deleting the department, it redirects the user to the list of departments page.
    def get_success_url(self):
          return reverse_lazy("departments:all_departments")

    # gets the specific department to delete
    def get_object(self, **kwargs):
        return get_object_or_404(
            Department,
            department_slug__iexact=self.kwargs['department_slug'],
            # access_key=self.kwargs['access_key'],
        )

    # returns a message to the user
    def delete(self, *args, **kwargs):
        messages.success(self.request, "Department Deleted")
        return super().delete(*args, **kwargs)


class AllDepartments(ListView):
    # shows all departments in the university
    model = Department
    template_name = 'department/department_list.html'









###########
