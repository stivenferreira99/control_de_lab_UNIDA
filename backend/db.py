from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import mysql.connector  # Asegúrate de que este paquete esté instalado
from mysql.connector import Error

# URL de la base de datos
DATABASE_URL = "mysql+mysqlconnector://root:1234@localhost/lab"

# Crear el motor de la base de datos
try:
    engine = create_engine(DATABASE_URL)
    # Probar la conexión
    connection = engine.connect()
    print("Conexión a la base de datos exitosa.")
    connection.close()  # Cierra la conexión después de la verificación
except Exception as e:
    print("Error al conectar a la base de datos:", str(e))

# Crear una sesión de base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base
Base = declarative_base()

# Función para obtener una conexión a la base de datos
def get_db_connection():
    
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='1234',
            database='lab'
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error al conectarse a la base de datos: {e}")
        return None
    
    
# Función para inicializar la base de datos
def init_db():
    from backend.models.alumno import Alumno  # Importación absoluta
    from backend.models.maquina import Maquina  # Importación absoluta
    from backend.models.sesion import Sesion  # Importación absoluta

    Base.metadata.create_all(bind=engine)
