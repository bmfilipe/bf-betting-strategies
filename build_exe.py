import subprocess
import sys

def build():
    """Build standalone executable using PyInstaller."""
    print("[BUILD] Instalando PyInstaller...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller", "-q"])

    print("[BUILD] A compilar executável BF_Analista_Futebol.exe...")
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name=BF_Analista_Futebol",
        "--add-data=config.py;.",
        "--add-data=models;models",
        "--add-data=services;services",
        "--add-data=ui;ui",
        "--add-data=app.py;.",
        "run.py"
    ]
    subprocess.check_call(cmd)
    print("\n✅ Compilação concluída com sucesso! Executável gerado na pasta 'dist/BF_Analista_Futebol.exe'")

if __name__ == "__main__":
    build()
