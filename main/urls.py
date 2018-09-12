from django.urls import path

from . import views
urlpatterns = [
    path('', views.index, name='index'),
    path('add/',views.add_data,name='add'),
    path('import/',views.import_data,name='import'),
    path('query/',views.query_data,name='query'),
]