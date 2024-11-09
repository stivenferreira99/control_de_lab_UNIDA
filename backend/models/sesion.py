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
    def verificar_sesion_activa(cursor, matriculas):
        for matricula in matriculas:
            # Verifica si existe una sesión activa para la matrícula
            cursor.execute("""
                SELECT id_sesion, id_equipo FROM sesion 
                WHERE id_alumno = (
                    SELECT id_alumno FROM alumno WHERE matricula = %s
                ) AND estado = 'activo'
            """, (matricula,))

            sesiones = cursor.fetchall()  # Obtiene todas las sesiones activas

            # Si hay sesiones activas, actualiza a 'inactivo' y cambia el equipo a 'disponible'
            for sesion in sesiones:
                id_sesion, id_equipo = sesion  # Extrae id_sesion e id_equipo

                # Cambia el estado de la sesión a 'inactivo' y asigna la fecha/hora de finalización
                cursor.execute("""
                    UPDATE sesion 
                    SET estado = 'inactivo', fecha_hora_fin = NOW() 
                    WHERE id_sesion = %s
                """, (id_sesion,))

                # Cambia el estado del equipo a 'disponible' cuando se cierra la sesión
                cursor.execute("""
                    UPDATE equipo 
                    SET estado_equipo = 'disponible' 
                    WHERE id_equipo = %s
                """, (id_equipo,))

    @staticmethod
    def crear_nueva_sesion(cursor, nombre_maquina, matricula1, matricula2, ip_maquina, contrasena):
        # Primero verifica y cierra sesiones activas existentes
        Sesion.verificar_sesion_activa(cursor, [matricula1, matricula2] if matricula2 else [matricula1])
        
        # Obtiene el id_equipo y Laboratorio basado en el nombre de la máquina
        cursor.execute("SELECT id_equipo, Laboratorio FROM equipo WHERE nombre_pc = %s", (nombre_maquina,))
        equipo = cursor.fetchone()
        
        if not equipo:
            return {"status": "error", "message": f"El equipo con nombre {nombre_maquina} no está registrado."}
        
        id_equipo, laboratorio = equipo  # Obtén el id_equipo y el valor de Laboratorio
        
        # Si la máquina está en uso, cambia su estado a 'disponible' antes de crear la nueva sesión
        cursor.execute("""SELECT estado_equipo FROM equipo WHERE id_equipo = %s""", (id_equipo,))
        estado_equipo = cursor.fetchone()[0]

        if estado_equipo == 'en uso':
            # Cambia el estado del equipo a 'disponible' antes de crear una nueva sesión
            cursor.execute("""
                UPDATE equipo 
                SET estado_equipo = 'disponible', IP_equipo = %s
                WHERE id_equipo = %s
            """, (ip_maquina, id_equipo))  # Actualiza la IP

        # Cambia el estado del equipo a 'en uso' para la nueva sesión
        cursor.execute("""
            UPDATE equipo 
            SET estado_equipo = 'en uso', IP_equipo = %s
            WHERE id_equipo = %s
        """, (ip_maquina, id_equipo))  # Actualiza la IP

        # Recupera y verifica el id de cada alumno
        alumno_ids = []
        for matricula in [matricula1, matricula2] if matricula2 else [matricula1]:
            cursor.execute("SELECT id_alumno FROM alumno WHERE matricula = %s", (matricula,))
            alumno = cursor.fetchone()
            if not alumno:
                return {"status": "error", "message": f"La matrícula proporcionada  {matricula} no está registrada."}
            alumno_ids.append(alumno[0])

        # Crea una nueva sesión para cada alumno y agrega el Laboratorio
        for id_alumno in alumno_ids:
            cursor.execute("""
                INSERT INTO sesion (id_equipo, id_alumno, contrasena, ip_maquina, nombre_pc, fecha_hora_inicio, estado, Laboratorio)
                VALUES (%s, %s, %s, %s, %s, NOW(), 'activo', %s)
            """, (id_equipo, id_alumno, contrasena, ip_maquina, nombre_maquina, laboratorio))  # Inserta el Laboratorio
        
        return {"status": "success", "message": "Sesión creada exitosamente."}


    @staticmethod
    def cerrar_sesion(cursor, matricula, id_equipo):
        cursor.execute("""
            SELECT COUNT(*) FROM alumno WHERE matricula = %s
        """, (matricula,))
        alumno_existente = cursor.fetchone()[0]

        if alumno_existente == 0:
            return {"status": "error", "message": "El alumno no está registrado."}

        cursor.execute("""
            SELECT COUNT(*) FROM sesion s
            JOIN alumno a ON s.id_alumno = a.id_alumno
            WHERE a.matricula = %s AND s.id_equipo = %s AND s.estado = 'activo'
        """, (matricula, id_equipo))
        sesion_activa = cursor.fetchone()[0]

        if sesion_activa == 0:
            return {"status": "error", "message": "No tiene sesión activa."}

        cursor.execute("""
            UPDATE sesion s
            JOIN alumno a ON s.id_alumno = a.id_alumno
            SET s.estado = 'inactivo', s.fecha_hora_fin = NOW()
            WHERE a.matricula = %s AND s.id_equipo = %s AND s.estado = 'activo'
        """, (matricula, id_equipo))

        cursor.execute("""
            UPDATE equipo 
            SET estado_equipo = 'disponible'
            WHERE id_equipo = %s
        """, (id_equipo,))

        return {"status": "success", "message": "Sesión cerrada exitosamente."}
