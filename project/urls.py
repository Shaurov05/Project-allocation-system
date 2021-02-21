from django.urls import path
from . import views
from django.conf.urls import url

app_name = 'projects'

urlpatterns = [
    path('create/project/', views.CreateNewProject, name='create_project'),

    path('all/', views.ProjectList, name='project_list'),

    path('<project_slug>/', views.ProjectDetailView.as_view(), name='project_detail'),


    # path('update/profile/student/<student_slug>/', views.update_student_profile, name='update_student_profile'),
    # path('delete/<department_slug>/student/<student_slug>/', views.StudentDeleteView.as_view(), name='delete_student'),
    #
    # path('all/students/', views.all_students.as_view(), name='all_students')
]
