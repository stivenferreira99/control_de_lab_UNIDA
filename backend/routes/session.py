from flask import Blueprint, request, jsonify
from backend.db import get_db_connection
from datetime import datetime
from functools import wraps
import jwt

session_blueprint = Blueprint('session', __name__)

SECRET_KEY = "1234"  # Asegúrate de configurar esto adecuadamente
ALGORITHM = "HS256"

# Decorador para verificar el token JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            token = auth_header.split(" ")[1] if len(auth_header.split(" ")) > 1 else None

        if not token:
            return jsonify({"status": "error", "message": "Token es necesario"}), 401

        try:
            jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except jwt.ExpiredSignatureError:
            return jsonify({"status": "error", "message": "Token ha expirado"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"status": "error", "message": "Token inválido"}), 401

        return f(*args, **kwargs)

    return decorated





# Endpoint para consultar sesiones activas
@session_blueprint.route('/consulta_session/<string:matricula>', methods=['GET'])
@token_required  # Proteger con JWT
def consulta_session(matricula):
    
    if not matricula:
        return jsonify({"status": "error", "message": "Faltan datos requeridos"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Consulta para verificar si el alumno existe
        cursor.execute("SELECT * FROM alumnos WHERE matricula = %s", (matricula,))
        alumno = cursor.fetchone()

        if not alumno:
            return jsonify({"status": "error", "message": "El alumno no existe en la base de datos"}), 404

        # Seleccionar sesiones activas
        cursor.execute("SELECT id_maquina, matricula, inicio_sesion, fin_sesion, estado FROM sesiones WHERE matricula = %s", (matricula,))
        sesiones = cursor.fetchall()

        if sesiones:
            sesiones_activas = []
            for sesion in sesiones:
                id_maquina, matricula, inicio_sesion, fin_sesion, estado = sesion
                tiempo_activo = None
                if estado == 'activo' and inicio_sesion is not None:
                    tiempo_activo = datetime.now() - inicio_sesion
                
                sesiones_activas.append({
                    "id_maquina": id_maquina,
                    "matricula": matricula,
                    "inicio_sesion": inicio_sesion,
                    "fin_sesion": fin_sesion,
                    "estado": estado,
                    "tiempo_activo": str(tiempo_activo) if tiempo_activo else None
                })

            return jsonify({"status": "success", "sesiones_activas": sesiones_activas}), 200
        else:
            return jsonify({"status": "error", "message": "No hay sesiones activas para el alumno"}), 404

    except Exception as e:
        print(f"Error al procesar la solicitud: {str(e)}")
        return jsonify({"status": "error", "message": "Error interno del servidor"}), 500
    
    finally:
        if 'conn' in locals():
            conn.close()






# Endpoint para crear una sesión
@session_blueprint.route('/crear_sesion', methods=['POST'])
@token_required  # Proteger con JWT
def crear_sesion():
    matricula1 = request.json.get('matricula1')  # Matrícula obligatoria
    matricula2 = request.json.get('matricula2')  # Matrícula opcional
    id_maquina = request.json.get('id_maquina')
    ip_maquina = request.json.get('ip_maquina')
    nombre_maquina = request.json.get('nombre_maquina', None)  # Puede ser NULL
    contrasena = request.json.get('contrasena')

    # Validar que se ingresaron todos los datos necesarios
    if not matricula1 or not ip_maquina:
        return jsonify({"status": "error", "message": "Faltan datos requeridos"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Verificar si la matrícula1 existe en la tabla alumnos
        cursor.execute("SELECT * FROM alumnos WHERE matricula = %s", (matricula1,))
        alumno_existente1 = cursor.fetchone()

        # Si la matrícula no existe, insertarla
        if not alumno_existente1:
            cursor.execute("INSERT INTO alumnos (matricula) VALUES (%s)", (matricula1,))
        
        # Verificar si hay una sesión activa para la matrícula1
        cursor.execute("SELECT * FROM sesiones WHERE matricula = %s AND estado = 'activo'", (matricula1,))
        sesion_activa1 = cursor.fetchone()

        if sesion_activa1:
            # Cerrar la sesión anterior
            fin_sesion = datetime.now()
            cursor.execute(
                "UPDATE sesiones SET fin_sesion = %s, estado = 'inactivo' WHERE matricula = %s AND estado = 'activo'",
                (fin_sesion, matricula1)
            )

        # Verificar si se proporcionó matricula2
        if matricula2:
            # Verificar si la matrícula2 existe en la tabla alumnos
            cursor.execute("SELECT * FROM alumnos WHERE matricula = %s", (matricula2,))
            alumno_existente2 = cursor.fetchone()

            # Si la matrícula2 no existe, insertarla
            if not alumno_existente2:
                cursor.execute("INSERT INTO alumnos (matricula) VALUES (%s)", (matricula2,))
        
            # Verificar si hay una sesión activa para la matrícula2
            cursor.execute("SELECT * FROM sesiones WHERE matricula = %s AND estado = 'activo'", (matricula2,))
            sesion_activa2 = cursor.fetchone()

            if sesion_activa2:
                # Cerrar la sesión anterior
                fin_sesion = datetime.now()
                cursor.execute(
                    "UPDATE sesiones SET fin_sesion = %s, estado = 'inactivo' WHERE matricula = %s AND estado = 'activo'",
                    (fin_sesion, matricula2)
                )

        # Crear una nueva sesión para matricula1 (y matricula2 si es necesario)
        cursor.execute(
            "INSERT INTO sesiones (id_maquina, matricula, inicio_sesion, estado, ip_maquina, nombre_usuario, contrasena) VALUES (%s, %s, NOW(), 'activo', %s, %s, %s)",
            (id_maquina, matricula1, ip_maquina, nombre_maquina, contrasena)
        )
        conn.commit()

        return jsonify({"status": "success", "message": "Sesión creada exitosamente"}), 201

    except Exception as e:
        print(f"Error al procesar la solicitud: {str(e)}")
        return jsonify({"status": "error", "message": "Error interno del servidor"}), 500

    finally:
        if 'conn' in locals():
            conn.close()


# Endpoint para finalizar una sesión
@session_blueprint.route('/end', methods=['POST'])
@token_required  # Proteger con JWT
def end_session():
    matricula = request.json.get('matricula')
    id_maquina = request.json.get('id_maquina')

    if not matricula or not id_maquina:
        return jsonify({"status": "error", "message": "Faltan datos requeridos"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM sesiones WHERE matricula = %s AND id_maquina = %s AND estado = 'activo'", (matricula, id_maquina))
        session = cursor.fetchone()

        if not session:
            return jsonify({"status": "error", "message": "No hay sesión activa para el alumno en esta máquina"}), 404

        fin_sesion = datetime.now()
        cursor.execute(
            "UPDATE sesiones SET fin_sesion = %s, estado = 'inactivo' WHERE matricula = %s AND id_maquina = %s",
            (fin_sesion, matricula, id_maquina)
        )
        conn.commit()

        return jsonify({"status": "success", "message": "Sesión finalizada exitosamente"}), 200

    except Exception as e:
        print(f"Error al procesar la solicitud: {str(e)}")
        return jsonify({"status": "error", "message": "Error interno del servidor"}), 500

    finally:
        if 'conn' in locals():
            conn.close()
