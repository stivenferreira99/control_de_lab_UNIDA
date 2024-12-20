from datetime import datetime, timedelta
import jwt  # Asegúrate de que sea la biblioteca PyJWT
from functools import wraps
from flask import request, jsonify, Blueprint

# Clave secreta para firmar los JWT
SECRET_KEY = '1234'  # Considera usar una clave más compleja en producción
ALGORITHM = 'HS256'
EXPIRATION_TIME = 3600  # 1 hora de duración del token

# Definición del Blueprint
auth_blueprint = Blueprint('auth', __name__)

# Función para generar el token JWT
def generate_token(username):
    try:
        return jwt.encode(
            {
                'sub': username,  # Identificador del sujeto (usuario)
                'exp': datetime.utcnow() + timedelta(seconds=EXPIRATION_TIME)  # Tiempo de expiración
            },
            SECRET_KEY,
            algorithm=ALGORITHM
        )
    except Exception as e:
        raise Exception(f"Error al generar el token: {str(e)}")

# Endpoint para autenticar y generar el token
@auth_blueprint.route('/autenticar_servicio', methods=['GET'])
def autenticar_servicio():
    username = "admin"  # Este puede ser cualquier valor o lógica que desees usar
    try:
        token = generate_token(username)
        return jsonify({"token": token}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Decorador para proteger otros endpoints
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Verificar si el token JWT está presente en el encabezado
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            token = auth_header.split(" ")[1] if len(auth_header.split(" ")) > 1 else None

        if not token:
            return jsonify({"status": "error", "message": "Token es necesario"}), 401

        try:
            # Decodificar el token JWT
            data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except jwt.ExpiredSignatureError:
            return jsonify({"status": "error", "message": "Token ha expirado"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"status": "error", "message": "Token inválido"}), 401
        except Exception as e:
            return jsonify({"status": "error", "message": f"Error al decodificar el token: {str(e)}"}), 500

        return f(*args, **kwargs)

    return decorated
