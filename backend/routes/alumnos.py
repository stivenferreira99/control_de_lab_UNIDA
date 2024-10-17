from backend.db import get_db_connection  # Importación absoluta
from flask import Blueprint, request, jsonify

alumnos_blueprint = Blueprint('alumnos', __name__)

# Consultar Todos los Alumnos
@alumnos_blueprint.route('/', methods=['GET'])
def get_alumnos():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM alumnos")
        alumnos = cursor.fetchall()

        alumnos_list = [{"matricula": alumno[0], "nombre": alumno[1], "apellido": alumno[2], "nro_cedula": alumno[3], "id_carrera": alumno[4], "id_materia": alumno[5]} for alumno in alumnos]

        return jsonify({"status": "success", "alumnos": alumnos_list}), 200
    
    except Exception as e:
        print(f"Error al obtener alumnos: {str(e)}")
        return jsonify({"status": "error", "message": "Error al obtener alumnos"}), 500

    finally:
        # Asegurarse de cerrar la conexión a la base de datos
        if 'conn' in locals():
            conn.close()

# Crear un Nuevo Alumno
@alumnos_blueprint.route('/', methods=['POST'])
def crear_alumno():
    try:
        matricula = request.json.get('matricula')
        nombre = request.json.get('nombre')
        apellido = request.json.get('apellido')
        nro_cedula = request.json.get('nro_cedula')
        id_carrera = request.json.get('id_carrera')
        id_materia = request.json.get('id_materia')

        if not matricula or not nombre or not apellido or not nro_cedula or not id_carrera or not id_materia:
            return jsonify({"status": "error", "message": "Faltan datos requeridos"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM alumnos WHERE matricula = %s", (matricula,))
        if cursor.fetchone():
            return jsonify({"status": "success", "message": "El alumno ya existe"}), 200

        cursor.execute(
            "INSERT INTO alumnos (matricula, nombre, apellido, nro_cedula, id_carrera, id_materia) VALUES (%s, %s, %s, %s, %s, %s)",
            (matricula, nombre, apellido, nro_cedula, id_carrera, id_materia)
        )
        conn.commit()

        return jsonify({"status": "success", "message": "Alumno creado exitosamente"}), 201

    except Exception as e:
        print(f"Error al crear alumno: {str(e)}")
        return jsonify({"status": "error", "message": "Error al crear alumno"}), 500

    finally:
        if 'conn' in locals():
            conn.close()

# Actualizar un Alumno
@alumnos_blueprint.route('/<matricula>', methods=['PUT'])
def actualizar_alumno(matricula):
    try:
        nombre = request.json.get('nombre')
        apellido = request.json.get('apellido')
        nro_cedula = request.json.get('nro_cedula')
        id_carrera = request.json.get('id_carrera')
        id_materia = request.json.get('id_materia')

        if not nombre and not apellido and not nro_cedula and not id_carrera and not id_materia:
            return jsonify({"status": "error", "message": "Se requiere al menos un campo para actualizar"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        if nombre:
            cursor.execute("UPDATE alumnos SET nombre = %s WHERE matricula = %s", (nombre, matricula))
        if apellido:
            cursor.execute("UPDATE alumnos SET apellido = %s WHERE matricula = %s", (apellido, matricula))
        if nro_cedula:
            cursor.execute("UPDATE alumnos SET nro_cedula = %s WHERE matricula = %s", (nro_cedula, matricula))
        if id_carrera:
            cursor.execute("UPDATE alumnos SET id_carrera = %s WHERE matricula = %s", (id_carrera, matricula))
        if id_materia:
            cursor.execute("UPDATE alumnos SET id_materia = %s WHERE matricula = %s", (id_materia, matricula))

        conn.commit()

        return jsonify({"status": "success", "message": "Alumno actualizado exitosamente"}), 200

    except Exception as e:
        print(f"Error al actualizar alumno: {str(e)}")
        return jsonify({"status": "error", "message": "Error al actualizar alumno"}), 500

    finally:
        if 'conn' in locals():
            conn.close()


# Eliminar alumno
@alumnos_blueprint.route('/<matricula>', methods=['DELETE'])
def eliminar_alumno(matricula):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Verificar si el alumno existe
        cursor.execute("SELECT * FROM alumnos WHERE matricula = %s", (matricula,))
        if cursor.fetchone() is None:
            return jsonify({"status": "error", "message": "Alumno no encontrado"}), 404
        
        # Verificar si el alumno tiene sesiones activas
        cursor.execute("SELECT id_usuario FROM sesiones WHERE matricula = %s AND id_estado = (SELECT id_estado FROM estado WHERE estado = 'A')", (matricula,))
        sesion_activa = cursor.fetchone()

        if sesion_activa:
            return jsonify({
                "status": "error", 
                "message": "No se puede eliminar el alumno porque tiene una sesión activa", 
                "id_usuario": sesion_activa[0]
            }), 400

        # Eliminar el alumno de la tabla `alumnos`
        cursor.execute("DELETE FROM alumnos WHERE matricula = %s", (matricula,))
        conn.commit()

        return jsonify({"status": "success", "message": f"Alumno {matricula} eliminado exitosamente"}), 200

    except Exception as e:
        print(f"Error al eliminar alumno: {str(e)}")
        return jsonify({"status": "error", "message": "Error al procesar la solicitud"}), 500

    finally:
        if 'conn' in locals():
            conn.close()
