from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    telefone = Column(String(20), nullable=False, index=True)
    criado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    agendamentos = relationship("Agendamento", back_populates="cliente")

class Servico(Base):
    __tablename__ = "servicos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(80), nullable=False, unique=True)
    duracao_minutos = Column(Integer, nullable=False, default=30)
    preco = Column(String(20), nullable=False)
    ativo = Column(Boolean, default=True)

    agendamentos = relationship("Agendamento", back_populates="servico")

class Agendamento(Base):
    __tablename__ = "agendamentos"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    servico_id = Column(Integer, ForeignKey("servicos.id"), nullable=False)
    data_str = Column(String(10), nullable=False, index=True) # YYYY-MM-DD
    horario_inicio = Column(String(5), nullable=False)        # HH:MM
    horario_fim = Column(String(5), nullable=False)           # HH:MM
    status = Column(String(20), default="agendado")           # agendado, cancelado, concluido

    cliente = relationship("Cliente", back_populates="agendamentos")
    servico = relationship("Servico", back_populates="agendamentos")
