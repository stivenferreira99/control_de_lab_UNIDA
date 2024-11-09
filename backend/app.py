from flask import Flask
from .db import init_db
from backend.routes.auth import auth_blueprint
from backend.routes.alumnos import alumnos_blueprint
from backend.routes.session import session_blueprint  # Importar el blueprint de sesión
from backend.routes.maquina import maquina_blueprint  # Importar el blueprint de maquina


def create_app():
    app = Flask(__name__)

    # Inicializar la base de datos (si es necesario)
    init_db()

    # Registrar blueprints
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(alumnos_blueprint, url_prefix='/alumnos')
    app.register_blueprint(session_blueprint, url_prefix='/session')
    app.register_blueprint(maquina_blueprint, url_prefix='/maquina')

    return app

if __name__ == '__main__':
    app = create_app()
    app.config['DEBUG'] = True
    app.run(host='127.0.0.1', port=5000)  # Cambia 5001 por cualquier puerto disponible
