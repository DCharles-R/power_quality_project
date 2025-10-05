# core/serializers.py

from rest_framework import serializers
from .models import Muestra, Espectrograma, Anotacion, Clasificacion, User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'rol', 'fecha_creacion')
        read_only_fields = ('fecha_creacion',) # No se permite modificar la fecha de creación desde la API

class MuestraSerializer(serializers.ModelSerializer):
    usuario_creacion_username = serializers.CharField(source='usuario_creacion.username', read_only=True)

    class Meta:
        model = Muestra
        fields = '__all__' # Incluye todos los campos del modelo Muestra
        read_only_fields = ('id', 'fecha_creacion', 'fecha_procesamiento', 'usuario_creacion')

class EspectrogramaSerializer(serializers.ModelSerializer):
    # Para evitar enviar la gran cantidad de datos binarios por defecto
    # a menos que se solicite específicamente, podríamos no incluirlo en el listado
    # Pero para empezar, lo incluiremos.
    class Meta:
        model = Espectrograma
        fields = '__all__'
        read_only_fields = ('muestra',)

class AnotacionSerializer(serializers.ModelSerializer):
    usuario_anotador_username = serializers.CharField(source='usuario_anotador.username', read_only=True)

    class Meta:
        model = Anotacion
        fields = '__all__'
        read_only_fields = ('fecha_anotacion',)

class ClasificacionSerializer(serializers.ModelSerializer):
    usuario_validador_username = serializers.CharField(source='usuario_validador.username', read_only=True)

    class Meta:
        model = Clasificacion
        fields = '__all__'
        read_only_fields = ('fecha_clasificacion',)