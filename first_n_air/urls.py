from django.urls import path
from . import views

urlpatterns=[
    path('', views.home, name='home'),
    path('contact/', views.contact, name='contact'),
    path('products/<slug>/', views.products, name='products'),
    path('register/', views.register, name='register'),
    path('single/<int:pk>/', views.single, name='single'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('logout/', views.logout_user, name='logout'),
    path('login/', views.login_user, name='login'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
]
