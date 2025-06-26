"""
Módulo de interfaz gráfica principal usando PyQt5
Contiene la clase principal de la aplicación con dos módulos: Ocultar y Extraer mensajes.
"""

import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QTabWidget, QTextEdit, QLineEdit, 
                           QPushButton, QLabel, QFileDialog, QMessageBox, 
                           QGroupBox, QRadioButton, QButtonGroup, QDialog,
                           QGridLayout, QFrame, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor
from Crypto.Random import get_random_bytes

import base64
import os
import tempfile
import requests

from encrypto.aes_cipher import cifrar_mensaje, descifrar_mensaje
from steganography.image_stego import ocultar_mensaje_imagen, extraer_mensaje_imagen
from steganography.audio_stego import ocultar_mensaje_audio, extraer_mensaje_audio
from steganography.text_stego import ocultar_cid_en_texto, extraer_cid_de_texto
from Blockchain.mod_blockchain import store_text, cuentas, retrieve_text


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
        btn_copiar.setStyleSheet("""
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
        """)
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
        btn_cerrar.setStyleSheet("""
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
        """)
        layout.addWidget(btn_cerrar, alignment=Qt.AlignCenter)
        
        self.setLayout(layout)
    
    def copiar_clave(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.clave_base64)
        QMessageBox.information(self, "Copiado", "Clave copiada al portapapeles")

