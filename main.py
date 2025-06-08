"""
Punto de entrada principal para la aplicación de Esteganografía con PyQt5.
Ejecuta la interfaz gráfica principal.
"""

import sys
import os
from gui.interface import main
# Añadir el directorio del proyecto al path para imports relativos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
if __name__ == "__main__":
    main()