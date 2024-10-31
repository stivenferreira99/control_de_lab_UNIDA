from flask import Blueprint, request, jsonify
from backend.db import SessionLocal
from backend.models.maquina import Maquina
from backend.models.auth import token_required

maquina_blueprint = Blueprint('maquina', __name__)

@maquina_blueprint.route('/agregar_maquina', methods=['POST'])
@token_required
def agregar_maquina():
    nombre = request.json.get('nombre')
    ip_maquina = request.json.get('ip_maquina')

    if not nombre or not ip_maquina:
        return jsonify({"status": "error", "message": "Faltan datos requeridos"}), 400

    existente = SessionLocal.query(Maquina).filter(Maquina.nombre == nombre).first()
    if existente:
        return jsonify({"status": "error", "message": "El nombre de la máquina ya existe"}), 400

    nueva_maquina = Maquina(nombre=nombre, ip_maquina=ip_maquina)

    try:
        SessionLocal.add(nueva_maquina)
        SessionLocal.commit()
        return jsonify({"status": "success", "message": "Máquina agregada exitosamente"}), 201
    except Exception as e:
        SessionLocal.rollback()
        print(f"Error al agregar la máquina: {str(e)}")
        return jsonify({"status": "error", "message": "Error interno del servidor"}), 500
