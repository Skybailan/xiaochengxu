from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path

urlpatterns = [
    path('', lambda request: JsonResponse({'status': 'ok', 'service': 'django-ij21'})),
    path('healthz', lambda request: JsonResponse({'status': 'ok'})),
    path('admin/', admin.site.urls),
    path('api/', include('words.urls')),
]
