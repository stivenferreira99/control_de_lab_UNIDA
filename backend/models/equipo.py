from sqlalchemy import Column, Integer, String, Enum
from backend.db import Base
import re

class Equipo(Base):
    __tablename__ = 'equipo'

    id_equipo = Column(Integer, primary_key=True, autoincrement=True)
    nombre_pc = Column(String(100), unique=True, nullable=False)
    ip_equipo = Column(String(45), nullable=False)
    monitor = Column(String(50), nullable=True)
    gabinete = Column(String(50), nullable=True)
    teclado = Column(String(50), nullable=True)
    mouse = Column(String(50), nullable=True)
    receptor = Column(String(50), nullable=True)
    estado_equipo = Column(Enum('disponible', 'en uso', 'en reparación'), default='disponible')
    Laboratorio = Column(String(50), nullable=True)

    def __init__(self, nombre_pc, ip_equipo):
        self.nombre_pc = nombre_pc
        self.set_ip_equipo(ip_equipo)

    def set_ip_equipo(self, ip_equipo):
        if not self.validar_ip(ip_equipo):
            raise ValueError(f"Dirección IP inválida: {ip_equipo}")
        self.ip_equipo = ip_equipo

    def validar_ip(self, ip):
        patron_ip = re.compile(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")
        return bool(patron_ip.match(ip))

    def __repr__(self):
        return f"<Equipo(nombre_pc={self.nombre_pc}, ip_equipo={self.ip_equipo})>"

    @classmethod
    def update_equipo(cls, db_session, id_equipo, nombre_pc=None, ip_equipo=None):
        equipo = db_session.query(cls).filter_by(id_equipo=id_equipo).first()
        if not equipo:
            print(f"No se encontró el equipo con id {id_equipo}.")
            return

        if nombre_pc:
            equipo.nombre_pc = nombre_pc
        if ip_equipo:
            equipo.set_ip_equipo(ip_equipo)

        db_session.commit()
        print(f"Equipo {id_equipo} actualizado exitosamente.")
