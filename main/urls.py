from django.urls import path

from . import views

app_name='main'
urlpatterns = [
    path('', views.index, name='index'),
    path('add/',views.add_data,name='add'),
    path('del/',views.del_data,name='del'),
    path('import/',views.import_data,name='import'),
    path('query/',views.query_data,name='query'),
    path('detail/',views.show_data,name='detail'),
    path('add_note/',views.add_notes,name='add_notes'),
    path('file/<str:pub_id>.pdf',views.view_file,name='view_file'),

    #ONLY FOR DEBUG !
    path('clear/',views.clear_all,name='clear_all'),
]