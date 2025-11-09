from django.urls import path,include
from . import views

urlpatterns = [
    path('social-auth/', include('social_django.urls', namespace='social')),
    path('', include('django.contrib.auth.urls')),
    path('',views.dashboard,name='dashboard'),
    path('register/', views.register, name='register'),
    path('edit/', views.edit, name='edit'),
    path("profile/", views.profile, name="profile"),
 
    
   
    path('banks/', views.bank_list, name='bank_list'),
    path('banks/add/', views.bank_create, name='bank_create'),
    path('banks/<int:pk>/edit/', views.bank_update, name='bank_update'),
    path('banks/<int:pk>/delete/', views.bank_delete, name='bank_delete'),

    
]