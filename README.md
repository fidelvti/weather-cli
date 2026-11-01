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

## Referencia rápida de opciones

Sintaxis completa (con todas las opciones a la vez):

```bash
docker run [-it] --rm weather-cli [-h] [-u {metric,imperial}] [-c] [-H N] [-g] [-l {en,es}] [--no-color] <ciudad>
```

| Opción | Larga | Valor | Por defecto | Qué hace |
|---|---|---|---|---|
| `-h` | `--help` | — | — | Muestra la ayuda y sale. |
| `-u` | `--units` | `metric` o `imperial` | `metric` | Unidades: métrico (°C, km/h, mm) o imperial (°F, mph, in). |
| `-c` | `--choose` | — | desactivado | Si hay varios lugares con ese nombre, los lista (hasta 10) y te deja elegir uno. **Requiere `-it` en Docker.** |
| `-H` | `--hours` | `N` (1–48) | desactivado | Añade la previsión de las próximas N horas. |
| `-g` | `--graph` | — | desactivado | Muestra la temperatura por horas como gráfico de barras. Si no pones `-H`, usa 24 horas. |
| `-l` | `--lang` | `en` o `es` | `en` | Idioma de la salida: textos, descripciones del tiempo, días, meses y nombres de lugares. |
| — | `--no-color` | — | colores activados | Desactiva los colores. También se desactivan si existe la variable de entorno `NO_COLOR`. |
| — | — | `<ciudad>` | obligatorio | Nombre de la ciudad; puede llevar espacios. Añade la región tras una coma, entre comillas, para desambiguar: `"Springfield, Massachusetts"`. |

Reglas:
- Las opciones van **antes** de la ciudad, y se pueden combinar en cualquier orden.
- `-it` solo es necesario con `-c`; en el resto de casos no hace falta.
- La previsión de 7 días se muestra siempre.

Ejemplos:

```bash
docker run --rm weather-cli Madrid                                   # lo básico
docker run --rm weather-cli "Springfield, Illinois"                  # con región
docker run --rm weather-cli -u imperial New York                     # en °F, mph
docker run --rm weather-cli -H 12 Madrid                             # + próximas 12 horas
docker run -it --rm weather-cli -c Springfield                       # elegir entre varios
docker run --rm weather-cli -g Madrid                                # gráfico de temperatura (24 h)
docker run --rm weather-cli -l es Madrid                             # en español
docker run --rm weather-cli --no-color Madrid > tiempo.txt           # sin colores (para guardar en un archivo)
docker run -it --rm weather-cli -c -H 12 -u imperial -l es London    # todo combinado
```

Para ver esta misma referencia desde la propia app:

```bash
docker run --rm weather-cli --help
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

### Elegir entre varios resultados

Con `-c` (o `--choose`) la app lista hasta 10 lugares que coinciden con el nombre y te deja elegir uno por número (con Enter eliges el primero):

```bash
docker run -it --rm weather-cli -c Springfield
```

```
Several places match:
  1. Springfield, Missouri, United States (pop. 170,188)
  2. Springfield, Illinois, United States (pop. 114,394)
  3. Springfield, Massachusetts, United States (pop. 154,341)
  ...
Choose 1-10 (Enter = 1): 3
```

**Importante:** esta opción es interactiva, así que con Docker necesitas `-it` (`docker run -it --rm ...`). Sin `-it` la app avisa y no hace nada. Sin `-c` sigue usando el primer resultado.

### Previsión por horas

Con `-H N` (o `--hours N`) añade la previsión de las próximas N horas (de 1 a 48), con descripción, temperatura y probabilidad de lluvia. Va después del tiempo actual y antes de la previsión de 7 días:

```bash
docker run --rm weather-cli -H 6 Madrid
```

```
Next 6 hours:
  Sun 19:00: ☀️ Clear sky, 17.8°C, rain chance 0%
  Sun 20:00: ☀️ Clear sky, 16.5°C, rain chance 0%
  ...
