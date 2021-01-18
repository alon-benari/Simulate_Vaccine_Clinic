from django.urls import path

from polls import views

urlpatterns = [
    path('', views.index, name='index'),
    path('post_params/', views.post_params, name = "post_params")
]
