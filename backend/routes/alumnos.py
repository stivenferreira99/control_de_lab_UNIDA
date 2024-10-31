# backend/routes/alumnos.py
from flask import Blueprint, request, jsonify
from backend.models.alumno import Alumno

alumnos_blueprint = Blueprint('alumnos', __name__)

# Consultar Todos los Alumnos
@alumnos_blueprint.route('/', methods=['GET'])
def get_alumnos():
    try:
        alumnos = Alumno.obtener_alumnos()
        return jsonify({"status": "success", "alumnos": alumnos}), 200
    except Exception as e:
        print(f"Error al obtener alumnos: {str(e)}")
        return jsonify({"status": "error", "message": "Error al obtener alumnos"}), 500

# Crear un Nuevo Alumno
@alumnos_blueprint.route('/', methods=['POST'])
def crear_alumno():
    datos = request.json
    required_fields = ['matricula', 'nombre', 'apellido', 'fecha_nacimiento', 'ci', 'id_carrera']
    if not all(field in datos for field in required_fields):
        return jsonify({"status": "error", "message": "Faltan datos requeridos"}), 400

    result = Alumno.crear_alumno(
        matricula=datos['matricula'],
        nombre=datos['nombre'],
        apellido=datos['apellido'],
        fecha_nacimiento=datos['fecha_nacimiento'],
        ci=datos['ci'],
        id_carrera=datos['id_carrera']
    )

    if result["status"] == "exists":
        return jsonify({"status": "success", "message": "El alumno ya existe"}), 200
    return jsonify({"status": "success", "message": "Alumno creado exitosamente"}), 201

# Actualizar un Alumno
@alumnos_blueprint.route('/<matricula>', methods=['PUT'])
def actualizar_alumno(matricula):
    datos = request.json
    if not any(datos.values()):
        return jsonify({"status": "error", "message": "Se requiere al menos un campo para actualizar"}), 400

    Alumno.actualizar_alumno(
        matricula,
        nombre=datos.get('nombre'),
        apellido=datos.get('apellido'),
        ci=datos.get('ci'),
        id_carrera=datos.get('id_carrera')
    )
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
