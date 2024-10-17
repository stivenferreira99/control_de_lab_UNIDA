from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from backend.db import Base

class Maquina(Base):
    __tablename__ = 'maquinas'
    
    id_maquina = Column(Integer, primary_key=True)
    nombre_maquina = Column(String(50), nullable=False)  # Longitud definida
    ip_maquina = Column(String(15), nullable=False)       # Longitud definida
    estado = Column(String(20), nullable=False)           # Longitud definida

    # Relación con la tabla de sesiones
    sesiones = relationship("Sesion", back_populates="maquina")

