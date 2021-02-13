from django.contrib import admin

# Register your models here.
from .models import Department, DepartmentImages


class DepartmentInline(admin.TabularInline):
    model = DepartmentImages

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    inlines = [
        DepartmentInline,
    ]
