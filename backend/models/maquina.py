from sqlalchemy import Column, Integer, String
from backend.db import Base
import re

class Maquina(Base):
    __tablename__ = 'maquinas'

    id_maquina = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), unique=True, nullable=False)
    ip_maquina = Column(String(45), nullable=False)

    def __init__(self, nombre, ip_maquina):
        self.nombre = nombre
        self.set_ip_maquina(ip_maquina)

    def set_ip_maquina(self, ip_maquina):
        if not self.validar_ip(ip_maquina):
            raise ValueError(f"Dirección IP inválida: {ip_maquina}")
        self.ip_maquina = ip_maquina

    def validar_ip(self, ip):
        patron_ip = re.compile(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")
        return bool(patron_ip.match(ip))

    def __repr__(self):
        return f"<Maquina(nombre={self.nombre}, ip_maquina={self.ip_maquina})>"

    @classmethod
    def update_maquina(cls, db_session, id_maquina, nombre=None, ip_maquina=None):
        maquina = db_session.query(cls).filter_by(id_maquina=id_maquina).first()
        if not maquina:
            print(f"No se encontró la máquina con id {id_maquina}.")
            return

        if nombre:
            maquina.nombre = nombre
        if ip_maquina:
            maquina.set_ip_maquina(ip_maquina)
        
        db_session.commit()
        print(f"Máquina {id_maquina} actualizada exitosamente.")
