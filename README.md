# weather-cli

Aplicación de línea de comandos en Python que muestra el tiempo actual y la previsión de 7 días de cualquier ciudad. Basada en el tutorial de freeCodeCamp [How to Build a Command Line Weather App with Python](https://www.freecodecamp.org/news/how-to-build-a-command-line-weather-app-with-python/).

Usa la API gratuita de [Open-Meteo](https://open-meteo.com/), que **no requiere API key**.

## Requisitos

- [Docker](https://www.docker.com/) instalado y en marcha
- Conexión a internet

No necesitas instalar Python ni crear un entorno virtual: todo va dentro de la imagen de Docker.

## Arrancar y parar

Esta app **no es un servicio que se quede encendido**: cada vez que ejecutas el comando se crea un contenedor, consulta el tiempo, imprime el resultado y se apaga y se borra solo (por eso lleva `--rm`). No hay nada que parar después de una consulta normal.

### 1. Arrancar Docker

Abre la aplicación **Docker Desktop** y espera a que indique que está en marcha. Si no está arrancado, los comandos fallan con `Cannot connect to the Docker daemon`. Para comprobarlo:

```bash
docker info
```

### 2. Construir la imagen (una sola vez)

Desde la carpeta del proyecto:

```bash
docker build -t weather-cli .
```

Repite este comando cada vez que cambies `weather.py` o `requirements.txt`; si no, seguirás ejecutando la versión antigua.

### 3. Ejecutar

```bash
docker run --rm weather-cli Madrid
```

### 4. Parar

| Situación | Qué hacer |
|---|---|
| Consulta normal | Nada: el contenedor termina solo en un par de segundos. |
| Se queda colgada (por ejemplo, sin red) | `Ctrl+C` en la terminal. |
| Quieres comprobar si queda algo en marcha | `docker ps` |
| Hay un contenedor en marcha que quieres parar | `docker stop <id>` (el id sale en `docker ps`) |
| Terminaste de usar Docker | Cierra Docker Desktop (menú de la ballena → *Quit Docker Desktop*). |

### Limpiar (opcional)

Para borrar la imagen y liberar espacio:

```bash
docker rmi weather-cli
```

## Uso

```bash
docker run --rm weather-cli <ciudad>
```

Los nombres con espacios no necesitan comillas:

```bash
docker run --rm weather-cli Madrid
docker run --rm weather-cli New York
```

### Ciudades con nombre repetido

Si hay varias ciudades con el mismo nombre (por ejemplo, Springfield), añade la región después de una coma y **pon todo entre comillas**:

```bash
docker run --rm weather-cli "Springfield, Massachusetts"
docker run --rm weather-cli "Springfield, Illinois"
```

La coma es necesaria: `Springfield Massachusetts` sin coma da `City not found`. La salida muestra la región y el país elegidos (`Springfield, Massachusetts, United States`), así que puedes comprobar que es la ciudad que buscabas.

### Unidades

Por defecto usa unidades métricas (°C, km/h, mm). Con `-u imperial` (o `--units imperial`) usa °F, mph y pulgadas:

```bash
docker run --rm weather-cli -u imperial "Springfield, Illinois"
```

Las opciones van **antes del nombre de la ciudad**. Para ver la ayuda:

```bash
docker run --rm weather-cli --help
```

### Ejemplo de salida

```
Madrid, Spain: 19.0°C (feels like 17.0°C), humidity 38%, wind 4.6 km/h
☀️ Clear sky

7-day forecast:
  Sun 01 Nov: ⛅ Partly cloudy, 8.0°C / 20.3°C, rain 0.0 mm
  Mon 02 Nov: 🌤️ Mainly clear, 6.4°C / 18.8°C, rain 0.0 mm
  ... (hasta completar 7 días)
```

- **Primera línea:** ciudad, región y país encontrados (la región se omite si coincide con el nombre de la ciudad), temperatura, sensación térmica, humedad y viento.
- **Segunda línea:** descripción del tiempo actual con su icono.
- **Previsión:** una línea por día con la descripción, la temperatura mínima / máxima y la lluvia acumulada.

Los valores cambian según el momento de la consulta.

### Casos especiales

| Situación | Resultado |
|---|---|
| Sin ciudad, o unidades no válidas | Mensaje `usage: ...` de `argparse` con el error |
| Ciudad no encontrada | `City not found: <ciudad>` |
| Sin conexión o API caída | Mensaje de error de conexión |
| Respuesta inesperada de la API | Mensaje de error al leer los datos |

## Alternativa: ejecutar sin Docker

Si prefieres no usar Docker, necesitas Python 3.8 o superior y un entorno virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate        # macOS / Linux (Windows: .venv\Scripts\activate)
pip install -r requirements.txt
python weather.py Madrid
```

Activa el entorno cada vez que abras una terminal nueva, y desactívalo con `deactivate` cuando termines.

## Cómo funciona

1. **Geocodificación:** `get_location()` consulta `https://geocoding-api.open-meteo.com/v1/search` con el nombre de la ciudad y devuelve el primer resultado (nombre, región, país, latitud y longitud).
2. **Tiempo y previsión:** `get_weather()` consulta `https://api.open-meteo.com/v1/forecast` en una sola petición con esas coordenadas. Pide el tiempo actual (`temperature_2m`, `apparent_temperature`, `relative_humidity_2m`, `wind_speed_10m`, `weather_code`) y la previsión diaria de 7 días (`weather_code`, `temperature_2m_max`, `temperature_2m_min`, `precipitation_sum`), con `timezone=auto`. Si usas `-u imperial`, añade `temperature_unit`, `wind_speed_unit` y `precipitation_unit`.
3. **Descripción:** `describe_weather_code()` traduce el `weather_code` (códigos estándar WMO) a un texto con icono usando el diccionario `WEATHER_CODES`. Si el código es desconocido, muestra `❓ Unknown conditions`.
4. **Previsión:** `print_forecast()` imprime una línea por día.
5. **Salida:** `parse_args()` (con `argparse`) lee la ciudad y las unidades; `main()` junta las palabras de la ciudad, llama a las funciones anteriores, imprime el resultado y gestiona los errores.

## Estructura del proyecto

```
weather-cli/
├── weather.py         # Código de la aplicación
├── requirements.txt   # Dependencias (requests)
├── Dockerfile         # Imagen de Docker (python:3.12-slim)
├── .dockerignore      # Archivos que no se copian a la imagen
├── .gitignore
├── LICENSE            # Licencia MIT
└── README.md
```

## Limitaciones

- Solo usa el primer resultado de la búsqueda, así que ciudades con nombres repetidos pueden devolver una distinta de la esperada. Por ejemplo, "Londres" se resuelve como Londres (Argentina). El país que se muestra ayuda a detectarlo; para forzar otra ciudad, prueba con el nombre en inglés (`London`) o añade la región (`"Springfield, Massachusetts"`).- Solo hay dos sistemas de unidades (métrico e imperial); no se pueden mezclar, por ejemplo °C con mph.
- La previsión es siempre de 7 días, sin opción para cambiarlo, y solo diaria (no por horas).
- Los iconos son emojis: su aspecto depende de la fuente de tu terminal.

## Ideas para ampliar

- Permitir elegir entre varios resultados de la búsqueda cuando hay ciudades con el mismo nombre.
- Elegir el número de días de previsión y añadir previsión por horas.

## Licencia y créditos

Código bajo licencia [MIT](LICENSE). Datos meteorológicos de [Open-Meteo](https://open-meteo.com/) (uso no comercial gratuito, consulta sus términos). Proyecto basado en el tutorial de freeCodeCamp enlazado arriba.
