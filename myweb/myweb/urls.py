from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('admin/', include('admin.urls', namespace='admin')),
    path('customer/', include('customer.urls', namespace='customer')),
]+ static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)