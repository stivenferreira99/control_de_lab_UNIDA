from datetime import datetime, timedelta
import jwt  # Asegúrate de que sea la biblioteca PyJWT
import base64
from functools import wraps
from flask import request, jsonify

# Clave secreta para firmar los JWT
SECRET_KEY = '1234'
ALGORITHM = 'HS256'
EXPIRATION_TIME = 3600  # 1 hora de duración del token

# Función para generar el token JWT
def generate_token(username):
    try:
        # Crear el payload
        payload = {
            'sub': username,  # Identificador del sujeto (usuario)
            'exp': datetime.utcnow() + timedelta(seconds=EXPIRATION_TIME)  # Tiempo de expiración
        }

        # Generar el token
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

        # Codificar el token en Base64 (opcional)
        base64_token = base64.urlsafe_b64encode(token.encode()).decode()

        return base64_token
    except Exception as e:
        return None, f"Error al generar el token: {str(e)}"


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
