import os
import subprocess
import sys

def build():
    """Script automatizado para generar el archivo .exe de PDF Master Pro."""
    print("--- Iniciando proceso de empaquetado ---")
    
    # 1. Asegurar dependencias necesarias para el build
    print("1. Verificando dependencias necesarias...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller", "-r", "requirements.txt"])
    except subprocess.CalledProcessError as e:
        print(f"Error al instalar dependencias: {e}")
        return

    # 2. Ejecutar PyInstaller con el archivo .spec
    print("\n2. Generando archivo ejecutable (.exe)...")
    try:
        # Usamos el archivo .spec que ya tiene toda la configuración técnica
        subprocess.check_call(["pyinstaller", "--clean", "PDFProcessor.spec"])
        print("\n" + "="*50)
        print("¡ÉXITO! El archivo ejecutable ha sido generado.")
        print("Puedes encontrarlo en: dist/PDFProcessor.exe")
        print("="*50)
        print("\nRecuerda: Este .exe es portable y puedes compartirlo.")
        print("Nota: Word debe estar instalado en el PC destino para Word->PDF.")
    except subprocess.CalledProcessError as e:
        print(f"Error durante el empaquetado: {e}")
    except FileNotFoundError:
        print("Error: PyInstaller no encontrado. Asegúrate de que esté en tu PATH.")

if __name__ == "__main__":
    build()
