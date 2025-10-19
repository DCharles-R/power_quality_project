# backend/core/filters.py

import django_filters
from .models import Muestra, Anotacion

class MuestraFilter(django_filters.FilterSet):
    # Filtro para 'tipo_perturbacion' que busca en las anotaciones relacionadas
    tipo_perturbacion = django_filters.CharFilter(
        field_name='anotacion__tipo_perturbacion', # Accede al campo tipo_perturbacion de las anotaciones
        lookup_expr='iexact', # Búsqueda insensible a mayúsculas/minúsculas y exacta
        distinct=True # Asegura que si una muestra tiene múltiples anotaciones, no se duplique
    )

    class Meta:
        model = Muestra
        fields = ['estado_procesamiento', 'tipo_perturbacion'] # Aquí incluirás los campos que quieres filtrar