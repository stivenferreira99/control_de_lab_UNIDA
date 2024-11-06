from flask import Blueprint, request, jsonify
from backend.db import get_db_connection
from backend.models.sesion import Sesion
from backend.models.auth import token_required
from datetime import datetime
from functools import wraps

session_blueprint = Blueprint('session', __name__)

@session_blueprint.route('/consulta_session/<string:matricula>', methods=['GET'])
@token_required
def consulta_session(matricula):
    if not matricula:
        return jsonify({"status": "error", "message": "Faltan datos requeridos"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Validar matrícula
        if not Sesion.validar_matricula(matricula):
            return jsonify({"status": "error", "message": "Formato de matrícula incorrecta"}), 400

        # Verificar si el alumno existe
        cursor.execute("""
            SELECT id_alumno FROM alumno WHERE matricula = %s
        """, (matricula,))
        alumno = cursor.fetchone()
        if not alumno:
            return jsonify({"status": "error", "message": "El alumno no existe en la base de datos"}), 404

        # Consultar las sesiones activas del alumno
        cursor.execute("""
            SELECT s.id_sesion, s.id_equipo, s.estado, s.fecha_hora_inicio, s.fecha_hora_fin
            FROM sesion s
            JOIN alumno a ON s.id_alumno = a.id_alumno
            WHERE a.matricula = %s AND s.estado = 'Activo'
        """, (matricula,))
        sesiones = cursor.fetchall()

        if not sesiones:
            return jsonify({"status": "error", "message": "No hay sesiones activas para el alumno"}), 404

        # Preparar los datos de las sesiones activas
        sesiones_activas = [
            {
                "id_sesion": sesion[0],
                "id_equipo": sesion[1],
                "estado": sesion[2],
                "inicio_sesion": sesion[3],
                "fin_sesion": sesion[4] if sesion[4] else None,
                "tiempo_activo": str(datetime.now() - sesion[3]) if sesion[2] == 'Activo' else None
            }
            for sesion in sesiones
        ]

        return jsonify({"status": "success", "sesiones_activas": sesiones_activas}), 200

    except Exception as e:
        print(f"Error al procesar la solicitud: {str(e)}")
        return jsonify({"status": "error", "message": "Error interno del servidor"}), 500
    finally:
        if 'conn' in locals():
            conn.close()


# Endpoint para crear una nueva sesión
@session_blueprint.route('/crear', methods=['POST'])
@token_required
def crear_sesion():
    data = request.get_json()
    matricula1 = data.get('matricula1')
    matricula2 = data.get('matricula2')
    id_equipo = data.get('id_equipo')
    ip_maquina = data.get('ip_maquina')
    nombre_maquina = data.get('nombre_maquina')
    contrasena = data.get('contrasena')

    response = {"status": "success"}

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Llamar a la función de creación de sesión
        result = Sesion.crear_nueva_sesion(cursor, id_equipo, matricula1, ip_maquina, nombre_maquina, matricula2, contrasena)
        response.update(result)

        conn.commit()
    except Exception as e:
        print(f"Error al crear la sesión: {str(e)}")
        return jsonify({"status": "error", "message": "Error al crear la sesión"}), 500
    finally:
        if 'conn' in locals():
            conn.close()

    return jsonify(response), 200

# Endpoint para finalizar una sesión
@session_blueprint.route('/end', methods=['POST'])
@token_required
def end_session():
    data = request.get_json()
    matricula = data.get('matricula')
    id_equipo = data.get('id_equipo')

    if matricula and not Sesion.validar_matricula(matricula):
        return jsonify({"status": "error", "message": "Formato de matrícula incorrecta"}), 400

    response = {"status": "success"}

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Llama a la función para cerrar sesiones
        result = Sesion.cerrar_sesion(cursor, matricula, id_equipo)
        response.update(result)

        conn.commit()
    except Exception as e:
        print(f"Error al cerrar la sesión: {str(e)}")
        return jsonify({"status": "error", "message": "Error al cerrar la sesión"}), 500
    finally:
        if 'conn' in locals():
            conn.close()

    return jsonify(response), 200



#programado directo aca, para que liste todas sesiones activas nomas
@session_blueprint.route('/sesiones_activas', methods=['GET'])
@token_required
def sesiones_activas():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Consultar todas las sesiones activas
        cursor.execute("""
            SELECT s.id_sesion, s.id_equipo, s.estado, s.fecha_hora_inicio, s.fecha_hora_fin, e.nombre_pc 
            FROM sesion s
            JOIN equipo e ON s.id_equipo = e.id_equipo
            WHERE s.estado = 'Activo'
        """)
        sesiones = cursor.fetchall()

        if not sesiones:
            return jsonify({"status": "error", "message": "No hay sesiones activas"}), 404

        # Preparar los datos de las sesiones activas
        sesiones_activas = [
            {
                "id_sesion": sesion[0],
                "id_equipo": sesion[1],
                "estado": sesion[2],
                "inicio_sesion": sesion[3],
                "fin_sesion": sesion[4] if sesion[4] else None,
                "nombre_pc": sesion[5],
                "tiempo_activo": str(datetime.now() - sesion[3]) if sesion[2] == 'Activo' else None
            }
            for sesion in sesiones
        ]

        return jsonify({"status": "success", "sesiones_activas": sesiones_activas}), 200

    except Exception as e:
        print(f"Error al procesar la solicitud: {str(e)}")
        return jsonify({"status": "error", "message": "Error interno del servidor"}), 500
    finally:
        if 'conn' in locals():
            conn.close()
