from datetime import datetime
from backend.db import get_db_connection
import re

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
    def validar_matricula(matricula):
        year = int(matricula[:4])
        current_year = datetime.now().year
        return re.fullmatch(r'\d{10}', matricula) and 2005 <= year <= current_year

    @staticmethod
    def verificar_existe_alumno(cursor, matricula):
        cursor.execute("SELECT matricula FROM alumnos WHERE matricula = %s", (matricula,))
        return cursor.fetchone() is not None

    @staticmethod
    def verificar_existe_usuario(cursor, contrasena, matricula):
        cursor.execute("SELECT matricula FROM usuarios WHERE matricula = %s AND contrasena = %s", (matricula, contrasena))
        return cursor.fetchone() is not None

    @staticmethod
    def cerrar_sesion_anterior(cursor, matricula_alumno):
        cursor.execute("SELECT * FROM sesiones WHERE matricula_alumno = %s AND estado = 'activo'", (matricula_alumno,))
        if cursor.fetchone():
            cursor.execute(
                "UPDATE sesiones SET fin_sesion = %s, estado = 'inactivo' WHERE matricula_alumno = %s AND estado = 'activo'",
                (datetime.now(), matricula_alumno)
            )

    @staticmethod
    def crear_nueva_sesion(cursor, id_maquina, matricula_alumno, ip_maquina, nombre_maquina, contrasena):
        cursor.execute(
            "INSERT INTO sesiones (id_maquina, matricula_alumno, inicio_sesion, estado, ip_maquina, nombre_maquina, contrasena) "
            "VALUES (%s, %s, NOW(), 'activo', %s, %s, %s)",
            (id_maquina, matricula_alumno, ip_maquina, nombre_maquina, contrasena)
        )

    @staticmethod
    def create_session(id_maquina, matricula_alumno, matricula_opcional, ip_maquina, nombre_maquina, contrasena):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            if not Sesion.validar_matricula(matricula_alumno):
                return {"status": "error", "message": "Formato de matrícula no válido"}
            
            if not Sesion.verificar_existe_alumno(cursor, matricula_alumno):
                return {"status": "error", "message": "El alumno no existe en la base de datos"}

            if not Sesion.verificar_existe_usuario(cursor, contrasena, matricula_alumno):
                return {"status": "error", "message": "El usuario no existe en la base de datos"}
            
            Sesion.cerrar_sesion_anterior(cursor, matricula_alumno)
            Sesion.crear_nueva_sesion(cursor, id_maquina, matricula_alumno, ip_maquina, nombre_maquina, contrasena)

            if matricula_opcional and Sesion.validar_matricula(matricula_opcional):
                if Sesion.verificar_existe_alumno(cursor, matricula_opcional):
                    Sesion.cerrar_sesion_anterior(cursor, matricula_opcional)
                    Sesion.crear_nueva_sesion(cursor, id_maquina, matricula_opcional, ip_maquina, nombre_maquina, contrasena)
            
            conn.commit()
            return {"status": "success", "message": "Sesión creada exitosamente"}
        except Exception as e:
            print(f"Error al crear la sesión: {str(e)}")
            return {"status": "error", "message": "Error al crear la sesión"}
        finally:
            if 'conn' in locals():
                conn.close()

    @staticmethod
    def end_session(matricula_alumno, id_maquina):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE sesiones SET fin_sesion = %s, estado = 'inactivo' WHERE matricula_alumno = %s AND id_maquina = %s",
                (datetime.now(), matricula_alumno, id_maquina)
            )
            conn.commit()
            return {"status": "success", "message": "Sesión finalizada exitosamente"}
        except Exception as e:
            print(f"Error al finalizar la sesión: {str(e)}")
            return {"status": "error", "message": "Error al finalizar la sesión"}
        finally:
            if 'conn' in locals():
                conn.close()

    @staticmethod
    def get_active_sessions():
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id_maquina, matricula_alumno, inicio_sesion, estado FROM sesiones WHERE estado = 'activo'")
            return cursor.fetchall()
        except Exception as e:
            print(f"Error al obtener sesiones activas: {str(e)}")
            return []
        finally:
            if 'conn' in locals():
                conn.close()
