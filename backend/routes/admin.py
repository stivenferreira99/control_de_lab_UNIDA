from flask import Blueprint, request, jsonify
from models.sesion import Sesion
from models.maquina import Maquina
from models.alumno import Alumno  # Asegúrate de importar tu modelo de alumno

admin_blueprint = Blueprint('admin', __name__)

# Consultar todas las sesiones
@admin_blueprint.route('/sesiones', methods=['GET'])
def get_sesiones():
    try:
        # Aquí obtendrás las sesiones desde la base de datos
        sesiones = Sesion.obtener_todas_las_sesiones()  # Implementa este método en tu modelo
        return jsonify({"status": "success", "sesiones": sesiones}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Consultar todas las máquinas
@admin_blueprint.route('/maquinas', methods=['GET'])
def get_maquinas():
    try:
        # Aquí obtendrás las máquinas desde la base de datos
        maquinas = Maquina.obtener_todas_las_maquinas()  # Implementa este método en tu modelo
        return jsonify({"status": "success", "maquinas": maquinas}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Otras rutas administrativas según sea necesario...
