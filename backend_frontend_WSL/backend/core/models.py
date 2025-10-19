from django.db import models
from django.contrib.auth.models import AbstractUser # Usaremos el modelo de User de Django para Usuarios

# Create your models here.

# Extendemos el modelo de usuario de Django para añadir el campo 'rol'
class User(AbstractUser):
    ROL_CHOICES = [
        ('admin', 'Administrador'),
        ('anotador', 'Anotador'),
        ('visor', 'Visor'),
    ]
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='anotador')
    
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions '
                  'granted to each of their groups.',
        related_name="core_user_set",  # <<-- AÑADE ESTO
        related_query_name="core_user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="core_user_set",  # <<-- AÑADE ESTO
        related_query_name="core_user",
    )
    # =======================================================

    class Meta:
        db_table = 'usuarios'
        verbose_name = 'usuario' # Para el panel de admin de Django
        verbose_name_plural = 'usuarios' # Para el panel de admin de Django


class Muestra(models.Model):
    # NOTA: Django creará automáticamente un campo 'id' SERIAL PRIMARY KEY
    event_id = models.CharField(max_length=50, unique=True, null=False)
    timestamp_inicio = models.DateTimeField(null=False)
    duracion_ms = models.IntegerField(null=False)
    frecuencia_muestreo_hz = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    num_puntos = models.IntegerField(default=5120, null=False)
    origen_hardware = models.CharField(max_length=50, blank=True, null=True) # blank=True permite que sea vacío en formularios
    estado_procesamiento_choices = [
        ('pendiente', 'Pendiente'),
        ('procesado', 'Procesado'),
        ('error', 'Error'),
    ]
    estado_procesamiento = models.CharField(max_length=20, choices=estado_procesamiento_choices, default='pendiente', null=False)
    fecha_procesamiento = models.DateTimeField(null=True, blank=True) # null=True y blank=True para campos opcionales
    fecha_creacion = models.DateTimeField(auto_now_add=True) # Se establece automáticamente al crear el objeto
    usuario_creacion = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True) # Si el usuario se borra, el campo se pone a NULL

    class Meta:
        db_table = 'muestras' # Mapea este modelo a tu tabla 'muestras' existente
        indexes = [ # Define los índices que creaste manualmente
            models.Index(fields=['event_id'], name='idx_muestras_eventid'),
            models.Index(fields=['timestamp_inicio'], name='idx_muestras_ts_inicio'),
            models.Index(fields=['estado_procesamiento'], name='idx_muestras_estado_proc'),
        ]

    def __str__(self):
        return f"Muestra {self.event_id} ({self.timestamp_inicio.strftime('%Y-%m-%d %H:%M')})"


class Espectrograma(models.Model):
    muestra = models.OneToOneField(Muestra, on_delete=models.CASCADE, primary_key=True) # OneToOneField implica que el ID de la Muestra es la PK aquí
    data_espectrograma = models.BinaryField(null=False) # BYTEA en PostgreSQL
    metadata_json = models.JSONField(null=True, blank=True) # JSONB en PostgreSQL
    fecha_generacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'espectrogramas'
        indexes = [
            models.Index(fields=['muestra'], name='idx_espectrogramas_muestra_id'), # Referencia la PK de la Muestra
        ]

    def __str__(self):
        return f"Espectrograma de Muestra {self.muestra.event_id}"


class Anotacion(models.Model):
    muestra = models.ForeignKey(Muestra, on_delete=models.CASCADE, null=False)
    tipo_perturbacion_choices = [
        ('sobretension', 'Sobretensión'),
        ('caida_tension', 'Caída de Tensión'),
        ('harmonicos', 'Armónicos'),
        ('transitorio', 'Transitorio'),
        ('falla_sistema', 'Falla del Sistema'),
        ('otros', 'Otros'),
    ]
    tipo_perturbacion = models.CharField(max_length=50, choices=tipo_perturbacion_choices, null=False)
    comentarios = models.TextField(blank=True, null=True)
    timestamp_inicio_region = models.IntegerField(null=True, blank=True)
    timestamp_fin_region = models.IntegerField(null=True, blank=True)
    usuario_anotador = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_anotacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'anotaciones'
        indexes = [
            models.Index(fields=['muestra'], name='idx_anotaciones_muestra'),
            models.Index(fields=['tipo_perturbacion'], name='idx_anot_tipo_pert'),
        ]

    def __str__(self):
        return f"Anotación para Muestra {self.muestra.event_id}: {self.tipo_perturbacion}"


class Clasificacion(models.Model):
    muestra = models.OneToOneField(Muestra, on_delete=models.CASCADE, null=False) # OneToOneField porque una muestra tiene UNA clasificación final
    clase_manual_choices = [
        ('sobretension', 'Sobretensión'),
        ('caida_tension', 'Caída de Tensión'),
        ('harmonicos', 'Armónicos'),
        ('transitorio', 'Transitorio'),
        ('falla_sistema', 'Falla del Sistema'),
        ('normal', 'Normal'),
        ('no_clasificado', 'No Clasificado'),
    ]
    clase_manual = models.CharField(max_length=50, choices=clase_manual_choices, blank=True, null=True)
    clase_modelo = models.CharField(max_length=50, blank=True, null=True)
    confianza_modelo = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    estado_clasificacion_choices = [
        ('pendiente', 'Pendiente'),
        ('validada', 'Validada por Experto'),
        ('rechazada', 'Rechazada por Experto'),
        ('modelo_aplicado', 'Modelo Aplicado (sin validación)'),
    ]
    estado_clasificacion = models.CharField(max_length=20, choices=estado_clasificacion_choices, default='pendiente', null=False)
    usuario_validador = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_clasificacion = models.DateTimeField(auto_now_add=True)
    version_modelo = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        db_table = 'clasificaciones'
        indexes = [
            models.Index(fields=['muestra'], name='idx_clasi_muestra'),
            models.Index(fields=['clase_manual'], name='idx_clasi_clase_manual'),
            models.Index(fields=['clase_modelo'], name='idx_clasi_clase_modelo'),
        ]

    def __str__(self):
        return f"Clasificación para Muestra {self.muestra.event_id}: Manual={self.clase_manual}, Modelo={self.clase_modelo}"