import subprocess
import sys
import os
import webbrowser
import threading
import time

def is_cloud_environment() -> bool:
    """Detect if running inside Streamlit Community Cloud or remote cloud container."""
    return bool(
        os.environ.get("STREAMLIT_SERVER_PORT") or
        os.environ.get("SERVER_PORT") or
        os.environ.get("IS_STREAMLIT_CLOUD") or
        "/mount/src" in os.getcwd().replace("\\", "/")
    )

def check_and_install_dependencies():
    """Ensure all required packages are installed (local environment only)."""
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
    try:
        print("[SYSTEM] Verificando dependências locais...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", *packages, "-q"])
    except Exception:
        pass

def open_browser(url: str):
    """Open default web browser after a short delay."""
    time.sleep(2.0)
    try:
        webbrowser.open(url)
    except Exception:
        pass

def setup_ngrok_tunnel(port: int, domain: str, ngrok_token: str):
    """Establish Ngrok tunnel in background after Streamlit server is active (local only)."""
    if is_cloud_environment():
        return

    time.sleep(3.0)
    token_file = os.path.join(os.path.dirname(__file__), ".ngrok_token")
    if not ngrok_token and os.path.exists(token_file):
        try:
            with open(token_file, "r", encoding="utf-8") as f:
                ngrok_token = f.read().strip()
        except Exception:
            pass

    if not ngrok_token:
        return

    try:
        from pyngrok import ngrok
        ngrok.set_auth_token(ngrok_token)
        target_addr = f"127.0.0.1:{port}"
        try:
            public_url = ngrok.connect(target_addr, domain=domain).public_url
        except Exception:
            public_url = ngrok.connect(target_addr).public_url

        print("\n" + "=" * 80)
        print(f" 🚀 ACESSO REMOTO (Ngrok Tunnel): {public_url}")
        print("=" * 80 + "\n")
    except Exception:
        pass

def start_application():
    """Start Streamlit server and optional Ngrok tunnel with auto browser launch."""
    # If running on Streamlit Cloud, run app directly without spawning sub-processes
    if is_cloud_environment():
        app_path = os.path.join(ROOT_DIR, "app.py")
        with open(app_path, "r", encoding="utf-8") as f:
            code = compile(f.read(), app_path, "exec")
        exec_scope = {
            "__name__": "__main__",
            "__file__": app_path,
            "__builtins__": __builtins__
        }
        exec(code, exec_scope)
        return



    check_and_install_dependencies()

    port = 8501
    local_url = f"http://localhost:{port}"
    ngrok_token = os.environ.get("NGROK_AUTHTOKEN", "").strip()
    ngrok_domain = os.environ.get("NGROK_DOMAIN", "blot-sandbag-wildcat.ngrok-free.dev").strip()

    print("\n" + "=" * 80)
    print(" ⚽ BF ANALISTA DE FUTEBOL - APLICAÇÃO EM EXECUÇÃO")
    print("=" * 80)
    print(f" 🌐 ACESSO LOCALHOST (Navegador): {local_url}")
    print("=" * 80 + "\n")

    threading.Thread(target=open_browser, args=(local_url,), daemon=True).start()
    threading.Thread(target=setup_ngrok_tunnel, args=(port, ngrok_domain, ngrok_token), daemon=True).start()

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
        sys.exit(0)
