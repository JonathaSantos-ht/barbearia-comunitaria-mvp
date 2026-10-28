import uvicorn

if __name__ == "__main__":
    print("================================================================")
    print("💈 Iniciando Barbearia Comunitária MVP...")
    print("🌐 Acesse no seu navegador: http://127.0.0.1:8000")
    print("📑 Documentação da API (Swagger): http://127.0.0.1:8000/docs")
    print("🛑 Pressione Ctrl+C para encerrar o servidor.")
    print("================================================================")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
