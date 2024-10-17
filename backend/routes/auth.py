from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import jwt
from functools import wraps

auth_blueprint = Blueprint('auth', __name__)

# Clave secreta para firmar los JWT
SECRET_KEY = '1234'
ALGORITHM = 'HS256'
EXPIRATION_TIME = 3600  # 1 hora de duración del token

# Credenciales predeterminadas del servicio (definidas en el backend)
SERVICE_USERNAME = 'admin'
SERVICE_PASSWORD = 'admin'

@auth_blueprint.route('/autenticar_servicio', methods=['POST'])
def autenticar_servicio():
    """
    Endpoint para autenticar el servicio y generar un token JWT
    """
    # Obtener las credenciales enviadas en la solicitud
    username = request.json.get('username')
    password = request.json.get('password')

    # Verificar si las credenciales coinciden con las predeterminadas
    if username == SERVICE_USERNAME and password == SERVICE_PASSWORD:
        # Generar el token JWT con un tiempo de expiración
        token = jwt.encode(
            {
                'sub': username,  # Identificador del sujeto (usuario)
                'exp': datetime.utcnow() + timedelta(seconds=EXPIRATION_TIME)  # Tiempo de expiración
            },
            SECRET_KEY,
            algorithm=ALGORITHM
        )
        
        # Devolver el token como respuesta
        return jsonify({"token": token}), 200
    else:
        # Si las credenciales son incorrectas
        return jsonify({"status": "error", "message": "Usuario o contraseña incorrectos"}), 401





# Decorador para proteger las rutas con JWT
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

        return f(*args, **kwargs)

    return decorated
