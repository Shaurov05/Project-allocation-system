from django.contrib.auth.models import User
from django.db import models
from django.conf import settings
from django.urls import reverse
from department.models import Department
from student.models import Student
from teacher.models import Teacher

# Create your models here.
from django.utils.text import slugify


class Project(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='student_project')
    department = models.ForeignKey(Department,blank=False, related_name="department_projects", on_delete=models.CASCADE)
    student_ID_no = models.CharField(max_length=20, unique=True, blank=False)

    name = models.CharField(max_length=300, blank=False)
    project_slug = models.SlugField(allow_unicode=True, unique=True)
    session = models.CharField(max_length=9, blank=False)

    created_by = models.ForeignKey(User, blank=False, related_name="project_created_by", on_delete=models.CASCADE)
    updated_by = models.ForeignKey(User, blank=False, related_name="project_updated_by", on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.project_slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("students:student_detail",
                        kwargs={'department_slug':self.department.department_slug, "project_slug":self.project_slug})

    class Meta:
        ordering = ["id"]
        unique_together = ["student", "department"]


class ProjectChoices(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="student_project_choices")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="student")
    rank = models.IntegerField(choices=(("1", "1"), ("2", "2"), ("3", "3")), blank=False)
    datetime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.project.name

    class Meta:
        unique_together = ("project", "student")


