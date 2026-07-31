import subprocess
import sys
import os
import webbrowser
import threading
import time

def check_and_install_dependencies():
    """Ensure all required packages are installed."""
    packages = [
        "streamlit",
        "pandas",
        "numpy",
        "scipy",
        "google-genai",
        "fpdf2",
        "pyngrok",
        "plotly",
        "tabulate"
    ]
    print("[SYSTEM] Verificando e instalando dependências...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", *packages, "-q"])
    print("[SYSTEM] Dependências verificadas com sucesso!\n")

def open_browser(url: str):
    """Open default web browser after a short delay."""
    time.sleep(2.0)
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"[AVISO] Não foi possível abrir o navegador automaticamente: {e}")

def setup_ngrok_tunnel(port: int, domain: str, ngrok_token: str):
    """Establish Ngrok tunnel in background after Streamlit server is active."""
    time.sleep(3.0)  # Wait for Streamlit server to bind to port 8501
    
    # Check local .ngrok_token file if exists
    token_file = os.path.join(os.path.dirname(__file__), ".ngrok_token")
    if not ngrok_token and os.path.exists(token_file):
        try:
            with open(token_file, "r", encoding="utf-8") as f:
                ngrok_token = f.read().strip()
        except Exception:
            pass

    if not ngrok_token:
        print("\n" + "⚠️ " * 30)
        print(" [AVISO NGROK] O túnel externo está offline porque é necessária autenticação Ngrok.")
        print(" Para colocar o endereço https://blot-sandbag-wildcat.ngrok-free.dev/ online:")
        print(" 1. Cria uma conta gratuita em: https://dashboard.ngrok.com/signup")
        print(" 2. Obtém a tua chave em: https://dashboard.ngrok.com/get-started/your-authtoken")
        print(" 3. Copia a chave para a 'Área de Administrador' na aplicação ou cria um ficheiro '.ngrok_token'.")
        print("⚠️ " * 30 + "\n")
        return

    try:
        from pyngrok import ngrok
        ngrok.set_auth_token(ngrok_token)

        # Target explicit IPv4 loopback 127.0.0.1:8501 to avoid IPv6 [::1] connection refused warnings
        target_addr = f"127.0.0.1:{port}"
        
        try:
            public_url = ngrok.connect(target_addr, domain=domain).public_url
        except Exception:
            public_url = ngrok.connect(target_addr).public_url

        print("\n" + "=" * 80)
        print(f" 🚀 ACESSO REMOTO (Ngrok Tunnel): {public_url}")
        print("=" * 80 + "\n")

    except Exception as e:
        print(f"\n[AVISO NGROK] Falha ao iniciar túnel Ngrok: {e}\n")

def start_application():
    """Start Streamlit server and optional Ngrok tunnel with auto browser launch."""
    check_and_install_dependencies()

    port = 8501
    local_url = f"http://localhost:{port}"

    ngrok_token = os.environ.get("NGROK_AUTHTOKEN", "").strip()
    ngrok_domain = os.environ.get("NGROK_DOMAIN", "blot-sandbag-wildcat.ngrok-free.dev").strip()

    # Terminal Access Banner
    print("\n" + "=" * 80)
    print(" ⚽ BF ANALISTA DE FUTEBOL - APLICAÇÃO EM EXECUÇÃO")
    print("=" * 80)
    print(f" 🌐 ACESSO LOCALHOST (Navegador): {local_url}")
    print("=" * 80 + "\n")

    # Start background thread to open default browser
    threading.Thread(target=open_browser, args=(local_url,), daemon=True).start()

    # Start background thread for Ngrok tunnel (waits for Streamlit to start first)
    threading.Thread(target=setup_ngrok_tunnel, args=(port, ngrok_domain, ngrok_token), daemon=True).start()

    print(f"[SYSTEM] A iniciar servidor Streamlit na porta {port}...")
    cmd = [
        sys.executable,
        "-m", "streamlit", "run", "app.py",
        f"--server.port={port}",
        "--server.address=127.0.0.1",
        "--server.headless=true"
    ]
    subprocess.run(cmd)

if __name__ == "__main__":
    try:
        start_application()
    except KeyboardInterrupt:
        print("\n[SYSTEM] Aplicação BF Analista de Futebol encerrada com sucesso pelo utilizador.")
        sys.exit(0)
