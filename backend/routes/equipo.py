# routes/equipo.py
from backend.models.auth import token_required
from flask import Blueprint, request, jsonify
from backend.models.equipo import Equipo

equipo_blueprint = Blueprint('equipo', __name__)

@equipo_blueprint.route('/agregar_equipo', methods=['POST'])
@token_required  # Verifica el token de autenticación
def agregar_equipo():
    data = request.get_json()
    nombre_pc = data.get('nombre_pc')
    ip_equipo = data.get('ip_equipo')
    laboratorio = data.get('laboratorio')

    # Validación de campos obligatorios
    if not nombre_pc or not ip_equipo or not laboratorio:
        return jsonify({"status": "error", "message": "Faltan datos requeridos: nombre_pc, ip_equipo, laboratorio"}), 400

    # Campos opcionales
    monitor = data.get('monitor')
    gabinete = data.get('gabinete')
    teclado = data.get('teclado')
    mouse = data.get('mouse')
    receptor = data.get('receptor')
    estado_equipo = data.get('estado_equipo', 'disponible')  # Valor predeterminado

    # Llama a la función para agregar el equipo
    result = Equipo.agregar_equipo(nombre_pc, ip_equipo, laboratorio, monitor, gabinete, teclado, mouse, receptor, estado_equipo)
    return jsonify(result), 200 if result["status"] == "success" else 400

@equipo_blueprint.route('/modificar_equipo', methods=['PUT'])
@token_required
def modificar_equipo():
    data = request.get_json()
    nombre_pc = data.get('nombre_pc')

    # Validación del campo obligatorio
    if not nombre_pc:
        return jsonify({"status": "error", "message": "Faltan datos requeridos: nombre_pc"}), 400

    # Campos opcionales
    ip_equipo = data.get('ip_equipo')
    laboratorio = data.get('laboratorio')
    monitor = data.get('monitor')
    gabinete = data.get('gabinete')
    teclado = data.get('teclado')
    mouse = data.get('mouse')
    receptor = data.get('receptor')
    estado_equipo = data.get('estado_equipo')

    # Llama a la función para modificar el equipo
    result = Equipo.modificar_equipo(nombre_pc, ip_equipo, laboratorio, monitor, gabinete, teclado, mouse, receptor, estado_equipo)
    return jsonify(result), 200 if result["status"] == "success" else 400

@equipo_blueprint.route('/eliminar_equipo', methods=['DELETE'])
@token_required
def eliminar_equipo():
    data = request.get_json()
    nombre_pc = data.get('nombre_pc')

    # Validación del campo obligatorio
    if not nombre_pc:
        return jsonify({"status": "error", "message": "Faltan datos requeridos: nombre_pc"}), 400

    # Llama a la función para eliminar el equipo
    result = Equipo.eliminar_equipo(nombre_pc)
    return jsonify(result), 200 if result["status"] == "success" else 400