```

### Unidades

Por defecto usa unidades métricas (°C, km/h, mm). Con `-u imperial` (o `--units imperial`) usa °F, mph y pulgadas:

```bash
docker run --rm weather-cli -u imperial "Springfield, Illinois"
```

Las opciones se pueden combinar y van **antes del nombre de la ciudad**:

```bash
docker run -it --rm weather-cli -c -H 12 -u imperial London
```

Para ver la ayuda:

```bash
docker run --rm weather-cli --help
```

### Ejemplo de salida

```
Madrid, Spain: 19.0°C (feels like 17.0°C), humidity 38%, wind 4.6 km/h, UV 2.1
☀️ Clear sky

7-day forecast:
  Sun 01 Nov: ⛅ Partly cloudy, 8.0°C / 20.3°C, rain 0.0 mm, UV 4.0
  Mon 02 Nov: 🌤️ Mainly clear, 6.4°C / 18.8°C, rain 0.0 mm, UV 3.9
  ... (hasta completar 7 días)
```

- **Primera línea:** ciudad, región y país encontrados (la región se omite si coincide con el nombre de la ciudad), temperatura, sensación térmica, humedad, viento e índice UV.
- **Segunda línea:** descripción del tiempo actual con su icono.
- **Previsión:** una línea por día con la descripción, la temperatura mínima / máxima, la lluvia acumulada y el UV máximo.

Los valores cambian según el momento de la consulta.

### Gráfico de temperatura por horas

Con `-g` las horas se muestran como barras proporcionales a la temperatura (la más baja del periodo tiene la barra más corta y la más alta la más larga), con el icono del tiempo y la probabilidad de lluvia:

```bash
docker run --rm weather-cli -g -l es Madrid
```

```
Próximas 24 horas:
  Dom 19:00 ███████████████████████████    17.8°C ☀️ 0%
  Dom 20:00 ████████████████████████       16.5°C ☀️ 0%
  Dom 21:00 █████████████████████          15.1°C ☀️ 0%
  ...
```

### Colores

Por defecto la salida usa colores: la temperatura va de azul (frío) a rojo (calor) y el índice UV de verde (bajo) a morado (extremo). El nombre del lugar y los títulos van en negrita, y la probabilidad de lluvia se marca en azul a partir del 50 %.

Para desactivarlos, usa `--no-color` o define la variable de entorno `NO_COLOR`:

```bash
docker run --rm weather-cli --no-color Madrid
docker run --rm -e NO_COLOR=1 weather-cli Madrid
```

Los colores se envían siempre, también cuando rediriges la salida a un archivo o a otro programa, así que en esos casos conviene usar `--no-color` para no guardar códigos de escape raros.

### Idioma

`-l es` muestra los textos, las descripciones del tiempo, los días, los meses y los nombres de los lugares en español; `-l en` (por defecto) en inglés. Por ejemplo, `-l es` convierte `Clear sky` en `Cielo despejado` y `Sun` en `Dom`.

```bash
docker run --rm weather-cli -l es Madrid
```

### Casos especiales

| Situación | Resultado |
|---|---|
| Sin ciudad, unidades no válidas o `-H` fuera de 1–48 | Mensaje `usage: ...` de `argparse` con el error |
| `-c` sin terminal interactiva (Docker sin `-it`) | Aviso pidiendo usar `docker run -it` |
| Ctrl+C o Ctrl+D al elegir con `-c` | Sale sin mostrar nada más |
| Idioma distinto de `en` o `es` | Mensaje de error de `argparse` |
| Ciudad no encontrada | `City not found: <ciudad>` (o `Ciudad no encontrada` con `-l es`) |
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

1. **Geocodificación:** `search_locations()` consulta `https://geocoding-api.open-meteo.com/v1/search` con el nombre de la ciudad (1 resultado, o 10 con `-c`). Cada resultado trae nombre, región, país, población, latitud y longitud. Con `-c`, `choose_location()` muestra la lista y pide un número.
2. **Tiempo y previsión:** `get_weather()` consulta `https://api.open-meteo.com/v1/forecast` en una sola petición con esas coordenadas. Pide el tiempo actual (`temperature_2m`, `apparent_temperature`, `relative_humidity_2m`, `wind_speed_10m`, `weather_code`, `uv_index`) y la previsión diaria de 7 días (`weather_code`, `temperature_2m_max`, `temperature_2m_min`, `precipitation_sum`, `uv_index_max`), con `timezone=auto`. Si usas `-u imperial`, añade `temperature_unit`, `wind_speed_unit` y `precipitation_unit`.
3. **Descripción:** `describe_weather_code()` traduce el `weather_code` (códigos estándar WMO) a un icono (`ICONS`) y un texto en el idioma elegido (`DESCRIPTIONS`). Si el código es desconocido, muestra `❓` y un aviso.
4. **Previsión:** `print_current()` imprime el tiempo actual, `print_hourly()` (solo con `-H` o `-g`, usa `forecast_hours`) una línea por hora o una barra por hora, y `print_forecast()` una línea por día.
5. **Colores:** `paint()` añade códigos de color ANSI; `temp_color()` y `uv_color()` eligen el color según el valor. Con `--no-color` o `NO_COLOR`, `paint()` devuelve el texto sin tocar.
6. **Idioma:** el diccionario `TEXTS` guarda los textos de cada idioma; la búsqueda de lugares usa el parámetro `language` de la API de geocodificación.
7. **Salida:** `parse_args()` (con `argparse`) lee las opciones; `main()` junta las palabras de la ciudad, llama a las funciones anteriores, imprime el resultado y gestiona los errores.

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

