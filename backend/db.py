from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import mysql.connector  # Make sure this package is installed
from mysql.connector import Error

# Database URL and connection settings
DATABASE_URL = "mysql+mysqlconnector://root:1234@localhost/proyectosui?auth_plugin=mysql_native_password"

# Create the database engine
try:
    engine = create_engine(DATABASE_URL)
    # Test the connection
    connection = engine.connect()
    print("Conexión a la base de datos exitosa.")
    connection.close()  # Close the connection after verification
except Exception as e:
    print("Error al conectar a la base de datos:", str(e))

# Configure session management for SQLAlchemy
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base for ORM models
Base = declarative_base()

# Function to get a direct connection to MySQL (if needed outside of ORM)
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='1234',
            database='proyectosui',
            auth_plugin='mysql_native_password'  # Corrected auth plugin
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error al conectarse a la base de datos: {e}")
        return None

# Function to initialize the database and create all tables
def init_db():
    # Import ORM models here to ensure tables are created
    from backend.models.alumno import Alumno
    from backend.models.maquina import Maquina
    from backend.models.sesion import Sesion

    # Create all tables in the database (equivalent to "create if not exists")
    Base.metadata.create_all(bind=engine)
