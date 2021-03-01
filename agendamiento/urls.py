from django.contrib import admin
from django.urls import path, include
from  app.views import  index, reserva

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/', include('app.urls')),
    path('', index, name='index'),
    path('reserva/<pk>/', reserva, name='reserva'),

]
