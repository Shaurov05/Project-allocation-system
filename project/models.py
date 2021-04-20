from django.contrib.auth.models import User
from django.db import models
from django.conf import settings
from django.urls import reverse
from department.models import Department
from student.models import Student
from teacher.models import Teacher

from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
from django.core.exceptions import PermissionDenied


# Create your models here.
from django.utils.text import slugify


class Project(models.Model):
    departments = models.ManyToManyField(Department, through="DepartmentProject")
    students = models.ManyToManyField(User, through="ProjectChoice")

    name = models.CharField(max_length=300, blank=False)
    project_details = models.TextField()
    project_slug = models.SlugField(allow_unicode=True, unique=True)
    available = models.BooleanField(default=True)

    software_required = models.TextField()
    lab = models.CharField(max_length=300)

    taken = models.IntegerField(default=0)
    can_be_taken_by = models.IntegerField(default=5)

    created_by = models.ForeignKey(User, blank=True, null=True, related_name="project_created_by", on_delete=models.CASCADE)
    updated_by = models.ForeignKey(User, blank=True, null=True, related_name="project_updated_by", on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.project_slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("projects:project_detail",
                        kwargs={"project_slug":self.project_slug})

    @receiver(pre_delete, sender=User)
    def delete_user(sender, instance, **kwargs):
        if not instance.is_superuser and not instance.teachers:
            raise PermissionDenied


class ProjectChoice(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="student_project_choices")
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="students")
    rank = models.IntegerField(choices=(("1", "1"), ("2", "2"), ("3", "3")), blank=False)
    datetime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.project.name

    class Meta:
        unique_together = ("project", "student")


class DepartmentProject(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="department_projects")
    department = models.ForeignKey(Department, related_name="departments", on_delete=models.CASCADE)

    def __str__(self):
        return self.project.name


class ProjectRequestProposal(models.Model):
    name = models.CharField(max_length=256)
    details = models.TextField()
    software_required = models.CharField(max_length=256)
    lab = models.CharField(max_length=300)
    supervisor = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    created_by = models.ForeignKey(Student, on_delete=models.CASCADE)


