from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class AgendamentoCreate(BaseModel):
    nome_cliente: str = Field(..., min_length=3, max_length=100)
    telefone_cliente: str = Field(..., min_length=8, max_length=20)
    servico_id: int
    data_str: str = Field(..., min_length=10, max_length=10) # YYYY-MM-DD
    horario_inicio: str = Field(..., min_length=5, max_length=5) # HH:MM

class AgendamentoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cliente_nome: str
    cliente_telefone: str
    servico_nome: str
    data_str: str
    horario_inicio: str
    horario_fim: str
    status: str
