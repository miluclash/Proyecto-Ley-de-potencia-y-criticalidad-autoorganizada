from django.contrib import admin
from django.urls import path
from . import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/simulations/', views.SimulationView.as_view(), name='simulation-create'), #Crear nueva simulación --POST
    path('api/simulations/<str:id>/', views.SimulationDetailView.as_view(), name='simulation-detail'), #Devuelve el estado actual por completo de la simulación con el ID especificado --GET
    # Elimina la simulación con el ID especificado --DELETE
    #Modifica la simulacion en caliente --PATCH
    
    path('api/simulations/<str:id>/step/', views.SimulationStepView.as_view(), name='simulation-step'), # Avanza N pasos en la simulación con el ID especificado --POST   
    path('api/weather/?city=<str:city_name>/', views.WeatherView.as_view(), name='weather'), #Consulta el clima actual de una ciudad --GET
    path('', views.index, name='index'), #Vista para renderizar la página principal de la aplicación --GET
]
