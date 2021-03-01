from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter
# from .views import PersonaFilaViewSet

# router = DefaultRouter()
# router.register('personas', PersonaFilaViewSet, basename='personas')

urlpatterns = [
    path('login/', user_login, name='login'),
    path('logout/', logout_user, name='logout'),
    path('mantenedor-fechas/', mantenedor_fecha, name='mantenedor-fechas'),
    path('mantenedor-personas/', mantenedor_persona, name='mantenedor-personas'),
    path('mantenedor-personas-admin/', mantenedor_persona_admin, name='mantenedor-personas-admin'),
    path('mantenedor-personas-admin/<pk>/', mantenedor_persona_admin_instituto, name='mantenedor-personas-admin-inst'),
    path('add-fecha/', add_fecha, name='add-fecha'),
    path('add-fecha/<pk>/', add_fecha_admin, name='add-fecha-admin'),
    path('update-fecha/<pk>/', update_fecha, name='update-fecha'),
    path('update-fecha/<pk>/<pk_centro>/', update_fecha_admin, name='update-fecha-admin'),
    path('delete-fecha/<pk>/', delete_fecha, name='delete-fecha'),
    path('dashboard/', dashboard, name='dashboard'),
    # path('api/', include(router.urls))
]
