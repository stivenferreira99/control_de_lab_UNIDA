from flask import Flask
from backend.db import init_db  # Asegúrate de que tienes la función de inicialización de base de datos
from backend.routes.auth import auth_blueprint
from backend.routes.alumnos import alumnos_blueprint
from backend.routes.session import session_blueprint  # Importar el blueprint de sesión

def create_app():
    app = Flask(__name__)

    # Inicializar la base de datos (si es necesario)
    init_db()

    # Registrar blueprints
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(alumnos_blueprint, url_prefix='/alumnos')
    app.register_blueprint(session_blueprint, url_prefix='/session')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)  # Ejecutar la aplicación
