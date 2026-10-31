# 💈 Barbearia Comunitária — MVP de Gestão de Agendamentos

[![CI Pipeline](https://github.com/JonathaSantos-ht/barbearia-comunitaria-mvp/actions/workflows/ci.yml/badge.svg)](https://github.com/JonathaSantos-ht/barbearia-comunitaria-mvp/actions)
![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.12%20%7C%203.14-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white)
![ODS 8](https://img.shields.io/badge/ODS-8%20Trabalho%20Decente-red)

> **Projeto de Software — Experiência Prática III**  
> Repositório público para implementação, versionamento e garantia de qualidade do MVP de agendamentos para o microempreendimento comunitário de barbearia do Sr. Carlos Alberto Moreira.

---

## 🎯 Contexto e ODS Vinculado
- **Público e Parceiro Comunitário:** Barbearia de bairro gerida por Denilson Venancio. O negócio sofria com sobreposição de horários e perda de clientes causada pelo controle em cadernos de papel e mensagens desorganizadas de WhatsApp.
- **Vínculo ODS:** **ODS 8 — Trabalho Decente e Crescimento Econômico** (Metas 8.2 e 8.3: produtividade, modernização tecnológica e formalização/eficiência de microempreendedores).
- **Solução Desenvolvida:** Sistema web responsivo mobile-first com grade semafórica visual (verde/vermelho), marcação rápida em 3 toques e cancelamento com liberação instantânea de horários.

---

## 🏗️ Arquitetura e Tecnologias
- **Linguagem & Runtime:** Python 3.14 / 3.12
- **Backend / API Web:** [FastAPI](https://fastapi.tiangolo.com/) com validação estrita via [Pydantic v2](https://docs.pydantic.dev/)
- **Persistência de Dados:** [SQLAlchemy ORM](https://www.sqlalchemy.org/) com banco de dados SQLite (`barbearia.db`)
- **Frontend / Interface:** HTML5 semântico integrado e estilizado via [Tailwind CSS CDN](https://tailwindcss.com/)
- **Qualidade & Testes:** [Pytest](https://docs.pytest.org/) com banco in-memory isolado
- **Integração Contínua (CI):** GitHub Actions automatizado (`.github/workflows/ci.yml`)

---

## 📂 Estrutura do Repositório

```text
barbearia-comunitaria-mvp/
├── .github/
│   └── workflows/
│       └── ci.yml               # Pipeline de Integração Contínua (GitHub Actions)
├── app/
│   ├── __init__.py
│   ├── database.py              # Conexão com banco SQLite e sessões
│   ├── models.py                # Modelos ORM (Cliente, Servico, Agendamento)
│   ├── schemas.py               # Schemas de validação Pydantic v2
│   ├── services.py              # Regras de negócio e prevenção de colisão
│   └── main.py                  # API FastAPI e interface visual responsiva
├── tests/
│   ├── __init__.py
│   └── test_services.py         # Testes automatizados unitários e de integração
├── .gitignore                   # Arquivos ignorados no versionamento
├── requirements.txt             # Dependências do projeto
├── run.py                       # Script direto de inicialização
└── README.md                    # Documentação do projeto
```

---

## 🚀 Como Executar o Projeto Localmente

### 1. Clonar o repositório ou baixar os arquivos
```bash
git clone https://github.com/JonathaSantos-ht/barbearia-comunitaria-mvp.git
cd barbearia-comunitaria-mvp
```

### 2. Instalar as dependências
```bash
pip install -r requirements.txt
```

### 3. Iniciar o servidor da aplicação
```bash
python run.py
```
*(ou se preferir: `python -m uvicorn app.main:app --reload`)*

### 4. Acessar a aplicação
- 📱 **Interface Visual do Usuário:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- 📑 **Documentação Interativa (Swagger API):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 🧪 Como Executar os Testes Automatizados

Os testes cobrem inicialização de serviços, verificação de horários disponíveis, criação de agendamentos, prevenção de choques de horário (colisão) e cancelamento com liberação imediata.

Execute no terminal:
```bash
python -m pytest tests/ -v
```

---

## ⚙️ Pipeline de Integração Contínua (CI)
O projeto conta com automação via GitHub Actions configurada em `.github/workflows/ci.yml`. A cada novo `push` ou `pull request`, a esteira do GitHub Actions:
1. Prepara uma máquina virtual Ubuntu;
2. Configura o ambiente Python 3.12 com cache de pacotes;
3. Instala todas as dependências do `requirements.txt`;
4. Roda a suíte completa de testes automatizados via `pytest`.
