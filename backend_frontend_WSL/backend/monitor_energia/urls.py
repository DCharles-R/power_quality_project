"""
URL configuration for monitor_energia project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

# monitor_energia/urls.py

from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core import views # Importa las vistas de tu app core

# Crear un router para registrar los ViewSets de la API
router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'muestras', views.MuestraViewSet)
router.register(r'espectrogramas', views.EspectrogramaViewSet)
router.register(r'anotaciones', views.AnotacionViewSet)
router.register(r'clasificaciones', views.ClasificacionViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)), # Incluye las URLs generadas por el router para tu API
    # DRF también proporciona URLs para autenticación básica y de sesión si las necesitas
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')), 
]