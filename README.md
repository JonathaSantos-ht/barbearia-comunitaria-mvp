# 💈 Barbearia Comunitária — Sistema Ágil de Agendamentos (MVP)

[![CI Pipeline](https://github.com/JonathaSantos-ht/barbearia-comunitaria-mvp/actions/workflows/ci.yml/badge.svg)](https://github.com/JonathaSantos-ht/barbearia-comunitaria-mvp/actions)
![Python Version](https://img.shields.io/badge/python-3.12-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-009688.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

MVP desenvolvido para a disciplina de **Projeto de Software**, com foco em modernização operacional e impacto social no comércio local, em conformidade com o **ODS 8 da ONU (Trabalho Decente e Crescimento Econômico)**.

---

## 📌 Contexto e Problema Diagnosticado

O projeto atende a uma pequena **Barbearia Comunitária**, cujo fluxo de agendamentos era realizado de maneira 100% manual em cadernos de papel, com solicitações recebidas presencialmente ou por chamadas telefônicas. Esse modelo arcaico gerava frequentes conflitos de horários (marcações duplicadas), ociosidade imprevista na cadeira e interrupções contínuas durante a prestação dos serviços.

### 🎯 Solução Proposta (MVP)
Uma aplicação web responsiva (Mobile-First) projetada para operação rápida em smartphones com uma só mão:
* **Grade Semafórica de Horários:** Identificação visual instantânea de horários livres (verde) e ocupados (cinza).
* **Agendamento Rápido em Três Toques:** Registro de nome, telefone e serviço em menos de 30 segundos.
* **Liberação e Cancelamento Imediato:** Reabertura automática de horários desmarcados na grade diária.

---

## 🛠️ Pilha Tecnológica (Stack)

* **Linguagem Principal:** Python 3.12
* **Backend / API REST:** FastAPI 0.111.0 + Pydantic
* **Persistência / ORM:** SQLAlchemy 2.0.x (PostgreSQL em nuvem / SQLite local)
* **Frontend:** HTML5 semântico, JavaScript e Tailwind CSS (Mobile-First)
* **Segurança:** Autenticação com hash `bcrypt` ($2b$12$) via `passlib` e tokens JWT
* **Testes e CI:** `pytest`, `pytest-cov` e GitHub Actions

---

## 📂 Estrutura do Repositório

```bash
barbearia-comunitaria-mvp/
├── .github/
│   └── workflows/
│       └── ci.yml               # Pipeline de Integração Contínua (CI)
├── app/
│   ├── core/
│   │   ├── config.py            # Variáveis de ambiente e segredos
│   │   └── security.py          # Hashing bcrypt e tokens JWT
│   ├── models/                  # Modelos relacionais SQLAlchemy (clientes, servicos, agendamentos)
│   ├── schemas/                 # Esquemas de validação Pydantic
│   ├── services/                # Regras de negócio (prevenção de conflito de horários)
│   ├── api/                     # Rotas e controladores REST da FastAPI
│   └── main.py                  # Ponto de entrada da aplicação
├── tests/
│   ├── test_services.py         # Testes unitários das regras de agendamento
│   └── test_api.py              # Testes de integração dos endpoints REST
├── requirements.txt             # Dependências estritas do projeto
├── .gitignore                   # Arquivos ignorados (venv, .env, __pycache__)
└── README.md                    # Documentação do projeto
```

---

## 🚀 Como Executar o Projeto Localmente

1. **Clonar o repositório:**
   ```bash
   git clone https://github.com/JonathaSantos-ht/barbearia-comunitaria-mvp.git
   cd barbearia-comunitaria-mvp
   ```

2. **Criar e ativar o ambiente virtual:**
   ```bash
   python -m venv venv
   # No Windows:
   venv\Scripts\activate
   # No Linux/Mac:
   source venv/bin/activate
   ```

3. **Instalar as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Executar a aplicação:**
   ```bash
   uvicorn app.main:app --reload
   ```
   Acesse a documentação interativa Swagger em: `http://127.0.0.1:8000/docs`

5. **Executar os testes automatizados:**
   ```bash
   pytest --cov=app tests/
   ```

---

## 📄 Licença
Distribuído sob a licença MIT. Veja `LICENSE` para mais informações.
* **Segurança:** Autenticação com hash `bcrypt` ($2b$12$) via `passlib` e tokens JWT
* **Testes e CI:** `pytest`, `pytest-cov` e GitHub Actions

---

## 📂 Estrutura do Repositório

```bash
barbearia-comunitaria-mvp/
├── .github/
│   └── workflows/
│       └── ci.yml               # Pipeline de Integração Contínua (CI)
├── app/
│   ├── core/
│   │   ├── config.py            # Variáveis de ambiente e segredos
│   │   └── security.py          # Hashing bcrypt e tokens JWT
│   ├── models/                  # Modelos relacionais SQLAlchemy (clientes, servicos, agendamentos)
│   ├── schemas/                 # Esquemas de validação Pydantic
│   ├── services/                # Regras de negócio (prevenção de conflito de horários)
│   ├── api/                     # Rotas e controladores REST da FastAPI
│   └── main.py                  # Ponto de entrada da aplicação
├── tests/
│   ├── test_services.py         # Testes unitários das regras de agendamento
│   └── test_api.py              # Testes de integração dos endpoints REST
├── requirements.txt             # Dependências estritas do projeto
├── .gitignore                   # Arquivos ignorados (venv, .env, __pycache__)
└── README.md                    # Documentação do projeto
