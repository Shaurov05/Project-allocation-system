from django.contrib.auth.models import User
from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.urls import reverse
# Create your models here.
import misaka
from department.models import Department

teacher_rank = [
    ("Lecturer", "Lecturer"),
    ("Assistant professor", "Assistant professor"),
    ("Associate professor", "Associate professor"),
    ("Professor", "Professor"),
    ("Professor emeritus", "Professor emeritus"),
]


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, blank=False, related_name="teachers", on_delete=models.CASCADE)

    profile_pic = models.ImageField(upload_to='teachers/profile_pics', blank=True)
    ID_Number = models.CharField(max_length=20, unique=True, blank=False)
    portfolio_site = models.URLField(blank=True, null=True)
    academic_rank = models.CharField(blank=False, max_length=100, choices=teacher_rank)
    teacher_slug = models.SlugField(allow_unicode=True, unique=True)

    created_by = models.ForeignKey(User, null=True, blank=True, related_name="teacher_created_by", on_delete=models.CASCADE)
    updated_by = models.ForeignKey(User, null=True, blank=True, related_name="teacher_updated_by", on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        self.teacher_slug = slugify(self.user.username)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("teachers:teacher_detail",
                        kwargs={"department_slug":self.department.department_slug,
                            "teacher_slug":self.teacher_slug})

    class Meta:
        ordering = ["id"]
        unique_together = ["user", "department"]
