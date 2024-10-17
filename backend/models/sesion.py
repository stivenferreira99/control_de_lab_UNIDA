from datetime import datetime
from backend.db import get_db_connection

class Sesion:
    def __init__(self, id_maquina, matricula_alumno, inicio_sesion, fin_sesion, estado, ip_maquina, nombre_maquina, contrasena):
        self.id_maquina = id_maquina
        self.matricula_alumno = matricula_alumno
        self.inicio_sesion = inicio_sesion
        self.fin_sesion = fin_sesion
        self.estado = estado
        self.ip_maquina = ip_maquina
        self.nombre_maquina = nombre_maquina
        self.contrasena = contrasena

    @staticmethod
    def create_session(id_maquina, matricula_alumno, ip_maquina, nombre_maquina, contrasena):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Crear una nueva sesión
            cursor.execute(
                "INSERT INTO sesiones (id_maquina, matricula_alumno, inicio_sesion, estado, ip_maquina, nombre_maquina, contrasena) VALUES (%s, %s, NOW(), 'activo', %s, %s, %s)",
                (id_maquina, matricula_alumno, ip_maquina, nombre_maquina, contrasena)
            )
            conn.commit()
            return {"status": "success", "message": "Sesión creada exitosamente"}
        except Exception as e:
            print(f"Error al crear la sesión: {str(e)}")
            return {"status": "error", "message": "Error al crear la sesión"}
        finally:
            # Asegurarse de cerrar la conexión a la base de datos
            if 'conn' in locals():
                conn.close()

    @staticmethod
    def end_session(matricula_alumno, id_maquina):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            fin_sesion = datetime.now()
            cursor.execute(
                "UPDATE sesiones SET fin_sesion = %s, estado = 'inactivo' WHERE matricula_alumno = %s AND id_maquina = %s",
                (fin_sesion, matricula_alumno, id_maquina)
            )
            conn.commit()
            return {"status": "success", "message": "Sesión finalizada exitosamente"}
        except Exception as e:
            print(f"Error al finalizar la sesión: {str(e)}")
            return {"status": "error", "message": "Error al finalizar la sesión"}
        finally:
            # Asegurarse de cerrar la conexión a la base de datos
            if 'conn' in locals():
                conn.close()

    @staticmethod
    def get_active_sessions():
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id_maquina, matricula_alumno, inicio_sesion, estado FROM sesiones WHERE estado = 'activo'")
            sesiones = cursor.fetchall()
            return sesiones
        except Exception as e:
            print(f"Error al obtener sesiones activas: {str(e)}")
            return []
        finally:
            # Asegurarse de cerrar la conexión a la base de datos
            if 'conn' in locals():
                conn.close()
