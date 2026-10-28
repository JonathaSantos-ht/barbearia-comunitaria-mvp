from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from datetime import date

from app.database import engine, Base, get_db
from app.models import Servico, Agendamento
from app.schemas import AgendamentoCreate
from app.services import (
    init_default_servicos,
    get_grade_do_dia,
    criar_agendamento,
    cancelar_agendamento,
)

# Criar tabelas automaticamente na inicialização
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Barbearia Comunitária MVP",
    description="Sistema de Gestão de Agendamentos para Barbearia Comunitária - Projeto de Software",
    version="1.0.0"
)

@app.on_event("startup")
def on_startup():
    db = next(get_db())
    init_default_servicos(db)

@app.get("/api/health")
def health_check():
    return {"status": "ok", "app": "Barbearia Comunitária MVP", "versao": "1.0.0"}

@app.get("/api/servicos")
def listar_servicos(db: Session = Depends(get_db)):
    init_default_servicos(db)
    servicos = db.query(Servico).filter(Servico.ativo == True).all()
    return [
        {
            "id": s.id,
            "nome": s.nome,
            "duracao_minutos": s.duracao_minutos,
            "preco": s.preco
        }
        for s in servicos
    ]

@app.get("/api/grade/{data_str}")
def obter_grade(data_str: str, db: Session = Depends(get_db)):
    try:
        grade = get_grade_do_dia(db, data_str)
        return grade
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/agendamentos")
def novo_agendamento(dados: AgendamentoCreate, db: Session = Depends(get_db)):
    try:
        ag = criar_agendamento(db, dados)
        return {
            "sucesso": True,
            "mensagem": "Agendamento confirmado com sucesso!",
            "id": ag.id,
            "cliente": ag.cliente.nome,
            "horario": f"{ag.horario_inicio} às {ag.horario_fim}"
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro interno ao processar agendamento.")

@app.post("/api/agendamentos/{agendamento_id}/cancelar")
def cancelar(agendamento_id: int, db: Session = Depends(get_db)):
    try:
        cancelar_agendamento(db, agendamento_id)
        return {"sucesso": True, "mensagem": "Horário cancelado e liberado com sucesso na grade!"}
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Interface Web Integrada (HTML5 + Tailwind CSS)
HTML_UI = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Barbearia Comunitária — Agendamentos</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .tap-target { min-height: 48px; min-width: 48px; }
    </style>
</head>
<body class="bg-slate-100 text-slate-800 font-sans antialiased min-h-screen flex flex-col items-center">

    <!-- Top Bar -->
    <header class="w-full bg-slate-900 text-white shadow-md">
        <div class="max-w-md mx-auto px-4 py-4 flex items-center justify-between">
            <div class="flex items-center space-x-3">
                <span class="text-2xl">✂️</span>
                <div>
                    <h1 class="text-lg font-bold tracking-tight leading-tight">Barbearia do Carlos</h1>
                    <p class="text-xs text-amber-400 font-medium">Comunidade & Tradição • ODS 8</p>
                </div>
            </div>
            <button onclick="carregarGrade()" class="tap-target bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs px-3 py-1.5 rounded-lg border border-slate-700 transition" title="Atualizar horários">
                🔄 Atualizar
            </button>
        </div>
    </header>

    <!-- Main Container -->
    <main class="w-full max-w-md px-4 py-4 flex-1 flex flex-col space-y-4">
        
        <!-- Painel de Data e Indicadores -->
        <section class="bg-white rounded-2xl p-4 shadow-sm border border-slate-200" aria-label="Seleção de Data e Legenda">
            <label for="data-selecionada" class="block text-xs font-semibold uppercase text-slate-500 mb-1">Escolha o dia de atendimento:</label>
            <input type="date" id="data-selecionada" class="tap-target w-full px-3 py-2 border-2 border-slate-300 rounded-xl font-bold text-slate-800 focus:outline-none focus:border-amber-500" onchange="carregarGrade()">
            
            <!-- Legenda Acessível (Cores + Ícones + Texto) -->
            <div class="mt-3 pt-3 border-t border-slate-100 flex items-center justify-around text-xs font-medium">
                <div class="flex items-center space-x-1.5 text-emerald-800">
                    <span class="w-3 h-3 rounded-full bg-emerald-500 inline-block"></span>
                    <span>🟢 <strong>LIVRE</strong> (Disponível)</span>
                </div>
                <div class="flex items-center space-x-1.5 text-rose-800">
                    <span class="w-3 h-3 rounded-full bg-rose-500 inline-block"></span>
                    <span>🔴 <strong>OCUPADO</strong> (Reservado)</span>
                </div>
            </div>
        </section>

        <!-- Grade de Horários (Tela 1 - Semáforo) -->
        <section aria-label="Grade de Horários">
            <div class="flex items-center justify-between mb-2">
                <h2 class="text-sm font-bold text-slate-700 uppercase tracking-wide">Horários do Dia</h2>
                <span id="contagem-vagas" class="text-xs font-semibold bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full">Carregando...</span>
            </div>
            
            <div id="lista-horarios" class="space-y-2.5">
                <!-- Inserido dinamicamente via JS -->
            </div>
        </section>
    </main>

    <!-- Modal de Agendamento Rápido (Tela 2) -->
    <div id="modal-agendamento" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm hidden z-50 flex items-end sm:items-center justify-center p-0 sm:p-4">
        <div class="bg-white w-full max-w-md rounded-t-3xl sm:rounded-2xl p-6 shadow-2xl border border-slate-200 transform transition-all">
            <div class="flex items-center justify-between pb-3 border-b border-slate-100">
                <h3 class="text-lg font-bold text-slate-900">Novo Agendamento</h3>
                <button onclick="fecharModalAgendamento()" class="text-slate-400 hover:text-slate-600 text-2xl leading-none">&times;</button>
            </div>

            <form id="form-agendamento" onsubmit="salvarAgendamento(event)" class="mt-4 space-y-4">
                <div class="bg-amber-50 border border-amber-200 rounded-xl p-3 flex items-center justify-between">
                    <span class="text-xs font-bold text-amber-900 uppercase">Horário Escolhido:</span>
                    <span id="label-horario-selecionado" class="text-base font-extrabold text-amber-900">09:00</span>
                </div>

                <div>
                    <label for="nome-cliente" class="block text-xs font-bold text-slate-700 mb-1">Nome Completo *</label>
                    <input type="text" id="nome-cliente" required minlength="3" placeholder="Ex: João da Silva" class="tap-target w-full px-3 py-2 border-2 border-slate-300 rounded-xl text-slate-800 focus:outline-none focus:border-amber-500">
                </div>

                <div>
                    <label for="telefone-cliente" class="block text-xs font-bold text-slate-700 mb-1">WhatsApp / Telefone *</label>
                    <input type="tel" id="telefone-cliente" required minlength="8" placeholder="Ex: (11) 98765-4321" class="tap-target w-full px-3 py-2 border-2 border-slate-300 rounded-xl text-slate-800 focus:outline-none focus:border-amber-500">
                </div>

                <div>
                    <label for="servico-select" class="block text-xs font-bold text-slate-700 mb-1">Serviço Desejado *</label>
                    <select id="servico-select" required class="tap-target w-full px-3 py-2 border-2 border-slate-300 rounded-xl text-slate-800 focus:outline-none focus:border-amber-500 bg-white">
                        <!-- Carregado via JS -->
                    </select>
                </div>

                <div id="msg-erro-agendamento" class="hidden text-xs text-rose-600 font-bold bg-rose-50 p-2.5 rounded-lg border border-rose-200"></div>

                <div class="flex space-x-3 pt-2">
                    <button type="button" onclick="fecharModalAgendamento()" class="tap-target flex-1 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold py-2.5 px-4 rounded-xl transition">Cancelar</button>
                    <button type="submit" id="btn-confirmar-agendamento" class="tap-target flex-1 bg-amber-500 hover:bg-amber-600 text-slate-950 font-extrabold py-2.5 px-4 rounded-xl shadow-md transition">Confirmar</button>
                </div>
            </form>
        </div>
    </div>

    <!-- Modal de Detalhes / Cancelamento (Tela 3) -->
    <div id="modal-cancelamento" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm hidden z-50 flex items-end sm:items-center justify-center p-0 sm:p-4">
        <div class="bg-white w-full max-w-md rounded-t-3xl sm:rounded-2xl p-6 shadow-2xl border border-slate-200">
            <div class="flex items-center justify-between pb-3 border-b border-slate-100">
                <div class="flex items-center space-x-2">
                    <span class="w-3 h-3 rounded-full bg-rose-500 inline-block"></span>
                    <h3 class="text-lg font-bold text-slate-900">Horário Agendado</h3>
                </div>
                <button onclick="fecharModalCancelamento()" class="text-slate-400 hover:text-slate-600 text-2xl leading-none">&times;</button>
            </div>

            <div class="mt-4 space-y-3 bg-slate-50 p-4 rounded-2xl border border-slate-200">
                <div>
                    <span class="text-xs text-slate-500 font-medium">Cliente:</span>
                    <p id="detalhe-cliente-nome" class="text-base font-bold text-slate-900">Carlos Silva</p>
                </div>
                <div>
                    <span class="text-xs text-slate-500 font-medium">Telefone / Contato:</span>
                    <p id="detalhe-cliente-telefone" class="text-sm font-semibold text-slate-800">(11) 98888-7777</p>
                </div>
                <div>
                    <span class="text-xs text-slate-500 font-medium">Serviço:</span>
                    <p id="detalhe-servico" class="text-sm font-semibold text-slate-800">Corte Tradicional</p>
                </div>
                <div>
                    <span class="text-xs text-slate-500 font-medium">Horário reservado:</span>
                    <p id="detalhe-horario" class="text-sm font-bold text-amber-700">10:30 até 11:00</p>
                </div>
            </div>

            <p class="text-xs text-slate-500 mt-3 text-center">Ao cancelar, este horário é liberado imediatamente para outros clientes da comunidade.</p>

            <div class="flex space-x-3 mt-4">
                <button type="button" onclick="fecharModalCancelamento()" class="tap-target flex-1 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold py-2.5 px-4 rounded-xl transition">Voltar</button>
                <button type="button" onclick="executarCancelamento()" id="btn-confirmar-cancelar" class="tap-target flex-1 bg-rose-600 hover:bg-rose-700 text-white font-extrabold py-2.5 px-4 rounded-xl shadow-md transition">Liberar Horário</button>
            </div>
        </div>
    </div>

    <!-- Feedback Toast -->
    <div id="toast" class="fixed bottom-5 left-1/2 -translate-x-1/2 bg-slate-900 text-white text-sm font-semibold px-5 py-3 rounded-2xl shadow-xl hidden transition-all z-50 flex items-center space-x-2">
        <span id="toast-icon">✅</span>
        <span id="toast-text">Operação realizada!</span>
    </div>

    <!-- Script de Interação -->
    <script>
        let servicosCache = [];
        let horarioSelecionado = null;
        let agendamentoSelecionadoId = null;

        // Inicializar com a data de hoje (YYYY-MM-DD local)
        const hoje = new Date().toISOString().split('T')[0];
        document.getElementById('data-selecionada').value = hoje;

        async function carregarServicos() {
            try {
                const res = await fetch('/api/servicos');
                servicosCache = await res.json();
                const select = document.getElementById('servico-select');
                select.innerHTML = servicosCache.map(s => 
                    `<option value="${s.id}">${s.nome} — ${s.preco} (${s.duracao_minutos} min)</option>`
                ).join('');
            } catch (e) {
                console.error("Erro ao carregar serviços", e);
            }
        }

        async function carregarGrade() {
            const dataStr = document.getElementById('data-selecionada').value;
            const container = document.getElementById('lista-horarios');
            const contagemEl = document.getElementById('contagem-vagas');
            
            container.innerHTML = '<div class="text-center py-8 text-slate-400 font-medium text-sm">Carregando horários...</div>';

            try {
                const res = await fetch(`/api/grade/${dataStr}`);
                const grade = await res.json();

                let livres = grade.filter(g => g.disponivel).length;
                contagemEl.textContent = `${livres} de ${grade.length} livres`;
                contagemEl.className = livres > 0 
                    ? "text-xs font-semibold bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full"
                    : "text-xs font-semibold bg-rose-100 text-rose-800 px-2 py-0.5 rounded-full";

                container.innerHTML = '';
                grade.forEach(item => {
                    const card = document.createElement('div');
                    if (item.disponivel) {
                        card.className = "tap-target p-3.5 bg-white border-2 border-emerald-500 hover:bg-emerald-50 rounded-2xl flex items-center justify-between shadow-sm cursor-pointer transition";
                        card.setAttribute('role', 'button');
                        card.setAttribute('aria-label', `Horário ${item.horario} disponível. Toque para agendar.`);
                        card.onclick = () => abrirModalAgendamento(item.horario);
                        card.innerHTML = `
                            <div class="flex items-center space-x-3">
                                <span class="text-lg font-black text-slate-900 bg-slate-100 px-2.5 py-1 rounded-xl">${item.horario}</span>
                                <div>
                                    <div class="flex items-center space-x-1.5">
                                        <span class="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
                                        <span class="text-xs font-extrabold text-emerald-700 uppercase tracking-wide">LIVRE</span>
                                    </div>
                                    <p class="text-xs text-slate-500 font-medium">Toque para agendar</p>
                                </div>
                            </div>
                            <span class="text-xs font-bold text-emerald-700 bg-emerald-100 px-3 py-1.5 rounded-xl">+ Agendar</span>
                        `;
                    } else {
                        card.className = "tap-target p-3.5 bg-rose-50/70 border-2 border-rose-300 rounded-2xl flex items-center justify-between shadow-sm cursor-pointer transition hover:bg-rose-100/60";
                        card.setAttribute('role', 'button');
                        card.setAttribute('aria-label', `Horário ${item.horario} ocupado por ${item.cliente_nome}. Toque para ver detalhes ou cancelar.`);
                        card.onclick = () => abrirModalCancelamento(item);
                        card.innerHTML = `
                            <div class="flex items-center space-x-3">
                                <span class="text-lg font-black text-slate-700 bg-white/80 px-2.5 py-1 rounded-xl">${item.horario}</span>
                                <div>
                                    <div class="flex items-center space-x-1.5">
                                        <span class="w-2.5 h-2.5 rounded-full bg-rose-500"></span>
                                        <span class="text-xs font-extrabold text-rose-700 uppercase tracking-wide">OCUPADO</span>
                                    </div>
                                    <p class="text-xs text-slate-800 font-semibold truncate max-w-[170px]">${item.cliente_nome}</p>
                                </div>
                            </div>
                            <span class="text-xs font-semibold text-rose-800 bg-white border border-rose-200 px-2.5 py-1.5 rounded-xl">Detalhes</span>
                        `;
                    }
                    container.appendChild(card);
                });
            } catch (e) {
                container.innerHTML = '<div class="text-center py-6 text-rose-500 text-sm font-semibold">Erro ao carregar horários. Verifique a conexão.</div>';
            }
        }

        function abrirModalAgendamento(horario) {
            horarioSelecionado = horario;
            document.getElementById('label-horario-selecionado').textContent = horario;
            document.getElementById('msg-erro-agendamento').classList.add('hidden');
            document.getElementById('modal-agendamento').classList.remove('hidden');
            document.getElementById('nome-cliente').focus();
        }

        function fecharModalAgendamento() {
            document.getElementById('modal-agendamento').classList.add('hidden');
            document.getElementById('form-agendamento').reset();
        }

        async function salvarAgendamento(e) {
            e.preventDefault();
            const btn = document.getElementById('btn-confirmar-agendamento');
            const erroEl = document.getElementById('msg-erro-agendamento');
            btn.disabled = true;
            btn.textContent = "Agendando...";

            const payload = {
                nome_cliente: document.getElementById('nome-cliente').value.trim(),
                telefone_cliente: document.getElementById('telefone-cliente').value.trim(),
                servico_id: parseInt(document.getElementById('servico-select').value),
                data_str: document.getElementById('data-selecionada').value,
                horario_inicio: horarioSelecionado
            };

            try {
                const res = await fetch('/api/agendamentos', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                if (!res.ok) throw new Error(data.detail || "Erro ao agendar.");

                fecharModalAgendamento();
                mostrarToast("✅ " + data.mensagem);
                carregarGrade();
            } catch (err) {
                erroEl.textContent = err.message;
                erroEl.classList.remove('hidden');
            } finally {
                btn.disabled = false;
                btn.textContent = "Confirmar";
            }
        }

        function abrirModalCancelamento(item) {
            agendamentoSelecionadoId = item.id;
            document.getElementById('detalhe-cliente-nome').textContent = item.cliente_nome;
            document.getElementById('detalhe-cliente-telefone').textContent = item.cliente_telefone || "Não informado";
            document.getElementById('detalhe-servico').textContent = item.servico_nome;
            document.getElementById('detalhe-horario').textContent = `${item.horario} até ${item.horario_fim}`;
            document.getElementById('modal-cancelamento').classList.remove('hidden');
        }

        function fecharModalCancelamento() {
            document.getElementById('modal-cancelamento').classList.add('hidden');
            agendamentoSelecionadoId = null;
        }

        async function executarCancelamento() {
            if (!agendamentoSelecionadoId) return;
            const btn = document.getElementById('btn-confirmar-cancelar');
            btn.disabled = true;
            btn.textContent = "Liberando...";

            try {
                const res = await fetch(`/api/agendamentos/${agendamentoSelecionadoId}/cancelar`, { method: 'POST' });
                const data = await res.json();
                if (!res.ok) throw new Error(data.detail || "Erro ao cancelar.");

                fecharModalCancelamento();
                mostrarToast("🗑️ Horário liberado na grade!");
                carregarGrade();
            } catch (err) {
                alert("Erro ao cancelar: " + err.message);
            } finally {
                btn.disabled = false;
                btn.textContent = "Liberar Horário";
            }
        }

        function mostrarToast(msg) {
            const toast = document.getElementById('toast');
            document.getElementById('toast-text').textContent = msg;
            toast.classList.remove('hidden');
            setTimeout(() => toast.classList.add('hidden'), 3500);
        }

        // Carregamento inicial
        carregarServicos();
        carregarGrade();
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def index():
    return HTMLResponse(content=HTML_UI)