- Sin `-c`, solo se usa el primer resultado de la búsqueda, así que ciudades con nombres repetidos pueden devolver una distinta de la esperada. El país y la región que se muestran ayudan a detectarlo; para elegir otra, usa `-c` o añade la región (`"Springfield, Massachusetts"`).
- Solo hay dos sistemas de unidades (métrico e imperial); no se pueden mezclar, por ejemplo °C con mph.
- La previsión diaria es siempre de 7 días, sin opción para cambiarlo. La horaria llega como máximo a 48 horas.
- Solo hay dos idiomas: inglés y español.
- Los iconos son emojis y los colores códigos ANSI: su aspecto depende de la fuente y la terminal.

## Ideas para ampliar

**Más datos**
- Elegir el número de días de la previsión diaria (`--days N`, hasta 16).
- Viento con dirección y rachas, presión, nubosidad y visibilidad.
- Amanecer y atardecer.
- Calidad del aire (Open-Meteo tiene una API aparte para eso).
- Avisos de lluvia: "lloverá en las próximas 3 horas".

**Uso más cómodo**
- Ciudad por defecto guardada en un archivo de configuración o en una variable de entorno (`WEATHER_CITY`), para ejecutar sin escribirla.
- Buscar por coordenadas (`--lat`, `--lon`) o por código postal.
- Guardar una lista de ciudades favoritas y ver varias a la vez.
- Un alias de shell (`alias tiempo='docker run --rm weather-cli'`) o un script `weather` que oculte el comando de Docker.
- Un `docker-compose.yml` o un `Makefile` con atajos (`make build`, `make run CITY=Madrid`).
- Autocompletado de opciones en la terminal.

**Salida**
- Salida en JSON (`--json`) para usar la app desde otros programas.
- Más idiomas (francés, alemán, portugués…).
- Desactivar los colores automáticamente cuando la salida no va a una terminal.
- Gráfico de lluvia o de viento por horas, además del de temperatura.
- Modo compacto de una sola línea, útil para barras de estado.

**Robustez y calidad**
- Reintentos y caché de resultados durante unos minutos para no repetir peticiones.
- Tests automáticos con `pytest` (sobre todo `describe_weather_code`, `format_place` y el formato de la salida) y una acción de GitHub que los ejecute.
- Mensajes de error más específicos: distinguir entre "sin red", "API caída" y "tiempo de espera agotado".
- Empaquetarlo como comando instalable con `pip` (`pyproject.toml`) y publicar la imagen en un registro de contenedores.

## Licencia y créditos

Código bajo licencia [MIT](LICENSE). Datos meteorológicos de [Open-Meteo](https://open-meteo.com/) (uso no comercial gratuito, consulta sus términos). Proyecto basado en el tutorial de freeCodeCamp enlazado arriba.
