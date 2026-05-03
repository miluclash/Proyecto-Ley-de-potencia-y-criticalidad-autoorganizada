# PREGUNTAS

## 1. El endpoint `/api/simulations/{id}/step/` usa POST en lugar de GET, aunque podría parecer que solo "lee" el siguiente estado. Explica por qué POST es la elección correcta según la semántica HTTP. ¿Qué propiedad de GET se viola si lo implementaras con ese método?

El método GET de HTTP se utiliza para obtener datos del servidor enviando parámetros mediante la URL. Una de las propiedades más importantes de GET es que es **seguro**. Esto quiere decir que no modifica nada de los datos del servidor. El método POST en cambio sirve para enviar datos al servidor, lo cual provoca cambios en la información del servidor. Eso es exactamente lo que ocurre aquí: cada llamada a `/step/` avanza el estado de la simulación, modifica el campo `grid`, incrementa `steps` y guarda el objeto en base de datos:

```python
# simulationForest/views.py
class SimulationStepView(APIView):
    def post(self, request, id):
        simulation = Simulation.objects.get(id=id)
        grid = np.array(simulation.grid)
        steps = request.data.get('steps', 1)
        for _ in range(steps):
            grid = step(grid, simulation.p, simulation.f)
        simulation.grid = grid.tolist()
        simulation.steps += steps
        simulation.save()          # <-- efecto de escritura en BD
        ...
```

Si se usara GET en vez de POST se violaría la propiedad de **seguridad** del método GET: produciría efectos secundarios como la modificación inesperada de datos en el servidor. Además, los navegadores, proxies y CDNs pueden cachear respuestas GET y repetirlas sin avisar, lo que haría que la simulación avanzara de forma impredecible o, al contrario, que se sirviera la misma respuesta cacheada una y otra vez sin avanzar de verdad.

---

## 2. En este proyecto el estado de la cuadrícula vive en el servidor. Sin embargo, en la simulación original de Veritasium corre íntegramente en el navegador. ¿Dónde debería vivir el estado y por qué?

Si la simulación viviera en el navegador, peligrarían la persistencia de la simulación y la latencia: aspectos que en servidor se reducen. La simulación en servidor permite guardar una sesión y poder volver a ella cuando se desee, ya que toda la información reside en la base de datos. En una web sin backend eso no sería posible, porque el navegador no tiene memoria persistente entre sesiones.

Además, si el cálculo fuera en cliente, la latencia aumentaría de cara a operaciones que sí requieren servidor (guardar, consultar historial). Para este proyecto se pedía explícitamente que las simulaciones se guardaran, lo cual se implementó con un UUID como clave primaria y campos de estadísticas persistentes:

```python
# simulationForest/models.py
class Simulation(models.Model):
    id             = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    p              = models.FloatField()
    f              = models.FloatField()
    size           = models.IntegerField()
    grid           = models.JSONField()
    steps          = models.IntegerField(default=0)
    fire_histogram = models.JSONField(default=list)
```

El UUID garantiza que cada simulación tiene un identificador único y estable que el cliente puede usar para reanudarla en cualquier momento. Si el estado viviera solo en el navegador, todo eso desaparecería al cerrar la pestaña.

---

## 3. ¿Qué ocurre con el tamaño medio de los incendios si aumentas `p` manteniendo `f` constante? ¿Y si mantienes constante el cociente `p/f` pero aumentas ambos valores proporcionalmente?

En mi simulación mantengo `p = 0.1` y `f = 0.0001`. Incrementaré `p` a `0.3`, `0.6`, `0.9` y `1.2` manteniendo `f` a su valor inicial.

- Con `p = 0.1` los incendios se generan pequeños al inicio y luego se generan incendios más grandes, pero estos desaparecen tras un tiempo generando incendios pequeños para que crezcan más árboles y se vuelvan a generar más árboles.
- Desde `p = 0.3` a `p = 0.6` los incendios y el crecimiento están en equilibrio haciendo que se generen muchos incendios pequeños, produciendo una especie de "pantalla gris" (muchos pequeños incendios y muchos árboles a la vez).
- Con `p = 0.9` se genera un equilibrio distinto en el que los árboles crecen muy rápido, dando pie a incendios muy grandes. Sin embargo, al crecer con mayor frecuencia los árboles, los incendios grandes suceden también, creando una sincronía entre crecimiento y quemado. Tras un tiempo, vuelve a aparecer la "interferencia" de muchos pequeños incendios.
- Finalmente con `p = 1.2`, al ser `p` casi 1000 veces mayor que `f`, la simulación genera árboles tan rápido que los incendios solo suceden en grandes cantidades. Es como si todo el rato se estuviera en el paso de "hay muchos árboles y por ende se genera un gran incendio". No se generan pequeños incendios.

