from django.urls import path
from myapp import views as user_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', user_views.home, name = 'home'),
    path('dashboard/', user_views.dashboard, name = 'dashboard'),
    path('signup/', user_views.signup, name = 'signup'),
    path('login/', user_views.login, name = 'login'),
    path('logout/', user_views.logout, name = 'logout'),
    path('forgot_password/', user_views.forgot_password, name='forgot_password'),
    path('reset_password/<str:reset_token>/', user_views.reset_password, name='reset_password'),
    path('category/', user_views.add_category, name = 'category'),
    path('createprod/', user_views.createprod, name = 'createprod'),
    path('editproduct/<str:product_name>/', user_views.editproduct, name = 'editproduct'),
    path('deleteproduct/<int:product_id>/', user_views.deleteproduct, name='deleteproduct'),
    path('category_related_products/<str:category_name>/', user_views.category_related_products, name='category_related_products'),
    path('add-to-cart/<int:product_id>/', user_views.add_to_cart, name='add_to_cart'),
    path('view_cart/', user_views.view_cart, name='view_cart'),
    path('search/', user_views.search, name = 'search'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
