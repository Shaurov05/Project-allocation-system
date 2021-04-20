from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(Project)
admin.site.register(DepartmentProject)
admin.site.register(ProjectChoice)
admin.site.register(ProjectRequestProposal)
