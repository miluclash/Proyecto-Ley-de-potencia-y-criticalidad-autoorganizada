#Convertir el modelo SIMULATION a JSON para las repuestas de la API
from rest_framework import serializers
from .models import Simulation
from .engine import get_stats
import numpy as np

class SimulationSerializer(serializers.ModelSerializer):
    """Serializador para el modelo Simulation, incluye un campo adicional para la densidad de árboles."""

    tree_density = serializers.SerializerMethodField()
    
    def get_tree_density(self, obj):
        obj_grid = np.array(obj.grid)   
        return get_stats(obj_grid)['tree']
    class Meta:
        model = Simulation
        fields = '__all__'
        