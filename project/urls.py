from django.urls import path
from . import views
from django.conf.urls import url

app_name = 'projects'

urlpatterns = [
    path('create/project/', views.CreateNewProject, name='create_project'),
    path('upload/project/lists/', views.upload_project_lists, name='upload_project_lists'),
    path('request/project/form/', views.request_form, name='request_form'),
    path('requested/project/list', views.RequestedProjectList, name='request_project_list'),
    path('all/', views.AllProjects.as_view(), name='project_list'),

    path('<project_slug>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('update/<project_slug>/', views.UpdateProject, name='update_project'),

    # path('update/profile/student/<student_slug>/', views.update_student_profile, name='update_student_profile'),
    path('delete/<project_slug>/', views.ProjectDeleteView.as_view(), name='delete_project'),

    # path('all/students/', views.all_students.as_view(), name='all_students')
]
