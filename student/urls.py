from django.urls import path
from . import views
from django.conf.urls import url

app_name = 'students'

urlpatterns = [
    path('student/register/', views.student_register, name='student_register'),

    path('selected/option/', views.getSelectedList, name='selected_option'),
    path('distribute/project/', views.genereteList, name='distributed_project_list'),

    path('<department_slug>/<student_slug>/profile/', views.student_detail_view, name='student_detail'),
    path('department/<department_slug>/students', views.StudentList.as_view(), name='student_list'),
    path('update/profile/student/<student_slug>/', views.update_student_profile, name='update_student_profile'),
    path('delete/<department_slug>/student/<student_slug>/', views.StudentDeleteView.as_view(), name='delete_student'),

    path('all/students/', views.all_students.as_view(), name='all_students'),

    path('choose/project/<student_slug>/', views.distributeProjects, name='project_choice'),
    path('edit/project/<student_slug>/', views.editDistributedProjects, name='edit_project_choice'),



]
