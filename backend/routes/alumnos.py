# backend/routes/alumnos.py
from flask import Blueprint, request, jsonify
from backend.models.alumno import Alumno

alumnos_blueprint = Blueprint('alumnos', __name__)

# Consultar Todos los Alumnos
@alumnos_blueprint.route('/consulta', methods=['GET'])
def get_alumnos():
    try:
        alumnos = Alumno.obtener_alumnos()
        return jsonify({"status": "success", "alumnos": alumnos}), 200
    except Exception as e:
        print(f"Error al obtener alumnos: {str(e)}")
        return jsonify({"status": "error", "message": "Error al obtener alumnos"}), 500

# Crear un Nuevo Alumno
@alumnos_blueprint.route('/registro', methods=['POST'])
def crear_alumno():
    datos = request.json
    required_fields = ['matricula', 'nombre', 'apellido', 'fecha_nacimiento', 'ci', 'nombre_carrera']
    if not all(field in datos for field in required_fields):
        return jsonify({"status": "error", "message": "Faltan datos requeridos"}), 400

    result = Alumno.crear_alumno(
        matricula=datos['matricula'],
        nombre=datos['nombre'],
        apellido=datos['apellido'],
        fecha_nacimiento=datos['fecha_nacimiento'],
        ci=datos['ci'],
        nombre_carrera=datos['nombre_carrera']
    )

    if result["status"] == "exists":
        return jsonify({"status": "error", "message": "El alumno ya existe"}), 400
    elif result["status"] == "not_found":
        return jsonify({"status": "error", "message": "La carrera no existe"}), 404

    return jsonify({"status": "success", "message": "Alumno creado exitosamente"}), 201

from datetime import datetime

# Actualizar un Alumno
@alumnos_blueprint.route('/<matricula>', methods=['PUT'])
def actualizar_alumno(matricula):
    datos = request.json
    required_fields = ['nombre', 'apellido', 'fecha_nacimiento', 'ci', 'id_carrera']
    
    # Verificar si el alumno existe
    if not Alumno.existe_alumno(matricula):
        return jsonify({"status": "error", "message": "El alumno no está registrado"}), 404

    # Verificar si todos los campos requeridos están presentes
    if not all(field in datos for field in required_fields):
        return jsonify({"status": "error", "message": "Todos los campos son obligatorios"}), 400

    # Intentar actualizar el alumno
    try:
        # Validación de la fecha
        if datos['fecha_nacimiento']:
            try:
                # Intentamos convertir la fecha al formato adecuado
                fecha = datetime.strptime(datos['fecha_nacimiento'], '%Y-%m-%d')
            except ValueError:
                return jsonify({
                    "status": "error",
                    "message": f"Error en la fecha de nacimiento: '{datos['fecha_nacimiento']}' no coincide con el formato '%Y-%m-%d'"
                }), 400

        Alumno.actualizar_alumno(
            matricula=matricula,
            nombre=datos['nombre'],
            apellido=datos['apellido'],
            ci=datos['ci'],
            fecha_nacimiento=datos['fecha_nacimiento'],  # Ya validada
            id_carrera=datos['id_carrera']
        )
    except Exception as e:
        # Captura cualquier otro error inesperado
        return jsonify({"status": "error", "message": f"Error al actualizar el alumno: {str(e)}"}), 500

    return jsonify({"status": "success", "message": "Alumno actualizado exitosamente"}), 200


# Eliminar alumno
@alumnos_blueprint.route('/<matricula>', methods=['DELETE'])
def eliminar_alumno(matricula):
    result = Alumno.eliminar_alumno(matricula)
    if result["status"] == "active_session":
        return jsonify({
            "status": "error",
            "message": "No se puede eliminar el alumno porque tiene una sesión activa"
        }), 400
    return jsonify({"status": "success", "message": f"Alumno {matricula} eliminado exitosamente"}), 200
