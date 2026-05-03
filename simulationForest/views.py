from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from .weather import get_weather_params
from .engine import create_grid, step, get_stats
from .models import Simulation
from .serializers import SimulationSerializer
import numpy as np

class SimulationView(APIView):
    """Vista para manejar la creación de simulaciones de incendios forestales.
    Permite crear una nueva simulación mediante una solicitud POST con los parámetros necesarios.
    
    Parámetros esperados en la solicitud POST:
- p (float): Probabilidad de crecimiento de un árbol en un espacio vacío.
- f (float): Probabilidad de que un árbol prenda fuego por un rayo, incluso sin vecinos en llamas.  
- size (int): Tamaño de la matriz que representa el bosque (N x N).
    Respuesta:
    - En caso de éxito: JSON con un mensaje de confirmación y los datos de la simulación creada.
    - En caso de error: JSON con un mensaje de error.
    """
    
    def post(self, request):
        p = request.data.get('p')
        f = request.data.get('f')
        size = request.data.get('size')
        if not (20 <= size <= 200):
            return Response({'error': 'size must be between 20 and 200'}, status=400)
        if p is None or f is None or size is None:
            return Response({'error': 'Missing parameters'}, status=400)
        
        try:
            p = float(p)
            f = float(f)
            size = int(size)
        except ValueError:
            return Response({'error': 'Invalid parameter types'}, status=400)
        
        grid = create_grid(size)
        simulation = Simulation.objects.create(p=p, f=f, size=size, grid=grid.tolist())
        data_serialized = SimulationSerializer(simulation).data
        
        return Response({'message': 'Simulation created', 'data': data_serialized}, status=201)

class SimulationDetailView(APIView):
    """Vista para manejar la consulta, eliminación y modificación de una simulación específica.
    Permite consultar, eliminar o modificar una simulación mediante solicitudes GET, DELETE o PATCH con el ID de la simulación.
    Parámetros esperados:
- id (str): ID de la simulación.
    Respuesta:
    - En caso de éxito (GET): JSON con los detalles completos de la simulación.
    - En caso de éxito (DELETE): JSON con un mensaje de confirmación de eliminación.
    - En caso de éxito (PATCH): JSON con los detalles actualizados de la simulación.
    - En caso de error: JSON con un mensaje de error.
    """
    
    def get(self, request, id):
        try:
            simulation = Simulation.objects.get(id=id)
        except Simulation.DoesNotExist:
            return Response({'error': 'Simulation not found'}, status=404)
        return Response(SimulationSerializer(simulation).data, status=200)

    def delete(self, request, id):
        try:
            simulation = Simulation.objects.get(id=id)
            simulation.delete()
            return Response({'message': 'Simulation deleted'}, status=200)
        except Simulation.DoesNotExist:
            return Response({'error': 'Simulation not found'}, status=404)

    def patch(self, request, id):
        try:
            simulation = Simulation.objects.get(id=id)
            p = request.data.get('p')
            f = request.data.get('f')
            if p is not None:
                simulation.p = float(p)
            if f is not None:
                simulation.f = float(f)
            simulation.save()
            return Response(SimulationSerializer(simulation).data, status=200)
        except Simulation.DoesNotExist:
            return Response({'error': 'Simulation not found'}, status=404)


class SimulationStepView(APIView):
    """Vista para manejar la simulación de un paso en una simulación específica.
    Permite simular un paso en una simulación mediante una solicitud POST con el ID de la simulación.
    
    Parámetros esperados en la solicitud POST:
- id (str): ID de la simulación.
    Respuesta:
    - En caso de éxito: JSON con los detalles actualizados de la simulación después de simular un paso.
    - En caso de error: JSON con un mensaje de error.   
    """
    
    def post(self, request, id):
        try:
            simulation = Simulation.objects.get(id=id)
        except Simulation.DoesNotExist:
            return Response({'error': 'Simulation not found'}, status=404)
        
        grid = np.array(simulation.grid)
        steps = request.data.get('steps', 1)  # Obtener el número de pasos a simular, por defecto 1
        for _ in range(steps):
            grid = step(grid, simulation.p, simulation.f)
        
        simulation.grid = grid.tolist()  # ← aquí
        simulation.steps += steps
        simulation.save()
        
        data_serialized = SimulationSerializer(simulation).data
        return Response(data_serialized, status=200)



class WeatherView(APIView):
    """Vista para manejar la consulta del clima actual de una ciudad.
    Permite consultar el clima actual de una ciudad mediante una solicitud GET con el nombre de la
    ciudad como parámetro de consulta.
    Parámetros esperados en la solicitud GET:
    - city (str): Nombre de la ciudad para la cual se desea consultar el clima.
    Respuesta:
        - En caso de éxito: JSON con los parámetros climáticos actuales de la ciudad consultada.
        - En caso de error: JSON con un mensaje de error.
        """
        
    def get(self, request):
        city = request.query_params.get('city')
        if not city:
            return Response({'error': 'Missing city parameter'}, status=400)
        
        result = get_weather_params(city)
        return Response(result, status=200)

def index(request):
    """Vista para renderizar la página principal de la aplicación."""
    return render(request, 'index.html')