"""
Utilidades y componentes reutilizables para la interfaz gráfica.
Incluye diálogos, validadores, factory de componentes y estilos.
"""

import os
import base64
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QPushButton, QFrame, QApplication, 
                           QMessageBox, QTextEdit, QGroupBox, QRadioButton,
                           QButtonGroup, QFileDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from Crypto.Random import get_random_bytes


class ClaveDialog(QDialog):
    """Diálogo para mostrar la clave generada."""
    
    def __init__(self, clave_base64, ruta_salida, tipo_archivo, parent=None):
        super().__init__(parent)
        self.clave_base64 = clave_base64
        self.setWindowTitle("Clave AES-256 Generada")
        self.setFixedSize(550, 250)
        self.setup_ui(ruta_salida, tipo_archivo)
    
    def setup_ui(self, ruta_salida, tipo_archivo):
        layout = QVBoxLayout()
        
        # Título de éxito
        titulo = QLabel("¡Mensaje oculto con éxito!")
        titulo.setFont(QFont("Arial", 12, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("color: green; margin: 10px;")
        layout.addWidget(titulo)
        
        # Información del archivo guardado
        info_archivo = QLabel(f"{tipo_archivo.capitalize()} guardada en:\n{ruta_salida}")
        info_archivo.setWordWrap(True)
        info_archivo.setAlignment(Qt.AlignCenter)
        info_archivo.setStyleSheet("margin: 5px; color: #333;")
        layout.addWidget(info_archivo)
        
        # Etiqueta de clave
        label_clave = QLabel("Clave AES-256:")
        label_clave.setFont(QFont("Arial", 10, QFont.Bold))
        label_clave.setStyleSheet("margin-top: 15px;")
        layout.addWidget(label_clave)
        
        # Frame para clave y botón copiar
        frame_clave = QFrame()
        layout_clave = QHBoxLayout(frame_clave)
        
        self.entry_clave = QLineEdit(self.clave_base64)
        self.entry_clave.setReadOnly(True)
        self.entry_clave.setFont(QFont("Courier", 9))
        self.entry_clave.setStyleSheet("padding: 5px; background-color: #f0f0f0;")
        layout_clave.addWidget(self.entry_clave)
        
        btn_copiar = QPushButton("📋 Copiar")
        btn_copiar.clicked.connect(self.copiar_clave)
        btn_copiar.setStyleSheet(ESTILOS.get_boton_secundario())
        layout_clave.addWidget(btn_copiar)
        
        layout.addWidget(frame_clave)
        
        # Advertencia
        advertencia = QLabel("¡Guarda esta clave bien! La necesitarás para extraer el mensaje.")
        advertencia.setFont(QFont("Arial", 10, QFont.Bold))
        advertencia.setAlignment(Qt.AlignCenter)
        advertencia.setStyleSheet("color: red; margin: 15px;")
        layout.addWidget(advertencia)
        
        # Botón cerrar
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.clicked.connect(self.accept)
        btn_cerrar.setStyleSheet(ESTILOS.get_boton_principal())
        layout.addWidget(btn_cerrar, alignment=Qt.AlignCenter)
        
        self.setLayout(layout)
    
    def copiar_clave(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.clave_base64)
        MensajeUtil.informacion(self, "Copiado", "Clave copiada al portapapeles")


class EstilosApp:
    """Clase para manejar todos los estilos de la aplicación."""
    
    @staticmethod
    def get_boton_principal():
        return """
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """
    
    @staticmethod
    def get_boton_secundario():
        return """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """
    
    @staticmethod
    def get_boton_ocultar():
        return """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """
    
    @staticmethod
    def get_boton_extraer():
        return """
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """
    
    @staticmethod
    def get_input_texto():
        return """
            QLineEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                font-size: 11px;
            }
            QLineEdit:focus {
                border: 2px solid #2196F3;
            }
        """
    
    @staticmethod
    def get_textarea():
        return """
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                font-size: 11px;
            }
            QTextEdit:focus {
                border: 2px solid #2196F3;
            }
        """
    
    @staticmethod
    def get_textarea_resultado():
        return """
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                font-size: 11px;
                background-color: #f9f9f9;
            }
        """
    
    @staticmethod
    def get_tabs():
        return """
            QTabWidget::pane {
                border: 1px solid #c0c0c0;
                border-radius: 5px;
                margin-top: 5px;
            }
            QTabBar::tab {
                background: #f0f0f0;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: #2196F3;
                color: white;
            }
            QTabBar::tab:hover {
                background: #e3f2fd;
            }
        """


class MensajeUtil:
    """Utilidad para mostrar mensajes al usuario."""
    
    @staticmethod
    def error(parent, titulo, mensaje):
        """Muestra un diálogo de error."""
        QMessageBox.critical(parent, titulo, mensaje)
    
    @staticmethod
    def advertencia(parent, titulo, mensaje):
        """Muestra un diálogo de advertencia."""
        QMessageBox.warning(parent, titulo, mensaje)
    
    @staticmethod
    def informacion(parent, titulo, mensaje):
        """Muestra un diálogo de información."""
        QMessageBox.information(parent, titulo, mensaje)


class ValidadorArchivos:
    """Validador para archivos y entradas del usuario."""
    
    @staticmethod
    def archivo_existe(ruta_archivo):
        """Valida que el archivo exista."""
        return ruta_archivo and os.path.isfile(ruta_archivo)
    
    @staticmethod
    def validar_mensaje(mensaje):
        """Valida que el mensaje no esté vacío."""
        return mensaje and mensaje.strip()
    
    @staticmethod
    def validar_clave_base64(clave_b64):
        """Valida que la clave sea base64 válida."""
        try:
            if not clave_b64:
                return False
            base64.b64decode(clave_b64)
            return True
        except:
            return False


class CriptoUtil:
    """Utilidades para manejo de criptografía."""
    
    @staticmethod
    def generar_clave_aes():
        """Genera una clave AES-256 y la devuelve junto con su base64."""
        clave = get_random_bytes(32)
        clave_base64 = base64.b64encode(clave).decode('utf-8')
        return clave, clave_base64
    
    @staticmethod
    def decodificar_clave_base64(clave_b64):
        """Decodifica una clave de base64 a bytes."""
        return base64.b64decode(clave_b64)


class ComponenteFactory:
    """Factory para crear componentes de UI reutilizables."""
    
    @staticmethod
    def crear_grupo_mensaje():
        """Crea el grupo de entrada de mensaje."""
        grupo = QGroupBox("📝 Mensaje a Ocultar")
        grupo.setFont(QFont("Arial", 10, QFont.Bold))
        layout = QVBoxLayout(grupo)
        
        text_edit = QTextEdit()
        text_edit.setPlaceholderText("Escribe aquí el mensaje que deseas ocultar...")
        text_edit.setMaximumHeight(120)
        text_edit.setStyleSheet(ESTILOS.get_textarea())
        
        layout.addWidget(text_edit)
        return grupo, text_edit
    
    @staticmethod
    def crear_grupo_seleccion_medio():
        """Crea el grupo de selección de medio."""
        grupo = QGroupBox("🎯 Seleccionar Medio de Ocultación")
        grupo.setFont(QFont("Arial", 10, QFont.Bold))
        layout = QVBoxLayout(grupo)
        
        radio_imagen = QRadioButton("🖼️ Imagen (BMP, PNG, JPEG)")
        radio_audio = QRadioButton("🔊 Audio (WAV)")
        radio_imagen.setChecked(True)
        
        grupo_botones = QButtonGroup()
        grupo_botones.addButton(radio_imagen, 0)
        grupo_botones.addButton(radio_audio, 1)
        
        layout.addWidget(radio_imagen)
        layout.addWidget(radio_audio)
        
        return grupo, radio_imagen, radio_audio, grupo_botones
    
    @staticmethod
    def crear_entrada_archivo(titulo, placeholder, boton_texto="📂 Buscar"):
        """Crea un grupo de entrada de archivo."""
        grupo = QGroupBox(titulo)
        grupo.setFont(QFont("Arial", 10, QFont.Bold))
        layout = QVBoxLayout(grupo)
        
        layout_archivo = QHBoxLayout()
        
        entry = QLineEdit()
        entry.setPlaceholderText(placeholder)
        entry.setStyleSheet(ESTILOS.get_input_texto())
        
        boton = QPushButton(boton_texto)
        boton.setStyleSheet(ESTILOS.get_boton_principal())
        
        layout_archivo.addWidget(entry)
        layout_archivo.addWidget(boton)
        layout.addLayout(layout_archivo)
        
        return grupo, entry, boton
    
    @staticmethod
    def crear_grupo_resultado():
        """Crea el grupo de resultado."""
        grupo = QGroupBox("📄 Mensaje Extraído")
        grupo.setFont(QFont("Arial", 10, QFont.Bold))
        layout = QVBoxLayout(grupo)
        
        text_edit = QTextEdit()
        text_edit.setPlaceholderText("El mensaje descifrado aparecerá aquí...")
        text_edit.setMaximumHeight(150)
        text_edit.setStyleSheet(ESTILOS.get_textarea_resultado())
        
        layout.addWidget(text_edit)
        return grupo, text_edit


class ManejadorArchivos:
    """Manejador para operaciones con archivos."""
    
    FILTROS = {
        'imagenes': "Imágenes (*.bmp *.png *.jpg *.jpeg);;Todos los archivos (*.*)",
        'audio': "Archivos WAV (*.wav);;Todos los archivos (*.*)",
        'bmp_salida': "Imágenes BMP (*.bmp)",
        'wav_salida': "Archivos WAV (*.wav)"
    }
    
    @staticmethod
    def buscar_archivo_entrada(parent, es_imagen=True):
        """Abre diálogo para seleccionar archivo de entrada."""
        if es_imagen:
            archivo, _ = QFileDialog.getOpenFileName(
                parent, 
                "Seleccionar imagen",
                "",
                ManejadorArchivos.FILTROS['imagenes']
            )
        else:
            archivo, _ = QFileDialog.getOpenFileName(
                parent,
                "Seleccionar archivo WAV", 
                "",
                ManejadorArchivos.FILTROS['audio']
            )
        return archivo
    
    @staticmethod
    def buscar_archivo_salida(parent, es_imagen=True):
        """Abre diálogo para seleccionar dónde guardar."""
        if es_imagen:
            archivo, _ = QFileDialog.getSaveFileName(
                parent,
                "Guardar imagen como",
                "",
                ManejadorArchivos.FILTROS['bmp_salida']
            )
        else:
            archivo, _ = QFileDialog.getSaveFileName(
                parent,
                "Guardar audio como", 
                "",
                ManejadorArchivos.FILTROS['wav_salida']
            )
        return archivo


# Crear instancia global de estilos para fácil acceso
ESTILOS = EstilosApp()