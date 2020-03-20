from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.urls import include


urlpatterns = [
    path('', include(('core.urls', 'core'), namespace='core')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

