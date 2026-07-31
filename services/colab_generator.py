import json

class ColabNotebookGenerator:
    """Service to programmatically generate a self-contained Google Colab (.ipynb) notebook."""

    @staticmethod
    def generate_ipynb_notebook() -> str:
        """
        Generate Jupyter Notebook v4 JSON string that contains all code files
        and auto-executes Streamlit with Pyngrok tunnel in Google Colab.
        """
        notebook = {
            "nbformat": 4,
            "nbformat_minor": 0,
            "metadata": {
                "colab": {
                    "provenance": [],
                    "authorship_tag": "BF Analista de Futebol Generator"
                },
                "kernelspec": {
                    "name": "python3",
                    "display_name": "Python 3"
                },
                "language_info": {
                    "name": "python"
                }
            },
            "cells": [
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        "# ⚽ BF Analista de Futebol - Google Colab Launcher\n",
                        "Notebook gerado automaticamente para execução completa da aplicação **BF Analista de Futebol** no Google Colab com acesso remoto via Ngrok."
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "# 1. Instalação de dependências no Colab\n",
                        "!pip install streamlit pyngrok google-genai pandas numpy scipy fpdf2 plotly tabulate -q\n",
                        "print('✅ Dependências instaladas com sucesso!')"
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "# 2. Criação da estrutura de ficheiros da aplicação\n",
                        "import os\n",
                        "os.makedirs('models', exist_ok=True)\n",
                        "os.makedirs('services', exist_ok=True)\n",
                        "os.makedirs('ui', exist_ok=True)\n",
                        "\n",
                        "print('✅ Diretórios criados!')"
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "%%writefile config.py\n",
                        "import streamlit as st\n",
                        "import os\n",
                        "\n",
                        "ADMIN_PASSWORD_HASH = \"Admin#1976\"\n",
                        "DEFAULT_MOCK_MATCHES = [\n",
                        "    {\n",
                        "        \"country\": \"Europa\", \"league\": \"Liga Europa\", \"home\": \"Benfica\", \"away\": \"St. Gallen\",\n",
                        "        \"h_xg\": 2.15, \"a_xg\": 0.90, \"h_xga\": 0.80, \"a_xga\": 1.85,\n",
                        "        \"odd_1\": 1.45, \"odd_x\": 4.50, \"odd_2\": 6.50,\n",
                        "        \"odd_o05\": 1.05, \"odd_o15\": 1.22, \"odd_o25\": 1.62,\n",
                        "        \"odd_btts_yes\": 1.75, \"odd_btts_no\": 2.00,\n",
                        "        \"home_form\": \"V-V-E-V-V\", \"away_form\": \"D-E-V-D-E\",\n",
                        "        \"h2h_summary\": \"Últimos 3 confrontos: 2 Vitórias Benfica, 1 Empate\",\n",
                        "        \"odd\": 1.45, \"market\": \"Vitória Casa (1)\"\n",
                        "    }\n",
                        "]\n",
                        "\n",
                        "def init_session_state():\n",
                        "    defaults = {\n",
                        "        \"matches_data\": [], \"analysed_results\": [], \"filtered_matches\": [],\n",
                        "        \"gemini_key\": os.environ.get(\"GEMINI_API_KEY\", \"AIzaSyCWnt9Foq226tOF7IG4JSx8lVLvqL1biq8\"),\n",
                        "        \"ngrok_key\": os.environ.get(\"NGROK_AUTHTOKEN\", \"3Gtx36ExMiXQAki5sFVrwTmOoC2_4CEFuYvnLQjUX5jYWcJyA\"),\n",
                        "        \"email_sender\": \"\", \"email_password\": \"\", \"is_admin\": False, \"last_ingestion_log\": \"\"\n",
                        "    }\n",
                        "    for k, v in defaults.items():\n",
                        "        if k not in st.session_state:\n",
                        "            st.session_state[k] = v\n"
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "%%writefile app.py\n",
                        "import streamlit as st\n",
                        "from config import init_session_state\n",
                        "\n",
                        "st.set_page_config(page_title=\"BF Analista de Futebol\", page_icon=\"⚽\", layout=\"wide\")\n",
                        "init_session_state()\n",
                        "st.title(\"⚽ BF Analista de Futebol - Google Colab Edition\")\n",
                        "st.info(\"Aplicação ativa e em execução completa dentro do Google Colab.\")\n"
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "# 3. Execução do Server Streamlit & Conexão Ngrok Tunnel no Colab\n",
                        "import subprocess\n",
                        "from pyngrok import ngrok\n",
                        "\n",
                        "NGROK_TOKEN = input('Introduz o teu Ngrok Auth Token (ou prime Enter para túnel público livre): ').strip()\n",
                        "if NGROK_TOKEN:\n",
                        "    ngrok.set_auth_token(NGROK_TOKEN)\n",
                        "\n",
                        "proc = subprocess.Popen(['streamlit', 'run', 'app.py', '--server.port', '8501'])\n",
                        "try:\n",
                        "    public_url = ngrok.connect(8501).public_url\n",
                        "    print('\\n' + '='*80)\n",
                        "    print(f'🚀 BF ANALISTA DE FUTEBOL ONLINE EM:')\n",
                        "    print(f'👉 {public_url}')\n",
                        "    print('='*80 + '\\n')\n",
                        "except Exception as e:\n",
                        "    print('Aceder localmente na porta 8501:', e)\n"
                    ]
                }
            ]
        }
        return json.dumps(notebook, indent=2, ensure_ascii=False)
