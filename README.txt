# Proyecto de Control de Acceso a Laboratorios

## Descripción
Este proyecto tiene como objetivo implementar un sistema de control de acceso para laboratorios universitarios. Permite a los estudiantes iniciar y finalizar sesiones en máquinas específicas, así como consultar sus sesiones activas. El sistema utiliza un backend en Flask con una base de datos MySQL para el almacenamiento de datos.

## Estructura del Proyecto

- `app.py`: Archivo principal que inicializa la aplicación Flask y registra los blueprints.
- `backend/`: Carpeta que contiene la lógica del backend, incluyendo modelos y la conexión a la base de datos.
  - `db.py`: Módulo para la conexión a la base de datos.
  - `models/`: Carpeta que contiene los modelos de la base de datos.
    - `alumno.py`: Modelo para la tabla de alumnos.
    - `maquina.py`: Modelo para la tabla de máquinas.
    - `sesion.py`: Modelo para la tabla de sesiones.
- `routes/`: Carpeta que contiene las rutas de la API.
  - `auth.py`: Rutas de autenticación.
  - `session.py`: Rutas relacionadas con las sesiones de los alumnos.
  - `admin.py`: Rutas de administración (si aplica).

## Requisitos

- Python 3.x
- Flask
- SQLAlchemy
- MySQL
- jwt (Flask-JWT-Extended)

## Instalación

1. Clona el repositorio:

2. Navega al directorio del proyecto:

3. Instala las dependencias:
pip install -r requirements.txt



4. Configura tu base de datos MySQL y actualiza la conexión en `db.py`.

## Uso

1. Inicia la aplicación Flask:

2. Realiza peticiones a la API utilizando herramientas como Postman o CURL.

### Ejemplos de Rutas:

- Iniciar sesión:
**Payload:**
```json
{
    "matricula": "123456",
    "id_maquina": "MAQ001",
    "ip_maquina": "192.168.0.2",
    "nombre_usuario": "usuario"
}


Finalizar sesión:

POST /end
