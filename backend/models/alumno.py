# models/alumno.py

from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from backend.db import Base
from sqlalchemy.exc import IntegrityError

class Alumno(Base):
    __tablename__ = 'alumnos'

    matricula = Column(String, primary_key=True)
    nombre = Column(String)
    apellido = Column(String)
    nro_cedula = Column(String)  # Agregado
    id_carrera = Column(String)  # Agregado
    id_materia = Column(String)  # Agregado

    # Relación con la tabla 'sesiones'
    sesiones = relationship("Sesion", back_populates="alumno")

    @classmethod
    def crear_alumno(cls, db_session, matricula, nombre, apellido, nro_cedula, id_carrera, id_materia):
        if not matricula or not nombre or not apellido or not nro_cedula or not id_carrera or not id_materia:
            print("Error: Faltan datos requeridos para crear el alumno.")
            return

        nuevo_alumno = cls(matricula=matricula, nombre=nombre, apellido=apellido,
                           nro_cedula=nro_cedula, id_carrera=id_carrera, id_materia=id_materia)
        try:
            db_session.add(nuevo_alumno)
            db_session.commit()
            print("Alumno creado exitosamente.")
        except IntegrityError:
            db_session.rollback()
            print(f"Error: El alumno con matrícula {matricula} ya existe.")
        except Exception as e:
            db_session.rollback()
            print(f"Error al crear el alumno: {str(e)}")
