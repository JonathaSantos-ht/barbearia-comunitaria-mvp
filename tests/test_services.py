import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import Servico, Cliente, Agendamento
from app.schemas import AgendamentoCreate
from app.services import (
    init_default_servicos,
    get_grade_do_dia,
    criar_agendamento,
    cancelar_agendamento
)

# Banco SQLite em memória para isolar testes
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture
def db_session():
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    init_default_servicos(session)
    try:
        yield session
    finally:
        session.close()

def test_inicializacao_servicos_padrao(db_session):
    servicos = db_session.query(Servico).all()
    assert len(servicos) == 4
    nomes = [s.nome for s in servicos]
    assert "Corte Tradicional" in nomes
    assert "Barba Terapia" in nomes

def test_grade_do_dia_inicialmente_livre(db_session):
    data_teste = "2026-10-30"
    grade = get_grade_do_dia(db_session, data_teste)
    assert len(grade) == 10
    # Todos devem estar disponíveis
    for slot in grade:
        assert slot["disponivel"] is True
        assert slot["status"] == "DISPONÍVEL"

def test_criar_agendamento_com_sucesso(db_session):
    data_teste = "2026-10-30"
    servico = db_session.query(Servico).filter_by(nome="Corte Tradicional").first()
    
    dados = AgendamentoCreate(
        nome_cliente="Carlos Eduardo",
        telefone_cliente="11999998888",
        servico_id=servico.id,
        data_str=data_teste,
        horario_inicio="09:00"
    )
    
    ag = criar_agendamento(db_session, dados)
    assert ag.id is not None
    assert ag.horario_inicio == "09:00"
    assert ag.horario_fim == "09:30"
    assert ag.status == "agendado"
    assert ag.cliente.nome == "Carlos Eduardo"

    # Verificar que na grade o horário agora está ocupado
    grade = get_grade_do_dia(db_session, data_teste)
    slot_09 = next(s for s in grade if s["horario"] == "09:00")
    assert slot_09["disponivel"] is False
    assert slot_09["status"] == "OCUPADO"
    assert slot_09["cliente_nome"] == "Carlos Eduardo"

def test_prevencao_choque_de_horarios(db_session):
    data_teste = "2026-10-30"
    servico = db_session.query(Servico).first()
    
    dados1 = AgendamentoCreate(
        nome_cliente="Primeiro Cliente",
        telefone_cliente="11911112222",
        servico_id=servico.id,
        data_str=data_teste,
        horario_inicio="10:30"
    )
    criar_agendamento(db_session, dados1)

    # Tentativa de agendamento no mesmo horário deve lançar ValueError
    dados2 = AgendamentoCreate(
        nome_cliente="Segundo Cliente",
        telefone_cliente="11933334444",
        servico_id=servico.id,
        data_str=data_teste,
        horario_inicio="10:30"
    )
    with pytest.raises(ValueError) as excinfo:
        criar_agendamento(db_session, dados2)
    assert "já está ocupado" in str(excinfo.value)

def test_cancelamento_e_liberacao_imediata(db_session):
    data_teste = "2026-10-30"
    servico = db_session.query(Servico).first()
    
    dados = AgendamentoCreate(
        nome_cliente="Cliente a Cancelar",
        telefone_cliente="11955556666",
        servico_id=servico.id,
        data_str=data_teste,
        horario_inicio="14:00"
    )
    ag = criar_agendamento(db_session, dados)
    assert ag.status == "agendado"

    # Cancelar agendamento
    cancelado = cancelar_agendamento(db_session, ag.id)
    assert cancelado is True

    # Verificar que o horário 14:00 voltou a estar LIVRE
    grade = get_grade_do_dia(db_session, data_teste)
    slot_14 = next(s for s in grade if s["horario"] == "14:00")
    assert slot_14["disponivel"] is True
    assert slot_14["status"] == "DISPONÍVEL"
