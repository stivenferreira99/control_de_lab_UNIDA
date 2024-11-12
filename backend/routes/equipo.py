from flask import Blueprint, request, jsonify
from backend.db import SessionLocal
from backend.models.equipo import Equipo
from backend.models.auth import token_required

equipo_blueprint = Blueprint('equipo', __name__)

@equipo_blueprint.route('/agregar_equipo', methods=['POST'])
@token_required
def agregar_equipo():
    nombre_pc = request.json.get('nombre_pc')
    ip_equipo = request.json.get('ip_equipo')

    if not nombre_pc or not ip_equipo:
        return jsonify({"status": "error", "message": "Faltan datos requeridos"}), 400

    existente = SessionLocal.query(Equipo).filter(Equipo.nombre_pc == nombre_pc).first()
    if existente:
        return jsonify({"status": "error", "message": "El nombre del equipo ya existe"}), 400

    nuevo_equipo = Equipo(nombre_pc=nombre_pc, ip_equipo=ip_equipo)

    try:
        SessionLocal.add(nuevo_equipo)
        SessionLocal.commit()
        return jsonify({"status": "success", "message": "Equipo agregado exitosamente"}), 201
    except Exception as e:
        SessionLocal.rollback()
        print(f"Error al agregar el equipo: {str(e)}")
        return jsonify({"status": "error", "message": "Error interno del servidor"}), 500
