from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('dashboard/', views.dashboard, name = 'dashboard'),
    path('signup/', views.signup, name = 'signup'),
    path('', views.login, name = 'login'),
    path('login/', views.login, name = 'login'),
    path('logout/', views.logout, name = 'logout'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('reset_password/<str:reset_token>/', views.reset_password, name='reset_password'),
    path('category/', views.add_category, name = 'category'),
    path('createprod/', views.createprod, name = 'createprod'),
    path('editproduct/<str:product_name>/', views.editproduct, name = 'editproduct'),
    path('deleteproduct/<int:product_id>/', views.deleteproduct, name='deleteproduct'),
    path('category_related_products/<str:category_name>/', views.category_related_products, name='category_related_products'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('view_cart/', views.view_cart, name='view_cart'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
