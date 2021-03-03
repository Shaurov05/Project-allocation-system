from django.urls import path
from . import views

app_name = 'teachers'

urlpatterns = [
    path('teacher/register/', views.teacher_register, name='teacher_register'),

    path('department/<department_slug>/profile/<teacher_slug>/', views.TeacherDetailView.as_view(), name='teacher_detail'),
    path('department/<department_slug>/teachers', views.TeacherList.as_view(), name='teacher_list'),
    path('update/profile/teacher/<teacher_slug>/', views.update_teacher_profile, name='update_teacher_profile'),
    path('delete/<department_slug>/teacher/<teacher_slug>/', views.TeacherDeleteView.as_view(), name='delete_teacher'),

    path('all/teachers/', views.AllTeachers.as_view(), name='all_teachers')
]
