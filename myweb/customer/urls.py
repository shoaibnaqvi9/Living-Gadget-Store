from django.urls import path
from customer import views as customer_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('customer/dashboard/', customer_views.dashboard, name = 'customer_dashboard'),
    path('customer/signup/', customer_views.signup, name = 'customer_signup'),
    path('customer/login/', customer_views.login, name = 'customer_login'),
    path('logout/', customer_views.logout, name = 'logout'),
    path('customer/forgot_password/', customer_views.forgot_password, name = 'customer_forgot_password'),
    path('customer/reset_password/<str:reset_token>/', customer_views.reset_password, name = 'customer_reset_password'),
]