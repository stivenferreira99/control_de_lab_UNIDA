# insert_data.py

from db import SessionLocal, init_db
from models.alumno import Alumno
from models.sesion import Sesion
from sqlalchemy.exc import IntegrityError

# Inicializa la base de datos
init_db()

# Crea una sesión
db = SessionLocal()

# Datos de prueba
nuevo_alumno = {
    "matricula": "2018101068",
    "nombre": "Juan",
    "apellido": "Pérez"
}

try:
    # Agregar un alumno
    Alumno.crear_alumno(db, nuevo_alumno['matricula'], nuevo_alumno['nombre'], nuevo_alumno['apellido'])

    # Agregar una sesión
    Sesion.crear_sesion(db, nuevo_alumno['matricula'])

except IntegrityError as e:
    db.rollback()  # Realiza un rollback en caso de error
    print(f"Error de integridad: {str(e)}")
except Exception as e:
    db.rollback()  # Realiza un rollback en caso de otro error
    print(f"Error al insertar datos: {str(e)}")
finally:
    # Cierra la sesión
    db.close()
