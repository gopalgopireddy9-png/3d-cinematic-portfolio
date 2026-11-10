from django.urls import path
from . import views
urlpatterns = [
    path('', views.home, name='home'),
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/<int:pk>/', views.job_detail, name='job_detail'),
    path('jobs/<int:pk>/apply/', views.apply_job, name='apply_job'),
    path('jobs/<int:pk>/save/', views.save_job, name='save_job'),
    path('jobs/<int:pk>/applications/', views.manage_applications, name='manage_applications'),
    path('jobs/post/', views.post_job, name='post_job'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('resume-database/', views.resume_database, name='resume_database'),
]
