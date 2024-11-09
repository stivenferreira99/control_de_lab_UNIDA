from flask import Blueprint, request, jsonify
from backend.db import get_db_connection
from backend.models.sesion import Sesion
from backend.models.auth import token_required
from datetime import datetime

session_blueprint = Blueprint('sesion', __name__)

@session_blueprint.route('/consulta_session/<string:matricula>', methods=['GET'])
@token_required
def consulta_session(matricula):
    if not matricula:
        return jsonify({"status": "error", "message": "Faltan datos requeridos"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if not Sesion.validar_matricula(matricula):
            return jsonify({"status": "error", "message": "Formato de matrícula incorrecta"}), 400

        cursor.execute("""
            SELECT id_alumno FROM alumno WHERE matricula = %s
        """, (matricula,))
        alumno = cursor.fetchone()
        if not alumno:
            return jsonify({"status": "error", "message": "El alumno no existe en la base de datos"}), 404

        cursor.execute("""
            SELECT s.id_sesion, s.id_equipo, s.estado, s.fecha_hora_inicio, s.fecha_hora_fin
            FROM sesion s
            JOIN alumno a ON s.id_alumno = a.id_alumno
            WHERE a.matricula = %s AND s.estado = 'activo'
        """, (matricula,))
        sesiones = cursor.fetchall()

        if not sesiones:
            return jsonify({"status": "error", "message": "No hay sesiones activas para el alumno"}), 404

        sesiones_activas = [
            {
                "id_sesion": sesion[0],
                "id_equipo": sesion[1],
                "estado": sesion[2],
                "inicio_sesion": sesion[3],
                "fin_sesion": sesion[4] if sesion[4] else None,
                "tiempo_activo": str(datetime.now() - sesion[3]) if sesion[2] == 'activo' else None
            }
            for sesion in sesiones
        ]

        return jsonify({"status": "success", "sesiones_activas": sesiones_activas}), 200

    except Exception as e:
        print(f"Error al procesar la solicitud: {str(e)}")
        return jsonify({"status": "error", "message": "Error interno del servidor"}), 500
    finally:
        conn.close()

@session_blueprint.route('/crear_sesion', methods=['POST'])
@token_required  # Agregamos el decorador para verificar el token
def crear_sesion():
    # Obtén los datos del cuerpo de la solicitud
    data = request.get_json()
    nombre_maquina = data.get('nombre_maquina')
    matricula1 = data.get('matricula1')
    matricula2 = data.get('matricula2', None)  # matricula2 es opcional
    ip_maquina = data.get('ip_maquina')
    contrasena = data.get('contrasena')

    # Validación de entrada
    if not nombre_maquina or not matricula1 or not ip_maquina or not contrasena:
        return jsonify({"status": "error", "message": "Faltan datos requeridos."}), 400
    
    conn = None
    cursor = None
    try:
        # Abre la conexión a la base de datos
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verifica que las matrículas estén registradas
        if not Sesion.verificar_existe_alumno(cursor, matricula1):
            return jsonify({"status": "error", "message": f"La matrícula {matricula1} no está registrada."}), 400
        if matricula2 and not Sesion.verificar_existe_alumno(cursor, matricula2):
            return jsonify({"status": "error", "message": f"La matrícula {matricula2} no está registrada."}), 400

        # Llama a la función para crear una nueva sesión
        result = Sesion.crear_nueva_sesion(cursor, nombre_maquina, matricula1, matricula2, ip_maquina, contrasena)

        # Si todo ha ido bien, confirma la transacción
        if result["status"] == "success":
            conn.commit()
            return jsonify(result), 200
        else:
            # En caso de error, no confirmamos la transacción
            conn.rollback()
            return jsonify(result), 400

    except Exception as e:
        print(f"Error al procesar la solicitud: {str(e)}")
        return jsonify({"status": "error", "message": "Error interno del servidor"}), 500

    finally:
        # Verifica si el cursor y la conexión fueron creados antes de intentar cerrarlos
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@session_blueprint.route('/cerrar_sesion', methods=['POST'])
@token_required  # Agregamos el decorador para verificar el token
def cerrar_sesion():
    data = request.get_json()
    matricula = data.get('matricula')
    id_equipo = data.get('id_equipo')

    # Validación de entrada
    if not matricula or not id_equipo:
        return jsonify({"status": "error", "message": "Faltan datos requeridos."}), 400

    conn = None
    cursor = None
    try:
        # Abre la conexión a la base de datos
        conn = get_db_connection()
        cursor = conn.cursor()

        # Llama a la función para cerrar la sesión
        result = Sesion.cerrar_sesion(cursor, matricula, id_equipo)

        # Si todo ha ido bien, confirma la transacción
        if result["status"] == "success":
            conn.commit()
            return jsonify(result), 200
        else:
            # En caso de error, no confirmamos la transacción
            conn.rollback()
            return jsonify(result), 400

    except Exception as e:
        print(f"Error al procesar la solicitud: {str(e)}")
        return jsonify({"status": "error", "message": "Error interno del servidor"}), 500

    finally:
        # Verifica si el cursor y la conexión fueron creados antes de intentar cerrarlos
        if cursor:
            cursor.close()
        if conn:
            conn.close()
