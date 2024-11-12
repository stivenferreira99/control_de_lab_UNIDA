from datetime import datetime
from sqlalchemy.orm import Session
from backend.models.sesion import Sesion  # Asegúrate de que Sesion esté bien importado
from backend.models.equipo import Equipo  # Asegúrate de que Equipo esté bien importado
from backend.db import get_db_connection





class laboratorio:
    @staticmethod
    def cerrar_sesiones_laboratorio(nombre_laboratorio):
        connection = get_db_connection()
        if connection is None:
            return {"status": "error", "message": "No se pudo obtener la conexión a la base de datos."}

        cursor = connection.cursor()

        try:
            # Consulta para seleccionar las sesiones activas y unirlas con el equipo
            cursor.execute("""
                SELECT sesion.id_sesion, sesion.id_equipo
                FROM sesion
                INNER JOIN equipo ON sesion.id_equipo = equipo.id_equipo
                WHERE equipo.Laboratorio = %s AND sesion.estado = 'activo'
            """, (nombre_laboratorio,))

            sesiones_activas = cursor.fetchall()

            if not sesiones_activas:
                return {"status": "error", "message": f"No hay sesiones activas en el laboratorio '{nombre_laboratorio}'."}

            # Iterar sobre las sesiones activas para cerrarlas
            for sesion in sesiones_activas:
                id_sesion, id_equipo = sesion
                cursor.execute("""
                    UPDATE sesion
                    SET estado = 'inactivo', fecha_hora_fin = NOW()
                    WHERE id_sesion = %s
                """, (id_sesion,))

                # Cambiar el estado del equipo a 'disponible'
                cursor.execute("""
                    UPDATE equipo
                    SET estado_equipo = 'disponible'
                    WHERE id_equipo = %s
                """, (id_equipo,))

            # Confirmar los cambios en la base de datos
            connection.commit()

            # Retornar solo el mensaje de éxito
            total_cerradas = len(sesiones_activas)
            return {"status": "success", "message": f"Se cerraron {total_cerradas} sesiones activas en el laboratorio '{nombre_laboratorio}'."}

        except Exception as e:
            # Registrar el error sin rollback
            return {"status": "error", "message": f"Error al cerrar sesiones: {str(e)}"}

        finally:
            # Cerrar el cursor y la conexión
            cursor.close()
            connection.close()

        



    @staticmethod
    def obtener_sesiones_activas(cursor, nombre_laboratorio):
        """
        Obtiene todas las sesiones activas en un laboratorio específico, incluyendo la contraseña.
        """
        # Consulta SQL directa para obtener las sesiones activas en el laboratorio especificado
        query = """
            SELECT sesion.id_sesion, sesion.id_alumno, sesion.fecha_hora_inicio, sesion.estado, 
                sesion.ip_maquina, sesion.nombre_pc, sesion.usuario, sesion.contrasena, 
                equipo.nombre_pc
            FROM sesion
            JOIN equipo ON sesion.id_equipo = equipo.id_equipo
            WHERE sesion.estado = 'activo' AND equipo.Laboratorio = %s
        """
        cursor.execute(query, (nombre_laboratorio,))
        sesiones = cursor.fetchall()

        # Procesar los resultados en un formato de lista de diccionarios
        sesiones_activas = [
            {
                "id_sesion": sesion[0],
                "id_alumno": sesion[1],
                "fecha_hora_inicio": sesion[2],
                "estado": sesion[3],
                "ip_maquina": sesion[4],
                "nombre_pc": sesion[5],
                "usuario": sesion[6],
                "contrasena": sesion[7],
                "nombre_equipo": sesion[8]
            }
            for sesion in sesiones
        ]

        return sesiones_activas
