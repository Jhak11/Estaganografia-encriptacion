"""
Punto de entrada principal del sistema
Canal de comunicación seguro con esteganografía (modo web)
"""

import sys
import os
from pathlib import Path

def main():
    """Ejecuta la aplicación web Flask"""
    try:
        print("🌐 Iniciando aplicación web...")
        print("📡 Servidor disponible en: http://localhost:5000")
        print("🔐 Canal de comunicación seguro con esteganografía")
        print("-" * 50)

        from app import app
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            threaded=True
        )
    except Exception as e:
        print(f"❌ Error al iniciar la aplicación: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()