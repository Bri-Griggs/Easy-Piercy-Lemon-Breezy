"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path
from app.views import *

urlpatterns = [
    path("", home, name = "home"),
    path('register/', registerPage, name="register"),
    path('login/', loginPage, name="login"),
    path('logout/', logoutUser, name="logout"),

    path('booking/', BookApp, name="booking"),
    path('time', timeApp, name='time'),
    path('appointments', userApp, name='appointments'),
    path('userUpdate/<int:id>', userUpdate, name='userUpdate'),
    path('userUpdateSubmit/<int:id>', userUpdateSubmit, name='userUpdateSubmit'),
    path('delete/<int:id>/', deleteAppointment, name='deleteAppointment'),
    path('staff-panel', staffPanel, name='staffPanel'),
    path("admin/", admin.site.urls),
]