class EsteganografiaApp(QMainWindow):
    """Clase principal de la aplicación."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Canal de comunicación seguro")
        self.setGeometry(100, 100, 800, 700)
        self.direccion_contrato = None  # Variable para guardar la dirección del contrato
        self.setup_ui()
        self.setup_styles()
    
    def setup_ui(self):
        """Crea la interfaz principal con pestañas."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Título principal
        titulo = QLabel("🔐 Canal de comunicación seguro 🔐")
        titulo.setFont(QFont("Arial", 16, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("color: #2c3e50; margin: 10px; padding: 10px;")
        layout.addWidget(titulo)
        
        # Crear pestañas
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
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
        """)
        
        # Crear pestañas
        self.tab_ocultar = self.crear_tab_ocultar()
        self.tab_extraer = self.crear_tab_extraer()
        
        self.tabs.addTab(self.tab_ocultar, "🔐 Ocultar Mensaje")
        self.tabs.addTab(self.tab_extraer, "🔓 Extraer Mensaje")
        
        layout.addWidget(self.tabs)
    
    def crear_tab_ocultar(self):
        """Crea la pestaña para ocultar mensajes."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # Sección del mensaje
        grupo_mensaje = QGroupBox("📝 Mensaje a Ocultar")
        grupo_mensaje.setFont(QFont("Arial", 10, QFont.Bold))
        layout_mensaje = QVBoxLayout(grupo_mensaje)
        
        self.text_mensaje = QTextEdit()
        self.text_mensaje.setPlaceholderText("Escribe aquí el mensaje que deseas ocultar...")
        self.text_mensaje.setMaximumHeight(120)
        self.text_mensaje.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                font-size: 11px;
            }
            QTextEdit:focus {
                border: 2px solid #2196F3;
            }
        """)
        layout_mensaje.addWidget(self.text_mensaje)
        layout.addWidget(grupo_mensaje)
        
        # Sección de selección de medio
        grupo_medio = QGroupBox("🎯 Seleccionar Medio de Ocultación")
        grupo_medio.setFont(QFont("Arial", 10, QFont.Bold))
        layout_medio = QVBoxLayout(grupo_medio)
        
        # Botones de radio para seleccionar medio
        self.radio_imagen = QRadioButton("🖼️ Imagen (BMP, PNG, JPEG)")
        self.radio_audio = QRadioButton("🔊 Audio (WAV)")
        self.radio_imagen.setChecked(True)  # Por defecto imagen
        
        self.grupo_botones = QButtonGroup()
        self.grupo_botones.addButton(self.radio_imagen, 0)
        self.grupo_botones.addButton(self.radio_audio, 1)
        self.grupo_botones.buttonClicked.connect(self.cambiar_medio)
        
        layout_medio.addWidget(self.radio_imagen)
        layout_medio.addWidget(self.radio_audio)
        layout.addWidget(grupo_medio)
        
        # Sección de archivo de entrada
        grupo_entrada = QGroupBox("📁 Archivo de Entrada")
        grupo_entrada.setFont(QFont("Arial", 10, QFont.Bold))
        layout_entrada = QVBoxLayout(grupo_entrada)
        
        layout_archivo = QHBoxLayout()
        self.entry_archivo_entrada = QLineEdit()
        self.entry_archivo_entrada.setPlaceholderText("Selecciona el archivo donde ocultar el mensaje...")
        self.entry_archivo_entrada.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                font-size: 11px;
            }
            QLineEdit:focus {
                border: 2px solid #2196F3;
            }
        """)
        
        self.btn_buscar_entrada = QPushButton("📂 Buscar")
        self.btn_buscar_entrada.clicked.connect(self.buscar_archivo_entrada)
        layout_archivo.addWidget(self.entry_archivo_entrada)
        layout_archivo.addWidget(self.btn_buscar_entrada)
        
        layout_entrada.addLayout(layout_archivo)
        layout.addWidget(grupo_entrada)
        
        # Sección de archivo de salida
        grupo_salida = QGroupBox("💾 Archivo de Salida")
        grupo_salida.setFont(QFont("Arial", 10, QFont.Bold))
        layout_salida = QVBoxLayout(grupo_salida)
        
        layout_guardar = QHBoxLayout()
        self.entry_archivo_salida = QLineEdit()
        self.entry_archivo_salida.setPlaceholderText("Especifica dónde guardar el archivo con mensaje oculto...")
        self.entry_archivo_salida.setStyleSheet(self.entry_archivo_entrada.styleSheet())
        
        self.btn_buscar_salida = QPushButton("💾 Guardar como")
        self.btn_buscar_salida.clicked.connect(self.buscar_archivo_salida)
        layout_guardar.addWidget(self.entry_archivo_salida)
        layout_guardar.addWidget(self.btn_buscar_salida)
        
        layout_salida.addLayout(layout_guardar)
        layout.addWidget(grupo_salida)
        
        # Botón de procesar
        self.btn_ocultar = QPushButton("🔐 Ocultar Mensaje")
        self.btn_ocultar.setFont(QFont("Arial", 12, QFont.Bold))
        self.btn_ocultar.setMinimumHeight(45)
        self.btn_ocultar.clicked.connect(self.ocultar_mensaje)
        layout.addWidget(self.btn_ocultar)
        
        layout.addStretch()
        return widget
    
    def crear_tab_extraer(self):
        """Crea la pestaña para extraer mensajes."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # Sección de método de extracción
        grupo_metodo = QGroupBox("🔍 Método de Extracción")
        grupo_metodo.setFont(QFont("Arial", 10, QFont.Bold))
        layout_metodo = QVBoxLayout(grupo_metodo)
        
        self.radio_extraer_archivo = QRadioButton("📁 Desde Archivo Local")
        self.radio_extraer_blockchain = QRadioButton("⛓️ Desde Blockchain + IPFS")
        self.radio_extraer_archivo.setChecked(True)
        
        self.grupo_metodo_extraer = QButtonGroup()
        self.grupo_metodo_extraer.addButton(self.radio_extraer_archivo, 0)
        self.grupo_metodo_extraer.addButton(self.radio_extraer_blockchain, 1)
        self.grupo_metodo_extraer.buttonClicked.connect(self.cambiar_metodo_extraccion)
        
        layout_metodo.addWidget(self.radio_extraer_archivo)
        layout_metodo.addWidget(self.radio_extraer_blockchain)
        layout.addWidget(grupo_metodo)
        
        # ========== SECCIÓN ARCHIVO LOCAL ==========
        self.grupo_archivo_local = QGroupBox("📁 Extracción desde Archivo Local")
        self.grupo_archivo_local.setFont(QFont("Arial", 10, QFont.Bold))
        layout_archivo_local = QVBoxLayout(self.grupo_archivo_local)
        
        # Selección de tipo de archivo
        layout_tipo = QHBoxLayout()
        self.radio_extraer_imagen = QRadioButton("🖼️ Imagen")
        self.radio_extraer_audio = QRadioButton("🔊 Audio")
        self.radio_extraer_imagen.setChecked(True)
        
        self.grupo_extraer = QButtonGroup()
        self.grupo_extraer.addButton(self.radio_extraer_imagen, 0)
        self.grupo_extraer.addButton(self.radio_extraer_audio, 1)
        self.grupo_extraer.buttonClicked.connect(self.cambiar_medio_extraer)
        
        layout_tipo.addWidget(self.radio_extraer_imagen)
        layout_tipo.addWidget(self.radio_extraer_audio)
        layout_tipo.addStretch()
        layout_archivo_local.addLayout(layout_tipo)
        
        # Selección de archivo
        layout_buscar = QHBoxLayout()
        self.entry_archivo_extraer = QLineEdit()
        self.entry_archivo_extraer.setPlaceholderText("Selecciona el archivo con mensaje oculto...")
        self.entry_archivo_extraer.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                font-size: 11px;
            }
            QLineEdit:focus {
                border: 2px solid #2196F3;
            }
        """)
        
        self.btn_buscar_extraer = QPushButton("📂 Buscar")
        self.btn_buscar_extraer.clicked.connect(self.buscar_archivo_extraer)
        layout_buscar.addWidget(self.entry_archivo_extraer)
        layout_buscar.addWidget(self.btn_buscar_extraer)
        
        layout_archivo_local.addLayout(layout_buscar)
        layout.addWidget(self.grupo_archivo_local)
        
        # ========== SECCIÓN BLOCKCHAIN ==========
        self.grupo_blockchain = QGroupBox("⛓️ Extracción desde Blockchain + IPFS")
        self.grupo_blockchain.setFont(QFont("Arial", 10, QFont.Bold))
        self.grupo_blockchain.setVisible(False)  # Oculto inicialmente
        layout_blockchain = QVBoxLayout(self.grupo_blockchain)
        
        # Campo para dirección del contrato
        layout_contrato = QVBoxLayout()
        label_contrato = QLabel("📜 Dirección del Contrato:")
        label_contrato.setFont(QFont("Arial", 9, QFont.Bold))
        
        self.entry_direccion_contrato = QLineEdit()
        self.entry_direccion_contrato.setPlaceholderText("Ingresa la dirección del contrato blockchain...")
        self.entry_direccion_contrato.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                font-size: 11px;
                font-family: 'Courier New';
            }
            QLineEdit:focus {
                border: 2px solid #2196F3;
            }
        """)
        
        # Botón para usar la última dirección generada
        self.btn_usar_ultima_direccion = QPushButton("📋 Usar Última Dirección Generada")
        self.btn_usar_ultima_direccion.clicked.connect(self.usar_ultima_direccion_contrato)
        self.btn_usar_ultima_direccion.setStyleSheet("""
            QPushButton {
                background-color: #9C27B0;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #7B1FA2;
            }
        """)
        
        layout_contrato.addWidget(label_contrato)
        layout_contrato.addWidget(self.entry_direccion_contrato)
        layout_contrato.addWidget(self.btn_usar_ultima_direccion)
        layout_blockchain.addLayout(layout_contrato)
        
        # Área de información del proceso
        self.text_info_proceso = QTextEdit()
        self.text_info_proceso.setPlaceholderText("Información del proceso de recuperación aparecerá aquí...")
        self.text_info_proceso.setMaximumHeight(100)
        self.text_info_proceso.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                font-size: 10px;
                background-color: #f0f8ff;
                font-family: 'Courier New';
            }
        """)
        self.text_info_proceso.setReadOnly(True)
        layout_blockchain.addWidget(self.text_info_proceso)
        
        layout.addWidget(self.grupo_blockchain)
        
        # Sección de clave (común para ambos métodos)
        grupo_clave = QGroupBox("🔑 Clave AES-256")
        grupo_clave.setFont(QFont("Arial", 10, QFont.Bold))
        layout_clave = QVBoxLayout(grupo_clave)
        
        self.entry_clave = QLineEdit()
        self.entry_clave.setPlaceholderText("Ingresa la clave AES-256 en formato base64...")
        self.entry_clave.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                font-size: 11px;
                font-family: 'Courier New';
            }
            QLineEdit:focus {
                border: 2px solid #2196F3;
            }
        """)
        layout_clave.addWidget(self.entry_clave)
        layout.addWidget(grupo_clave)
        
        # Botón de extraer
        self.btn_extraer = QPushButton("🔓 Extraer y Descifrar Mensaje")
        self.btn_extraer.setFont(QFont("Arial", 12, QFont.Bold))
        self.btn_extraer.setMinimumHeight(45)
        self.btn_extraer.clicked.connect(self.extraer_mensaje)
        layout.addWidget(self.btn_extraer)
        
        # Resultado
        grupo_resultado = QGroupBox("📄 Mensaje Extraído")
        grupo_resultado.setFont(QFont("Arial", 10, QFont.Bold))
        layout_resultado = QVBoxLayout(grupo_resultado)
        
        self.text_resultado = QTextEdit()
        self.text_resultado.setPlaceholderText("El mensaje descifrado aparecerá aquí...")
        self.text_resultado.setMaximumHeight(150)
        self.text_resultado.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                font-size: 11px;
                background-color: #f9f9f9;
            }
        """)
        layout_resultado.addWidget(self.text_resultado)
        layout.addWidget(grupo_resultado)
        
        layout.addStretch()
        return widget
    
    def setup_styles(self):
        """Configura los estilos generales de la aplicación."""
        button_style = """
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """
        
        # Aplicar estilos a botones específicos
        self.btn_ocultar.setStyleSheet("""
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
        """)
        
        self.btn_extraer.setStyleSheet("""
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
        """)
        
        # Aplicar estilos a botones de búsqueda
        for btn in [self.btn_buscar_entrada, self.btn_buscar_salida, self.btn_buscar_extraer]:
            btn.setStyleSheet(button_style)
    
    def cambiar_metodo_extraccion(self, button):
        """Maneja el cambio entre métodos de extracción."""
        if button == self.radio_extraer_archivo:
            self.grupo_archivo_local.setVisible(True)
            self.grupo_blockchain.setVisible(False)
            self.btn_extraer.setText("🔓 Extraer y Descifrar Mensaje")
        else:
            self.grupo_archivo_local.setVisible(False)
            self.grupo_blockchain.setVisible(True)
            self.btn_extraer.setText("⛓️ Recuperar desde Blockchain + IPFS")
    
    def usar_ultima_direccion_contrato(self):
        """Usa la última dirección de contrato generada."""
        if self.direccion_contrato:
            self.entry_direccion_contrato.setText(self.direccion_contrato)
            QMessageBox.information(self, "Información", "Dirección del contrato cargada correctamente.")
        else:
            QMessageBox.warning(self, "Advertencia", "No hay ninguna dirección de contrato disponible.\nPrimero debes ocultar un mensaje.")
    
    def cambiar_medio(self, button):
        """Maneja el cambio de medio de ocultación."""
        if button == self.radio_imagen:
            self.entry_archivo_entrada.setPlaceholderText("Selecciona una imagen (BMP, PNG, JPEG)...")
        else:
            self.entry_archivo_entrada.setPlaceholderText("Selecciona un archivo de audio WAV...")
    
    def cambiar_medio_extraer(self, button):
        """Maneja el cambio de medio para extracción."""
        if button == self.radio_extraer_imagen:
            self.entry_archivo_extraer.setPlaceholderText("Selecciona una imagen con mensaje oculto...")
        else:
            self.entry_archivo_extraer.setPlaceholderText("Selecciona un archivo WAV con mensaje oculto...")
    
    def buscar_archivo_entrada(self):
        """Abre diálogo para seleccionar archivo de entrada."""
        if self.radio_imagen.isChecked():
            archivo, _ = QFileDialog.getOpenFileName(
                self, 
                "Seleccionar imagen",
                "",
                "Imágenes (*.bmp *.png *.jpg *.jpeg);;Todos los archivos (*.*)"
            )
        else:
            archivo, _ = QFileDialog.getOpenFileName(
                self,
                "Seleccionar archivo WAV", 
                "",
                "Archivos WAV (*.wav);;Todos los archivos (*.*)"
            )
        
        if archivo:
            self.entry_archivo_entrada.setText(archivo)
    
    def buscar_archivo_salida(self):
        """Abre diálogo para seleccionar dónde guardar."""
        if self.radio_imagen.isChecked():
            archivo, _ = QFileDialog.getSaveFileName(
                self,
                "Guardar imagen como",
                "",
                "Imágenes BMP (*.bmp)"
            )
        else:
            archivo, _ = QFileDialog.getSaveFileName(
                self,
                "Guardar audio como", 
                "",
                "Archivos WAV (*.wav)"
            )
        
        if archivo:
            self.entry_archivo_salida.setText(archivo)
    
    def buscar_archivo_extraer(self):
        """Abre diálogo para seleccionar archivo a extraer."""
        if self.radio_extraer_imagen.isChecked():
            archivo, _ = QFileDialog.getOpenFileName(
                self,
                "Seleccionar imagen con mensaje oculto",
                "",
                "Imágenes (*.bmp *.png *.jpg *.jpeg);;Todos los archivos (*.*)"
            )
        else:
            archivo, _ = QFileDialog.getOpenFileName(
                self,
                "Seleccionar archivo WAV con mensaje oculto",
                "",
                "Archivos WAV (*.wav);;Todos los archivos (*.*)"
            )
        
        if archivo:
            self.entry_archivo_extraer.setText(archivo)

    def ocultar_mensaje(self):
        mensaje = self.text_mensaje.toPlainText().strip()
        ruta_entrada = self.entry_archivo_entrada.text().strip()
        ruta_salida = self.entry_archivo_salida.text().strip()
        
        # Validaciones
        if not mensaje:
            QMessageBox.warning(self, "Advertencia", "Debes escribir un mensaje para ocultar.")
            return
        if not ruta_entrada or not os.path.isfile(ruta_entrada):
            QMessageBox.critical(self, "Error", "Selecciona un archivo de entrada válido.")
            return
        if not ruta_salida:
            QMessageBox.warning(self, "Advertencia", "Especifica dónde guardar el archivo.")
            return
        
        # Generar clave AES
        clave = get_random_bytes(32)
        clave_base64 = base64.b64encode(clave).decode('utf-8')

        info_ipfs = None
        try:
            if self.radio_imagen.isChecked():
                mensaje_cifrado = cifrar_mensaje(mensaje, clave)
                info_ipfs = ocultar_mensaje_imagen(ruta_entrada, mensaje_cifrado, ruta_salida)
                tipo_archivo = "imagen"
            else:
                mensaje_cifrado = cifrar_mensaje(mensaje, clave)
                info_ipfs = ocultar_mensaje_audio(ruta_entrada, mensaje_cifrado, ruta_salida)
                tipo_archivo = "audio"
            
            if not info_ipfs or 'cid' not in info_ipfs:
                QMessageBox.critical(self, "Error", "Error al subir a IPFS. No se generó CID.")
                return
            
            # CID oculto con esteganografía en texto
            texto_B = ocultar_cid_en_texto(info_ipfs['cid'], usar_tab=True)

            # Obtener cuenta
            cuenta = cuentas()
            if not cuenta or len(cuenta) < 2:
                raise Exception("No se pudo obtener la cuenta para firmar el contrato.")
            
            direccion_de_contrato = store_text(texto_B, cuenta[1])
            self.direccion_contrato = direccion_de_contrato

            # Mostrar clave y datos
            dialog = ClaveDialog(clave_base64, ruta_salida, tipo_archivo, self)
            dialog.exec_()

            QMessageBox.information(
                self,
                "Éxito - Contrato Creado",
                f"Mensaje oculto exitosamente.\n\n"
                f"📜 Dirección del contrato: {direccion_de_contrato}\n"
                f"🔑 Clave AES generada y mostrada en el diálogo.\n\n"
                f"Guarda tanto la dirección del contrato como la clave para recuperar el mensaje."
            )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo ocultar el mensaje:\n{str(e)}")

    
    def extraer_mensaje(self):
        """Procesa la extracción del mensaje."""
        if self.radio_extraer_archivo.isChecked():
            self._extraer_desde_archivo()
        else:
            self._extraer_desde_blockchain()
    
    def _extraer_desde_archivo(self):
        """Extrae mensaje desde archivo local."""
        ruta_archivo = self.entry_archivo_extraer.text().strip()
        clave_b64 = self.entry_clave.text().strip()
        
        # Validaciones
        if not ruta_archivo or not os.path.isfile(ruta_archivo):
            QMessageBox.critical(self, "Error", "Selecciona un archivo válido.")
            return
        
        if not clave_b64:
            QMessageBox.warning(self, "Advertencia", "Debes ingresar la clave AES-256.")
            return
        
        try:
            clave = base64.b64decode(clave_b64)
            
            if self.radio_extraer_imagen.isChecked():
                # Extraer de imagen
                mensaje_cifrado = extraer_mensaje_imagen(ruta_archivo)
                mensaje_descifrado = descifrar_mensaje(mensaje_cifrado, clave)
            else:
                # Extraer de audio
                mensaje_descifrado = extraer_mensaje_audio(ruta_archivo, clave)
            
            self.text_resultado.setText(mensaje_descifrado)
            QMessageBox.information(self, "Éxito", "Mensaje extraído y descifrado correctamente.")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo extraer o descifrar el mensaje:\n{str(e)}")
    
    def _extraer_desde_blockchain(self):
        """Extrae mensaje desde blockchain e IPFS."""
        direccion_contrato = self.entry_direccion_contrato.text().strip()
        clave_b64 = self.entry_clave.text().strip()
    
        # Validaciones
        if not direccion_contrato:
            QMessageBox.warning(self, "Advertencia", "Debes ingresar la dirección del contrato.")
            return
    
        if not clave_b64:
            QMessageBox.warning(self, "Advertencia", "Debes ingresar la clave AES-256.")
            return
    
        try:
            clave = base64.b64decode(clave_b64)
        
            # Paso 1: Recuperar texto del contrato
            self.text_info_proceso.append("🔍 Recuperando texto del contrato blockchain...")
            self.text_info_proceso.repaint()
        
            texto_recuperado = retrieve_text(direccion_contrato)
            if not texto_recuperado:
                raise Exception("No se pudo recuperar el texto del contrato")
        
            self.text_info_proceso.append(f"✅ Texto recuperado del contrato: {len(texto_recuperado)} caracteres")
        
            # Paso 2: Extraer CID del texto esteganografiado
            self.text_info_proceso.append("🔍 Extrayendo CID del texto esteganografiado...")
            self.text_info_proceso.repaint()
        
            # Crear archivo temporal con el texto
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
                temp_file.write(texto_recuperado)
                temp_file_path = temp_file.name
        
            try:
                cid_extraido = extraer_cid_de_texto(temp_file_path, usar_tab=True)
                if not cid_extraido:
                    raise Exception("No se pudo extraer el CID del texto")

                self.text_info_proceso.append(f"✅ CID extraído: {cid_extraido}")

                # Paso 3: Descargar archivo de IPFS
                self.text_info_proceso.append("📥 Descargando archivo desde IPFS...")
                self.text_info_proceso.repaint()

                # Crear archivo temporal para la descarga
                with tempfile.NamedTemporaryFile(delete=False) as temp_download:
                    ruta_archivo_temp = temp_download.name

                # Importar y usar el manejador IPFS
                from ipfs.manejador_ipfs import crear_manejador_ipfs
                manejador_ipfs = crear_manejador_ipfs()
                
                # Usar la función descargar_archivo del manejador
                exito_descarga, mensaje_descarga = manejador_ipfs.descargar_archivo(cid_extraido, ruta_archivo_temp)
                
                if not exito_descarga:
                    raise Exception(f"Error al descargar archivo desde IPFS: {mensaje_descarga}")
                
                self.text_info_proceso.append(f"✅ {mensaje_descarga}")

                # Leer el archivo descargado para determinar su tipo
                with open(ruta_archivo_temp, 'rb') as f:
                    file_content = f.read()

                # Verificar los primeros bytes para determinar el tipo
                primeros_bytes = file_content[:20]

                # Detectar tipo de archivo
                es_imagen = False
                es_audio = False

                # Firmas de archivos de imagen
                if (primeros_bytes.startswith(b'\xff\xd8\xff') or  # JPEG
                    primeros_bytes.startswith(b'\x89PNG') or       # PNG
                    primeros_bytes.startswith(b'GIF8') or          # GIF
                    primeros_bytes.startswith(b'BM')):             # BMP
                    es_imagen = True

                # Firmas de archivos de audio
                elif (primeros_bytes.startswith(b'RIFF') or        # WAV
                    primeros_bytes.startswith(b'ID3') or         # MP3
                    primeros_bytes.startswith(b'\xff\xfb') or    # MP3
                    primeros_bytes.startswith(b'OggS') or        # OGG
                    primeros_bytes.startswith(b'fLaC')):         # FLAC
                    es_audio = True

                if not es_imagen and not es_audio:
                    raise Exception("No se pudo determinar si el archivo es una imagen o audio")

                if es_imagen:
                    self.text_info_proceso.append("📸 Archivo detectado como imagen")
                    
                    # Crear nuevo archivo temporal con extensión apropiada para imagen
                    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_image:
                        temp_image.write(file_content)
                        ruta_imagen_temp = temp_image.name

                    self.text_info_proceso.append(f"✅ Imagen procesada: {len(file_content)} bytes")

                    # Paso 4: Extraer mensaje de la imagen
                    self.text_info_proceso.append("🔓 Extrayendo y descifrando mensaje de la imagen...")
                    self.text_info_proceso.repaint()

                    # Extraer mensaje cifrado de la imagen
                    mensaje_cifrado = extraer_mensaje_imagen(ruta_imagen_temp)

                    # Descifrar mensaje
                    mensaje_descifrado = descifrar_mensaje(mensaje_cifrado, clave)

                elif es_audio:
                    self.text_info_proceso.append("🎵 Archivo detectado como audio")

                    # Verificar si es WAV
                    if not primeros_bytes.startswith(b'RIFF'):
                        raise Exception("❌ Solo se aceptan archivos de audio en formato WAV.")

                    # Crear nuevo archivo temporal con extensión apropiada para audio
                    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
                        temp_audio.write(file_content)
                        ruta_audio_temp = temp_audio.name

                    self.text_info_proceso.append(f"✅ Audio WAV procesado: {len(file_content)} bytes")

                    # Paso 4: Extraer mensaje del audio
                    self.text_info_proceso.append("🔓 Extrayendo y descifrando mensaje del audio WAV...")
                    self.text_info_proceso.repaint()

                    try:
                        mensaje_descifrado = extraer_mensaje_audio(ruta_audio_temp, clave)
                    except Exception as e:
                        raise Exception(f"❌ Error al extraer el mensaje del audio: {str(e)}")

                # Mostrar resultado
                self.text_resultado.setText(mensaje_descifrado)
                self.text_info_proceso.append("✅ ¡Proceso completado exitosamente!")

                # Limpiar archivos temporales
                try:
                    os.unlink(temp_file_path)
                    os.unlink(ruta_archivo_temp)
                    if es_imagen:
                        os.unlink(ruta_imagen_temp)
                    elif es_audio:
                        os.unlink(ruta_audio_temp)
                except:
                    pass

                tipo_archivo = "imagen" if es_imagen else "audio"
                QMessageBox.information(
                    self, 
                    "Éxito", 
                    f"Mensaje recuperado exitosamente desde blockchain e IPFS.\n\n"
                    f"El proceso completo fue:\n"
                    f"1. ✅ Recuperación del texto del contrato\n"
                    f"2. ✅ Extracción del CID esteganografiado\n"
                    f"3. ✅ Descarga de {tipo_archivo} desde IPFS\n"
                    f"4. ✅ Extracción y descifrado del mensaje"
                )
            
            finally:
                # Limpiar archivo temporal del texto si existe
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
                
        except Exception as e:
            self.text_info_proceso.append(f"❌ Error: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error durante el proceso: {str(e)}")
        
            # Limpiar archivos temporales en caso de error
            try:
                if 'temp_file_path' in locals():
                    os.unlink(temp_file_path)
                if 'ruta_archivo_temp' in locals():
                    os.unlink(ruta_archivo_temp)
                if 'ruta_audio_original' in locals():
                    os.unlink(ruta_audio_temp)
            except:
                pass
            
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Error de Red", f"Error al descargar desde IPFS:\n{str(e)}")
            self.text_info_proceso.append(f"❌ Error de descarga: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo recuperar el mensaje desde blockchain:\n{str(e)}")
            self.text_info_proceso.append(f"❌ Error: {str(e)}")


def main():
    """Función principal para ejecutar la aplicación."""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Estilo moderno
    
    # Configurar paleta de colores
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(245, 245, 245))
    palette.setColor(QPalette.WindowText, QColor(50, 50, 50))
    app.setPalette(palette)
    
    ventana = EsteganografiaApp()
    ventana.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
