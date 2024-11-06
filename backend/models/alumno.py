from sqlalchemy import Column, String, Integer, Date, ForeignKey
from sqlalchemy.orm import relationship
from backend.db import Base, get_db_connection
from datetime import datetime

class Alumno(Base):
    __tablename__ = 'alumno'

    id_alumno = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    matricula = Column(String(50), nullable=False, unique=True)
    fecha_nacimiento = Column(Date, nullable=False)
    ci = Column(String(20), nullable=False)
    id_carrera = Column(Integer, ForeignKey('carrera.id_carrera'), nullable=False)

    # Relaciones
    sesiones = relationship("Sesion", back_populates="alumno")
    carrera = relationship("Carrera", back_populates="alumno")

    @classmethod
    def obtener_alumnos(cls):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id_alumno, nombre, apellido, matricula, fecha_nacimiento, ci, id_carrera
            FROM alumno
        """)
        alumnos = cursor.fetchall()
        conn.close()
        return [
            {
                "id_alumno": a[0],
                "nombre": a[1],
                "apellido": a[2],
                "matricula": a[3],
                "fecha_nacimiento": a[4],
                "ci": a[5],
                "id_carrera": a[6]
            }
            for a in alumnos
        ]

    @classmethod
    def crear_alumno(cls, matricula, nombre, apellido, fecha_nacimiento, ci, nombre_carrera):
        conn = get_db_connection()
        cursor = conn.cursor()

        # Obtener el id_carrera basado en el nombre de la carrera
        cursor.execute("""
            SELECT id_carrera FROM carrera WHERE nombre = %s
        """, (nombre_carrera,))
        carrera = cursor.fetchone()

        if not carrera:
            conn.close()
            return {"status": "not_found", "message": "La carrera no existe."}

        id_carrera = carrera[0]

        # Comprobar si el alumno ya existe
        cursor.execute("""
            SELECT id_alumno FROM alumno WHERE matricula = %s
        """, (matricula,))
        if cursor.fetchone():
            conn.close()
            return {"status": "exists", "message": "El alumno ya existe."}

        cursor.execute("""
            INSERT INTO alumno (matricula, nombre, apellido, fecha_nacimiento, ci, id_carrera)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (matricula, nombre, apellido, fecha_nacimiento, ci, id_carrera))

        conn.commit()
        conn.close()
        return {"status": "created", "message": "Alumno creado exitosamente."}

   
    @classmethod
    def actualizar_alumno(cls, matricula, nombre=None, apellido=None, ci=None, fecha_nacimiento=None, id_carrera=None):
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verificar si el alumno existe
        cursor.execute("SELECT id_alumno FROM alumno WHERE matricula = %s", (matricula,))
        alumno = cursor.fetchone()
        if not alumno:
            conn.close()
            return {"status": "not_found", "message": "El alumno no está registrado"}

        # Validar y actualizar fecha de nacimiento si se proporciona
        if fecha_nacimiento:
            if isinstance(fecha_nacimiento, str):
                try:
                    # Intentar convertir la fecha al formato esperado
                    datetime.strptime(fecha_nacimiento, '%Y-%m-%d')
                except ValueError:
                    conn.close()
                    return {"status": "error", "message": "El formato de la fecha de nacimiento debe ser AAAA-MM-DD"}
            else:
                conn.close()
                return {"status": "error", "message": "Fecha de nacimiento debe ser una cadena de texto"}

            # Si la fecha es válida, ejecuta la actualización
            cursor.execute("UPDATE alumno SET fecha_nacimiento = %s WHERE matricula = %s", (fecha_nacimiento, matricula))

        # Actualizar los demás campos si se proporcionan
        if nombre:
            cursor.execute("UPDATE alumno SET nombre = %s WHERE matricula = %s", (nombre, matricula))
        if apellido:
            cursor.execute("UPDATE alumno SET apellido = %s WHERE matricula = %s", (apellido, matricula))
        if ci:
            cursor.execute("UPDATE alumno SET ci = %s WHERE matricula = %s", (ci, matricula))
        if id_carrera:
            cursor.execute("UPDATE alumno SET id_carrera = %s WHERE matricula = %s", (id_carrera, matricula))

        # Intentar hacer commit de los cambios
        try:
            conn.commit()
        except Exception as e:
            conn.close()
            return {"status": "error", "message": f"Error al actualizar el alumno: {str(e)}"}

        # Cerrar la conexión
        conn.close()

        return {"status": "success", "message": "Alumno actualizado exitosamente"}
    @classmethod
    def eliminar_alumno(cls, matricula):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id_sesion FROM sesion
            WHERE id_alumno = (SELECT id_alumno FROM alumno WHERE matricula = %s)
            AND estado = 'activo'
        """, (matricula,))
        if cursor.fetchone():
            conn.close()
            return {"status": "active_session", "message": "El alumno tiene sesiones activas."}

        cursor.execute("""
            DELETE FROM alumno WHERE matricula = %s
        """, (matricula,))
        conn.commit()
        conn.close()
        return {"status": "deleted", "message": "Alumno eliminado exitosamente."}



    @classmethod
    def existe_alumno(cls, matricula):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id_alumno FROM alumno WHERE matricula = %s", (matricula,))
        existe = cursor.fetchone() is not None
        conn.close()
        return existe
