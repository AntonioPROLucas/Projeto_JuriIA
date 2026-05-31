from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from usuarios.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='root_home'),
    path('usuarios/', include('usuarios.urls')),
    path('ia/', include('ia.urls')),
    path('martor/', include('martor.urls')),
]

# Isso permite que o Django sirva os arquivos de mídia (PDFs/Imagens) no ambiente local
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)