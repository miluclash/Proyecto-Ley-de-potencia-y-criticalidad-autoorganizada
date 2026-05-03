import uuid

from django.db import models

# Create your models here.

class Simulation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    p = models.FloatField() # Probabilidad de crecimiento de un árbol en un espacio vacío
    f = models.FloatField() # Probabilidad de que un árbol prenda fuego por un rayo, incluso sin vecinos en llamas      
    size = models.IntegerField() # Tamaño de la matriz (N x N)
    grid = models.JSONField()  # Almacena la matriz del bosque como JSON
    steps = models.IntegerField(default=0) # Número de pasos de la simulación
    fire_histogram = models.JSONField(default=list)  # Almacena el historial de fuego como JSON
    