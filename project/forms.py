from django import forms
from django.contrib.auth.models import User
from .models import *
from department.models import Department
from student.models import Student


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        # fields = ['name', 'date', 'members']
        fields = ['name', 'project_details', 'can_be_taken_by',
                  'software_required', 'lab']

    # departments = forms.ModelMultipleChoiceField(
    #     queryset=Department.objects.all(),
    #     widget=forms.CheckboxSelectMultiple
    # )


class ProjectRequestProposalForm(forms.ModelForm):
    class Meta:
        model = ProjectRequestProposal
        exclude = ['created_by', 'supervisor']


