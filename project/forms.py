from django import forms
from django.contrib.auth.models import User
from .models import Project
from department.models import Department
from student.models import Student


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        # fields = ['name', 'date', 'members']
        fields = ['name', 'project_details']

    # departments = forms.ModelMultipleChoiceField(
    #     queryset=Department.objects.all(),
    #     widget=forms.CheckboxSelectMultiple
    # )