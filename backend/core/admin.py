from django.contrib import admin
from .models import User, Muestra, Espectrograma, Anotacion, Clasificacion
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Register your models here.
# Registra tus modelos aquí.

# Opcional: Personaliza la vista del modelo User en el admin
# Si quieres más control sobre cómo se ve el usuario en el admin
# from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# @admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'rol', 'is_staff')
    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {'fields': ('rol',)}),
    )

# Para empezar, un registro simple es suficiente:
admin.site.register(User)
admin.site.register(Muestra)
admin.site.register(Espectrograma)
admin.site.register(Anotacion)
admin.site.register(Clasificacion)
