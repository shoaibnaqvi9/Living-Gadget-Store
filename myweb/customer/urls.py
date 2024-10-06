from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
app_name = 'customer'
urlpatterns = [
    path('dashboard/', views.dashboard, name = 'dashboard'),
    path('customer/signup/', views.signup, name = 'customer/signup'),
    path('customer/login/', views.login, name = 'login'),
    path('forgot_password/', views.forgot_password, name = 'forgot_password'),
    path('reset_password/<str:reset_token>/', views.reset_password, name = 'reset_password'),
    
]