from datetime import datetime
from backend.db import get_db_connection
import re

class Sesion:
    def __init__(self, id_equipo, matricula, inicio_sesion, fin_sesion, estado, ip_maquina, nombre_pc, contrasena):
        self.id_equipo = id_equipo
        self.matricula = matricula
        self.inicio_sesion = inicio_sesion
        self.fin_sesion = fin_sesion
        self.estado = estado
        self.ip_maquina = ip_maquina
        self.nombre_pc = nombre_pc
        self.contrasena = contrasena

    @staticmethod
    def validar_matricula(matricula):
        year = int(matricula[:4])
        current_year = datetime.now().year
        return re.fullmatch(r'\d{10}', matricula) and 2005 <= year <= current_year

    @staticmethod
    def verificar_existe_alumno(cursor, matricula):
        cursor.execute("SELECT matricula FROM alumno WHERE matricula = %s", (matricula,))
        return cursor.fetchone() is not None

    @staticmethod
    def verificar_existe_usuario(cursor, contrasena, matricula):
        cursor.execute("SELECT matricula FROM usuario WHERE matricula = %s AND contrasena = %s", (matricula, contrasena))
        return cursor.fetchone() is not None

    @staticmethod
    def verificar_sesion_activa(matriculas):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            for matricula in matriculas:
                cursor.execute("""
                    SELECT s.id_sesion 
                    FROM Sesion s
                    JOIN Alumno a ON s.id_alumno = a.id_alumno
                    WHERE a.matricula = %s AND s.estado = 'Activo'
                """, (matricula,))
                sesion = cursor.fetchone()
                if sesion:
                    cursor.execute("""
                        UPDATE Sesion 
                        SET estado = 'Inactivo', fecha_hora_fin = NOW() 
                        WHERE id_sesion = %s
                    """, (sesion[0],))
            conn.commit()
        except Exception as e:
            print(f"Error al verificar sesiones activas: {str(e)}")
            raise
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def crear_nueva_sesion(cursor, id_equipo, id_alumno, ip_maquina, nombre_pc, matricula, contrasena):
        """
        Crea una nueva sesión y cambia el estado del equipo a 'en uso'.
        """
        # Verificar si el equipo está disponible
        cursor.execute("""
            SELECT estado_equipo FROM equipo WHERE nombre_pc = %s
        """, (nombre_pc,))
        equipo = cursor.fetchone()

        if equipo and equipo[0] == 'en uso':
            return {"status": "error", "message": "El equipo está en uso por otra sesión."}

        # Obtener el id_alumno a partir de la matricula
        cursor.execute("""
            SELECT id_alumno FROM alumno WHERE matricula = %s
        """, (matricula,))
        alumno = cursor.fetchone()

        if not alumno:
            return {"status": "error", "message": "El alumno no está registrado."}

        # Si el equipo está disponible y el alumno existe, crear la nueva sesión
        cursor.execute("""
            INSERT INTO Sesion (id_equipo, id_alumno, contrasena, ip_maquina, nombre_pc, fecha_hora_inicio, estado)
            VALUES (%s, %s, %s, %s, %s, NOW(), 'activo')
        """, (id_equipo, alumno[0], contrasena, ip_maquina, nombre_pc))

        # Actualizar el estado del equipo a 'en uso'
        cursor.execute("""
            UPDATE equipo
            SET estado_equipo = 'en uso'
            WHERE nombre_pc = %s
        """, (nombre_pc,))
        
        return {"status": "success", "message": "Sesión creada exitosamente."}

    @staticmethod
    def create_session(id_equipo, matricula1, matricula2, ip_maquina, nombre_pc, contrasena):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Verificar si los alumnos existen
            for matricula in [matricula1, matricula2] if matricula2 else [matricula1]:
                if not Sesion.verificar_existe_alumno(cursor, matricula):
                    return {"status": "error", "message": f"El alumno con matrícula {matricula} no existe en la base de datos"}

            # Cerrar sesiones activas si existen
            Sesion.verificar_sesion_activa([matricula1, matricula2] if matricula2 else [matricula1])

            # Crear la nueva sesión
            response = Sesion.crear_nueva_sesion(cursor, id_equipo, matricula1, ip_maquina, nombre_pc, matricula1, contrasena)
            return response

        except Exception as e:
            print(f"Error al crear sesión: {str(e)}")
            return {"status": "error", "message": "Error al crear sesión"}
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def cerrar_sesion(cursor, matricula, id_equipo):
        # Verificar si el alumno está registrado
        cursor.execute("""
            SELECT COUNT(*) FROM proyectosui.alumno WHERE matricula = %s
        """, (matricula,))
        alumno_existente = cursor.fetchone()[0]

        if alumno_existente == 0:
            return {"status": "error", "message": "El alumno no está registrado."}

        # Verificar si hay una sesión activa
        cursor.execute("""
            SELECT COUNT(*) FROM proyectosui.sesion a
            JOIN proyectosui.alumno b ON a.id_alumno = b.id_alumno
            WHERE b.matricula = %s AND a.id_equipo = %s AND a.estado = 'Activo'
        """, (matricula, id_equipo))
        sesion_activa = cursor.fetchone()[0]

        if sesion_activa == 0:
            return {"status": "error", "message": "No tiene sesión activa."}

        # Cerrar la sesión si existe
        cursor.execute("""
            UPDATE proyectosui.sesion a
            JOIN proyectosui.alumno b ON a.id_alumno = b.id_alumno
            SET a.estado = 'Inactivo', a.fecha_hora_fin = NOW()
            WHERE b.matricula = %s AND a.id_equipo = %s AND a.estado = 'Activo'
        """, (matricula, id_equipo))

        cursor.execute("""
            UPDATE Equipo 
            SET estado_equipo = 'Disponible'
            WHERE id_equipo = %s
        """, (id_equipo,))

        return {"status": "success", "message": "Sesión cerrada exitosamente."}
