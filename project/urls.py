from django.urls import path
from . import views
from django.conf.urls import url

app_name = 'projects'

urlpatterns = [
    path('create/project/', views.CreateProject.as_view(), name='create_project'),


    # path('<department_slug>/<student_slug>/profile/', views.StudentDetailView.as_view(), name='student_detail'),
    #
    path('projects/', views.ProjectList.as_view(), name='project_list'),
    # path('update/profile/student/<student_slug>/', views.update_student_profile, name='update_student_profile'),
    # path('delete/<department_slug>/student/<student_slug>/', views.StudentDeleteView.as_view(), name='delete_student'),
    #
    # path('all/students/', views.all_students.as_view(), name='all_students')
]
