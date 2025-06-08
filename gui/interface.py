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

from encrypto.aes_cipher import cifrar_mensaje, descifrar_mensaje
from steganography.image_stego import ocultar_mensaje_imagen, extraer_mensaje_imagen
from steganography.audio_stego import ocultar_mensaje_audio, extraer_mensaje_audio
from steganography.text_stego import ocultar_cid_en_texto, extraer_cid_de_texto
from steganography.texto_CID_Clave import guardar_cid_en_texto


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

class IPFSDialog(QDialog):
    """Diálogo para mostrar los datos de IPFS generados."""
    
    def __init__(self, cid_ipfs, url_ipfs, ruta_salida, tipo_archivo, parent=None):
        super().__init__(parent)
        self.cid_ipfs = cid_ipfs
        self.url_ipfs = url_ipfs
        self.setWindowTitle("Archivo Subido a IPFS")
        self.setFixedSize(600, 320)
        self.setup_ui(ruta_salida, tipo_archivo)
    
    def setup_ui(self, ruta_salida, tipo_archivo):
        layout = QVBoxLayout()
        
        # Título de éxito
        titulo = QLabel("¡Archivo subido a IPFS con éxito!")
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
        
        # Etiqueta de CID
        label_cid = QLabel("CID de IPFS:")
        label_cid.setFont(QFont("Arial", 10, QFont.Bold))
        label_cid.setStyleSheet("margin-top: 15px;")
        layout.addWidget(label_cid)
        
        # Frame para CID y botón copiar
        frame_cid = QFrame()
        layout_cid = QHBoxLayout(frame_cid)
        
        self.entry_cid = QLineEdit(self.cid_ipfs)
        self.entry_cid.setReadOnly(True)
        self.entry_cid.setFont(QFont("Courier", 9))
        self.entry_cid.setStyleSheet("padding: 5px; background-color: #f0f0f0;")
        layout_cid.addWidget(self.entry_cid)
        
        btn_copiar_cid = QPushButton("📋 Copiar")
        btn_copiar_cid.clicked.connect(self.copiar_cid)
        btn_copiar_cid.setStyleSheet("""
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
        layout_cid.addWidget(btn_copiar_cid)
        
        layout.addWidget(frame_cid)
        
        # Etiqueta de URL
        label_url = QLabel("URL de acceso:")
        label_url.setFont(QFont("Arial", 10, QFont.Bold))
        label_url.setStyleSheet("margin-top: 10px;")
        layout.addWidget(label_url)
        
        # Frame para URL y botón copiar
        frame_url = QFrame()
        layout_url = QHBoxLayout(frame_url)
        
        self.entry_url = QLineEdit(self.url_ipfs)
        self.entry_url.setReadOnly(True)
        self.entry_url.setFont(QFont("Courier", 9))
        self.entry_url.setStyleSheet("padding: 5px; background-color: #f0f0f0;")
        layout_url.addWidget(self.entry_url)
        
        btn_copiar_url = QPushButton("📋 Copiar")
        btn_copiar_url.clicked.connect(self.copiar_url)
        btn_copiar_url.setStyleSheet("""
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
        layout_url.addWidget(btn_copiar_url)
        
        layout.addWidget(frame_url)
        
        # Información adicional
        info = QLabel("Puedes usar el CID o la URL para acceder a tu archivo desde cualquier gateway de IPFS.")
        info.setFont(QFont("Arial", 9))
        info.setAlignment(Qt.AlignCenter)
        info.setStyleSheet("color: #666; margin: 10px;")
        info.setWordWrap(True)
        layout.addWidget(info)
        
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
    
    def copiar_cid(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.cid_ipfs)
        QMessageBox.information(self, "Copiado", "CID de IPFS copiado al portapapeles")
    
    def copiar_url(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.url_ipfs)
        QMessageBox.information(self, "Copiado", "URL de IPFS copiada al portapapeles")


class EsteganografiaApp(QMainWindow):
    """Clase principal de la aplicación de esteganografía."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Esteganografía + AES-256 en Imágenes y Audio")
        self.setGeometry(100, 100, 800, 700)
        self.setup_ui()
        self.setup_styles()
    
    def setup_ui(self):
        """Crea la interfaz principal con pestañas."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Título principal
        titulo = QLabel("🔐 Esteganografía con Cifrado AES-256 🔐")
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
        
        # Sección de archivo con mensaje oculto
        grupo_archivo = QGroupBox("📁 Archivo con Mensaje Oculto")
        grupo_archivo.setFont(QFont("Arial", 10, QFont.Bold))
        layout_archivo = QVBoxLayout(grupo_archivo)
        
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
        layout_archivo.addLayout(layout_tipo)
        
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
        
        layout_archivo.addLayout(layout_buscar)
        layout.addWidget(grupo_archivo)
        
        # Sección de clave
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
        """Procesa la ocultación del mensaje."""
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
        
        try:
            if self.radio_imagen.isChecked():
                # Ocultar en imagen
                mensaje_cifrado = cifrar_mensaje(mensaje, clave)
                info_ipfs = ocultar_mensaje_imagen(ruta_entrada, mensaje_cifrado, ruta_salida)
                tipo_archivo = "imagen"
            else:
                # Ocultar en audio
                info_ipfs = ocultar_mensaje_audio(ruta_entrada, mensaje, ruta_salida, clave)
                tipo_archivo = "audio"
            
            # Mostrar diálogo con la clave
            clave_base64 = base64.b64encode(clave).decode('utf-8')
            dialog = ClaveDialog(clave_base64, ruta_salida, tipo_archivo, self)
           
            dialogIfps = IPFSDialog(
            cid_ipfs=info_ipfs['cid'],
            url_ipfs=info_ipfs['url'],
            ruta_salida="/tu/ruta/archivo.jpg",
            tipo_archivo="imagen")

            ruta = "cid_output.txt"
            cid_Clave = info_ipfs['cid'] + "  | Clave: " + clave_base64
            guardar_cid_en_texto(cid_Clave, ruta)

            #esteganografia con espacios/ tab
            ruta_salida_texto = "cid_text_stego"
            cid = info_ipfs['cid']
            ocultar_cid_en_texto(cid, ruta_salida_texto, usar_tab=True)


            
            dialog.exec_()
            dialogIfps.exec_()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo ocultar el mensaje:\n{str(e)}")
    
    def extraer_mensaje(self):
        """Procesa la extracción del mensaje."""
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




