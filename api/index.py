import os
import sys

# Adicionar raiz ao PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app

# Exportar a aplicacao para o runtime serverless da Vercel
app = app
