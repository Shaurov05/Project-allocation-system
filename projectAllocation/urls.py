"""university_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from . import views
from . views import ErrorTemplateView
# from django.conf import settings
from django.conf.urls.static import static

from django.views.static import serve
from django.conf.urls import url
from django.conf import settings

urlpatterns = [
    url(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    url(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),

    path('admin/', admin.site.urls),
    path('', views.IndexPage.as_view() , name='index'),

    path('registration/options/', views.RegistrationOptionsPage.as_view(), name='registration_options'),
    path('logout/', views.user_logout, name='logout'),
    path('thanks/', views.LogoutPage.as_view(), name='thanks'),

    path('user/login/', views.user_login, name='user_login'),
    path('departments/', include("department.urls", namespace='departments')),
    path('students/', include("student.urls", namespace='students')),
    path('teachers/', include("teacher.urls", namespace='teachers')),
    path('projects/', include("project.urls", namespace='projects')),

    re_path(r"^.*$", ErrorTemplateView.as_view(), name='entry-point'),


]


from django.conf import settings
from django.conf.urls.static import static
if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL,
                              document_root=settings.MEDIA_ROOT)
