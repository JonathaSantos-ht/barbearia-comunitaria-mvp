from sqlalchemy.orm import Session
from app.models import Cliente, Servico, Agendamento
from app.schemas import AgendamentoCreate
from datetime import datetime, timedelta

DEFAULT_HORARIOS = [
    "09:00", "09:45", "10:30", "11:15",
    "14:00", "14:45", "15:30", "16:15", "17:00", "17:45"
]

def init_default_servicos(db: Session):
    if db.query(Servico).count() == 0:
        db.add_all([
            Servico(nome="Corte Tradicional", duracao_minutos=30, preco="R$ 30,00"),
            Servico(nome="Barba Terapia", duracao_minutos=30, preco="R$ 25,00"),
            Servico(nome="Corte + Barba", duracao_minutos=45, preco="R$ 50,00"),
            Servico(nome="Acabamento / Pezinho", duracao_minutos=15, preco="R$ 15,00"),
        ])
        db.commit()

def get_grade_do_dia(db: Session, data_str: str):
    init_default_servicos(db)
    agendamentos = db.query(Agendamento).filter(
        Agendamento.data_str == data_str,
        Agendamento.status == "agendado"
    ).all()

    map_agendados = {a.horario_inicio: a for a in agendamentos}

    resultado = []
    for h in DEFAULT_HORARIOS:
        if h in map_agendados:
            ag = map_agendados[h]
            resultado.append({
                "id": ag.id,
                "horario": h,
                "status": "OCUPADO",
                "cliente_nome": ag.cliente.nome,
                "cliente_telefone": ag.cliente.telefone,
                "servico_nome": ag.servico.nome,
                "horario_fim": ag.horario_fim,
                "disponivel": False
            })
        else:
            resultado.append({
                "id": None,
                "horario": h,
                "status": "DISPONÍVEL",
                "cliente_nome": "Toque para agendar",
                "cliente_telefone": "",
                "servico_nome": "Horário Livre",
                "horario_fim": "",
                "disponivel": True
            })
    return resultado

def criar_agendamento(db: Session, dados: AgendamentoCreate):
    # 1. Verificar se horário já está ocupado (prevenção de conflito)
    existente = db.query(Agendamento).filter(
        Agendamento.data_str == dados.data_str,
        Agendamento.horario_inicio == dados.horario_inicio,
        Agendamento.status == "agendado"
    ).first()

    if existente:
        raise ValueError("Este horário já está ocupado por outro cliente.")

    # 2. Localizar ou cadastrar cliente
    cliente = db.query(Cliente).filter(Cliente.telefone == dados.telefone_cliente).first()
    if not cliente:
        cliente = Cliente(nome=dados.nome_cliente, telefone=dados.telefone_cliente)
        db.add(cliente)
        db.commit()
        db.refresh(cliente)

    # 3. Localizar serviço
    servico = db.query(Servico).filter(Servico.id == dados.servico_id).first()
    if not servico:
        raise ValueError("Serviço não encontrado.")

    # 4. Calcular horário fim
    h_ini = datetime.strptime(dados.horario_inicio, "%H:%M")
    h_fim = h_ini + timedelta(minutes=servico.duracao_minutos)
    horario_fim_str = h_fim.strftime("%H:%M")

    # 5. Criar agendamento
    novo_agendamento = Agendamento(
        cliente_id=cliente.id,
        servico_id=servico.id,
        data_str=dados.data_str,
        horario_inicio=dados.horario_inicio,
        horario_fim=horario_fim_str,
        status="agendado"
    )
    db.add(novo_agendamento)
    db.commit()
    db.refresh(novo_agendamento)
    return novo_agendamento

def cancelar_agendamento(db: Session, agendamento_id: int):
    ag = db.query(Agendamento).filter(Agendamento.id == agendamento_id).first()
    if not ag:
        raise ValueError("Agendamento não encontrado.")
    ag.status = "cancelado"
    db.commit()
    return True
