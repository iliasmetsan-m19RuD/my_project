from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.home_view, name='home'),
    path('directories/', views.directories_view, name='directories'),  # ← ЭТУ СТРОКУ ДОБАВЬ
    path('directories/<str:directory_name>/', views.directory_detail_view, name='directory_detail'),
    path('directories/<str:directory_name>/add/', views.directory_add_view, name='directory_add'),
    path('directories/<str:directory_name>/<int:item_id>/edit/', views.directory_edit_view, name='directory_edit'),
    path('directories/<str:directory_name>/<int:item_id>/delete/', views.directory_delete_view, name='directory_delete'),
    path('documents/', views.documents_view, name='documents'),
    path('documents/<str:doc_type>/<int:doc_id>/', views.document_detail_view, name='document_detail'),
    path('documents/add/<str:doc_type>/', views.add_document_view, name='add_document'),
    path('documents/delete/<str:doc_type>/<int:doc_id>/', views.delete_document_view, name='delete_document'),
    path('documents/edit/<str:doc_type>/<int:doc_id>/', views.edit_document_view, name='edit_document'),
]