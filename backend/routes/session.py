from flask import Blueprint, request, jsonify
from backend.db import get_db_connection
from backend.models.sesion import Sesion
from backend.models.auth import token_required  # Importa el decorador para JWT
from datetime import datetime

session_blueprint = Blueprint('session', __name__)

# Endpoint para consultar sesiones activas
@session_blueprint.route('/consulta_session/<string:matricula>', methods=['GET'])
@token_required
def consulta_session(matricula):
    if not matricula:
        return jsonify({"status": "error", "message": "Faltan datos requeridos"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM alumnos WHERE matricula = %s", (matricula,))
        if not cursor.fetchone():
            return jsonify({"status": "error", "message": "El alumno no existe en la base de datos"}), 404

        cursor.execute("SELECT id_maquina, matricula, inicio_sesion, fin_sesion, estado FROM sesiones WHERE matricula = %s", (matricula,))
        sesiones = cursor.fetchall()

        if not sesiones:
            return jsonify({"status": "error", "message": "No hay sesiones activas para el alumno"}), 404

        sesiones_activas = [
            {
                "id_maquina": sesion[0],
                "matricula": sesion[1],
                "inicio_sesion": sesion[2],
                "fin_sesion": sesion[3],
                "estado": sesion[4],
                "tiempo_activo": str(datetime.now() - sesion[2]) if sesion[4] == 'activo' and sesion[2] else None
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
@session_blueprint.route('/crear_sesion', methods=['POST'])
@token_required
def crear_sesion():
    data = request.get_json()
    matricula1 = data.get('matricula1')
    matricula2 = data.get('matricula2')
    id_maquina = data.get('id_maquina')
    ip_maquina = data.get('ip_maquina')
    nombre_maquina = data.get('nombre_maquina')
    contrasena = data.get('contrasena')

    if not matricula1 or not contrasena:
        return jsonify({"status": "error", "message": "Faltan datos requeridos: matrícula y contraseña"}), 400

    if not Sesion.validar_matricula(matricula1) or (matricula2 and not Sesion.validar_matricula(matricula2)):
        return jsonify({"status": "error", "message": "Formato de matrícula no válido"}), 400

    response = Sesion.create_session(id_maquina, matricula1, matricula2, ip_maquina, nombre_maquina, contrasena)
    status_code = 201 if response["status"] == "success" else 500
    return jsonify(response), status_code

# Endpoint para finalizar una sesión
@session_blueprint.route('/end', methods=['POST'])
@token_required
def end_session():
    data = request.get_json()
    matricula = data.get('matricula')
    id_maquina = data.get('id_maquina')

    if not matricula or not id_maquina:
        return jsonify({"status": "error", "message": "Faltan datos requeridos"}), 400
