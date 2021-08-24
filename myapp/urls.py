from . import views
from django.urls import path, include

add_name = 'myapp'

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
]
