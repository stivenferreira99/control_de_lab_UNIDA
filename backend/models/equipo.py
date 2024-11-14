# models/equipo.py

from backend.db import get_db_connection

class Equipo:
    @staticmethod
    def agregar_equipo(nombre_pc, ip_equipo, laboratorio, monitor=None, gabinete=None, teclado=None, mouse=None, receptor=None, estado_equipo="disponible"):
        connection = get_db_connection()
        if connection is None:
            return {"status": "error", "message": "No se pudo obtener la conexión a la base de datos."}

        cursor = connection.cursor()

        try:
            # Inserta un nuevo equipo en la base de datos
            cursor.execute("""
                INSERT INTO equipo (nombre_pc, monitor, gabinete, teclado, mouse, receptor, estado_equipo, IP_equipo, Laboratorio)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (nombre_pc, monitor, gabinete, teclado, mouse, receptor, estado_equipo, ip_equipo, laboratorio))

            connection.commit()
            return {"status": "success", "message": "Equipo agregado exitosamente."}

        except Exception as e:
            return {"status": "error", "message": f"Error al agregar equipo: {str(e)}"}

        finally:
            cursor.close()
            connection.close()

    @staticmethod
    def modificar_equipo(nombre_pc, ip_equipo=None, laboratorio=None, monitor=None, gabinete=None, teclado=None, mouse=None, receptor=None, estado_equipo=None):
        connection = get_db_connection()
        if connection is None:
            return {"status": "error", "message": "No se pudo obtener la conexión a la base de datos."}

        cursor = connection.cursor()

        try:
            # Construye la consulta de actualización dinámica
            updates = []
            values = []

            if ip_equipo is not None:
                updates.append("IP_equipo = %s")
                values.append(ip_equipo)
            if laboratorio is not None:
                updates.append("Laboratorio = %s")
                values.append(laboratorio)
            if monitor is not None:
                updates.append("monitor = %s")
                values.append(monitor)
            if gabinete is not None:
                updates.append("gabinete = %s")
                values.append(gabinete)
            if teclado is not None:
                updates.append("teclado = %s")
                values.append(teclado)
            if mouse is not None:
                updates.append("mouse = %s")
                values.append(mouse)
            if receptor is not None:
                updates.append("receptor = %s")
                values.append(receptor)
            if estado_equipo is not None:
                updates.append("estado_equipo = %s")
                values.append(estado_equipo)

            if not updates:
                return {"status": "error", "message": "No se proporcionaron campos para actualizar."}

            values.append(nombre_pc)

            # Ejecuta la consulta de actualización
            cursor.execute(f"""
                UPDATE equipo
                SET {', '.join(updates)}
                WHERE nombre_pc = %s
            """, tuple(values))

            connection.commit()
            return {"status": "success", "message": "Equipo modificado exitosamente."}

        except Exception as e:
            return {"status": "error", "message": f"Error al modificar equipo: {str(e)}"}

        finally:
            cursor.close()
            connection.close()

    @staticmethod
    def eliminar_equipo(nombre_pc):
        connection = get_db_connection()
        if connection is None:
            return {"status": "error", "message": "No se pudo obtener la conexión a la base de datos."}

        cursor = connection.cursor()

        try:
            # Elimina el equipo de la base de datos
            cursor.execute("DELETE FROM equipo WHERE nombre_pc = %s", (nombre_pc,))

            connection.commit()
            return {"status": "success", "message": "Equipo eliminado exitosamente."}

        except Exception as e:
            return {"status": "error", "message": f"Error al eliminar equipo: {str(e)}"}

        finally:
            cursor.close()
            connection.close()
