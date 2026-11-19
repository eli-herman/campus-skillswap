from django.urls import path

from . import views

urlpatterns = [
    path('', views.skill_list, name='skill_list'),
    path('register/', views.register, name='register'),
    path('skills/<int:pk>/', views.skill_detail, name='skill_detail'),
    path('skills/create/', views.skill_create, name='skill_create'),
    path('skills/<int:pk>/edit/', views.skill_edit, name='skill_edit'),
    path('skills/<int:pk>/delete/', views.skill_delete, name='skill_delete'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('skills/<int:pk>/favorite/', views.favorite_toggle, name='favorite_toggle'),
    path('skills/<int:pk>/request/', views.booking_create, name='booking_create'),
    path('bookings/<int:pk>/update/', views.booking_update, name='booking_update'),
    path('inbox/', views.inbox, name='inbox'),
    path('messages/<str:username>/new/', views.message_create, name='message_create'),
    path('skills/<int:pk>/report/', views.report_create, name='report_create'),
    path('reviews/<int:pk>/delete/', views.review_delete, name='review_delete'),
]