Este comportamiento está directamente codificado en el motor de la simulación:

```python
# simulationForest/engine.py
next_grid[(grid == 0) & (num < p)] = 1   # crecimiento de árboles, controlado por p
next_grid[(grid == 1) & (~vecino_fuego) & (num < f)] = 2  # ignición por rayo, controlado por f
```

Manteniendo una relación de `p/f = 20` (por ejemplo `p = 0.02`, `f = 0.001`), los árboles crecen y se generan muchos incendios pequeños.

---

## 4. El parámetro `size` que se pasa al crear la simulación debe ser un entero entre 20 y 200. ¿Dónde validaste este valor en tu implementación y por qué elegiste ese lugar? Describe al menos dos lugares alternativos donde podrías haberlo validado y qué implicaciones tendría cada opción.

Validé `size` en la vista `SimulationView`, dentro del método `post()`, justo después de convertir los parámetros:

```python
# simulationForest/views.py
def post(self, request):
    p    = request.data.get('p')
    f    = request.data.get('f')
    size = request.data.get('size')

    if not (20 <= size <= 200):
        return Response({'error': 'size must be between 20 and 200'}, status=400)
```

Lo puse ahí porque es el punto de entrada de la petición HTTP. Si el dato es inválido, no tiene sentido seguir: no se toca el motor, no se crea nada en base de datos, y el cliente recibe un `400` claro.

Hay otros dos sitios donde podría haber validado:

**En el serializer.** DRF permite añadir validación en `validate_size()`. La ventaja es que centraliza la lógica de validación junto al resto del modelo, y reutilizas esa validación si el serializer se usa en otro contexto. El inconveniente es que mezcla responsabilidades: un serializer debería transformar datos, no aplicar reglas de negocio.

```python
# simulationForest/serializers.py  (alternativa no implementada)
class SimulationSerializer(serializers.ModelSerializer):
    def validate_size(self, value):
        if not (20 <= value <= 200):
            raise serializers.ValidationError('size must be between 20 and 200')
        return value
```

**En el modelo.** Podría usar `MinValueValidator` y `MaxValueValidator` en el campo `size`. Esto tiene la ventaja de que la restricción está en la capa más baja y se aplica siempre, incluso si alguien llama a `Simulation.objects.create()` directamente sin pasar por la vista. El problema es que Django no lanza esos validators automáticamente al hacer `.create()`: hay que llamar a `.full_clean()` manualmente, lo cual es fácil de olvidar.

En el frontend también tengo `min="20" max="200"` en el `<input>` HTML, pero eso no es validación real: cualquiera puede mandar una petición directa con `curl` o Postman. La validación del cliente es orientativa, nunca suficiente por sí sola.

---

## 5. El proyecto se gestiona con `uv` y `pyproject.toml`. ¿Qué ventaja tiene este enfoque frente a un `requirements.txt` generado con `pip freeze`? Explica la diferencia entre dependencias directas y transitivas y cómo las trata cada herramienta.

En mi `pyproject.toml` solo aparecen los paquetes que yo añadí con `uv add`: `django`, `djangorestframework`, `numpy` y `requests`. Esos son mis **dependencias directas**:

```toml
# pyproject.toml
[project]
dependencies = [
    "django>=6.0.4",
    "djangorestframework>=3.17.1",
    "numpy>=2.4.4",
    "requests>=2.33.1",
]
```

Si ejecuto `pip freeze` en el mismo entorno, aparecen 30-40 paquetes. La mayoría no los pedí yo: llegaron porque los míos los necesitaban internamente. Esos son las **dependencias transitivas**.

El problema de `pip freeze` es que mezcla todo en una lista plana sin distinción. No sabes qué es tuyo y qué llegó de rebote. Si quieres actualizar `django` en seis meses, no tienes manera de saber qué otras entradas del `requirements.txt` dependen de él. Es un fichero que da miedo tocar.

`uv` lo separa. Las dependencias directas van en `pyproject.toml` (las controlo yo). Las transitivas las resuelve `uv` solo y las fija en `uv.lock`, que sí incluye todo con versiones exactas para reproducibilidad. El `uv.lock` está pensado para ser generado automáticamente, no editado a mano, al contrario que un `requirements.txt` de `pip freeze`, que acabas editando a mano y rompiendo cosas sin querer.
