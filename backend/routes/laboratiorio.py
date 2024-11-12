from flask import Blueprint, jsonify, request
from backend.models.laboratorio import laboratorio
from backend.db import get_db_connection
from backend.models.auth import token_required

laboratorio_blueprint = Blueprint('lab', __name__)

@laboratorio_blueprint.route('/end_sesiones', methods=['POST'])
@token_required
def cerrar_sesiones():
    """
    Endpoint para cerrar todas las sesiones activas en un laboratorio específico.
    """
    data = request.get_json()
    nombre_laboratorio = data.get('laboratorio')
    
    if not nombre_laboratorio:
        return jsonify({"error": "Se requiere el nombre del laboratorio"}), 400

    # Conexión a la base de datos
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "No se pudo obtener la conexión a la base de datos"}), 500

    try:
        # Llamar a la función para cerrar sesiones activas
        resultado = laboratorio.cerrar_sesiones_laboratorio(nombre_laboratorio)
        
        # Validar el resultado y construir la respuesta según el status
        if resultado["status"] == "success":
            mensaje = resultado["message"]
            return jsonify({"mensaje": mensaje}), 200
        else:
            return jsonify({"error": resultado["message"]}), 400

    except Exception as e:
        # En caso de error en el procesamiento
        return jsonify({"error": f"Error al intentar cerrar sesiones: {str(e)}"}), 500

    finally:
        # Cerrar la conexión
        conn.close()


@laboratorio_blueprint.route('/active_sesiones', methods=['GET'])
@token_required
def obtener_sesiones_activas_laboratorio():
    """
    Endpoint para obtener todas las sesiones activas en un laboratorio específico.
    """
    nombre_laboratorio = request.args.get('laboratorio')
    
    if not nombre_laboratorio:
        return jsonify({"error": "Se requiere el nombre del laboratorio"}), 400

    try:
        conn = get_db_connection()  # Conexión a la base de datos
        cursor = conn.cursor()

        # Llamar a la función para obtener las sesiones activas
        sesiones_activas = laboratorio.obtener_sesiones_activas(cursor, nombre_laboratorio)
        
        if not sesiones_activas:
            return jsonify({"mensaje": f"No se encontraron sesiones activas en el laboratorio '{nombre_laboratorio}'."}), 404

        return jsonify(sesiones_activas), 200

    except ConnectionError:
        return jsonify({"error": "Error al conectar con la base de datos"}), 500

    except Exception as e:
        return jsonify({"error": "Ha ocurrido un error inesperado", "detalle": str(e)}), 500

    finally:
        cursor.close()
        conn.close()
