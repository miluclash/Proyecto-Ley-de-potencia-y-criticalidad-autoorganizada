# Simulación de Incendios Forestales

Simulación del modelo de Drossel-Schwabl (autómata celular de incendios forestales) con una API REST en Django y una interfaz web en el navegador.

---

## Requisitos previos

- [Python 3.13+](https://www.python.org/downloads/)
- [uv](https://docs.astral.sh/uv/getting-started/installation/) — gestor de paquetes y entornos virtuales
- [Git](https://git-scm.com/)

Comprueba que los tienes instalados:

```bash
python --version   # Python 3.13.x
uv --version       # uv 0.x.x
git --version
```

---

## Instalación

### 1. Clona el repositorio

```bash
git clone <url-del-repositorio>
cd proyectoIncendios
```

### 2. Crea el entorno virtual e instala las dependencias

```bash
uv sync
```

`uv` leerá el `pyproject.toml` y creará automáticamente un entorno virtual en `.venv` con todas las dependencias:

- `django >= 6.0.4`
- `djangorestframework >= 3.17.1`
- `numpy >= 2.4.4`
- `requests >= 2.33.1`

### 3. Aplica las migraciones de base de datos

```bash
uv run python manage.py migrate
```

Esto crea el archivo `db.sqlite3` con la tabla de simulaciones.

### 4. Inicia el servidor de desarrollo

```bash
uv run python manage.py runserver
```

El servidor quedará disponible en `http://127.0.0.1:8000`.

---

## Uso

Abre el navegador en `http://127.0.0.1:8000` para acceder a la interfaz web.

Desde ahí puedes:

- Crear una nueva simulación indicando el tamaño de la cuadrícula (`size`, entre 20 y 200), la probabilidad de crecimiento de árboles (`p`) y la probabilidad de ignición por rayo (`f`).
- Avanzar la simulación paso a paso o en modo automático.
- Ver las estadísticas en tiempo real (densidad de árboles, fuego y casillas vacías).

---

## API REST

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/api/simulations/` | Crea una nueva simulación |
| `GET` | `/api/simulations/<id>/` | Devuelve el estado actual de una simulación |
| `POST` | `/api/simulations/<id>/step/` | Avanza N pasos la simulación |

### Ejemplo: crear una simulación

```bash
curl -X POST http://127.0.0.1:8000/api/simulations/ \
  -H "Content-Type: application/json" \
  -d '{"size": 50, "p": 0.05, "f": 0.001}'
```

Respuesta:

```json
{
  "message": "Simulation created",
  "data": {
    "id": "3f8a1c2d-...",
    "size": 50,
    "p": 0.05,
    "f": 0.001,
    "steps": 0
  }
}
```

### Ejemplo: avanzar un paso

```bash
curl -X POST http://127.0.0.1:8000/api/simulations/<id>/step/ \
  -H "Content-Type: application/json" \
  -d '{"steps": 1}'
```

---

## Tests

Para ejecutar los tests del proyecto:

```bash
uv run pytest
```

---

## Estructura del proyecto

```
proyectoIncendios/
├── core/                  # Configuración Django (settings, urls, wsgi)
├── simulationForest/      # App principal
│   ├── engine.py          # Motor de simulación (modelo Drossel-Schwabl)
│   ├── models.py          # Modelo Simulation con UUID
│   ├── serializers.py     # Serializadores DRF
│   ├── views.py           # Endpoints de la API
│   ├── urls.py            # Rutas de la app
│   ├── weather.py         # Integración con API del tiempo
│   └── templates/         # Interfaz web
├── pyproject.toml         # Dependencias y configuración del proyecto
├── uv.lock                # Versiones exactas de todas las dependencias
└── manage.py
```
