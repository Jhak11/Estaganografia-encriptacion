
"""
Lógica de esteganografía para aplicación Flask
Contiene las funciones principales para ocultar y extraer mensajes.
"""

import base64
import os
import tempfile
import requests
from Crypto.Random import get_random_bytes

from encrypto.aes_cipher import cifrar_mensaje, descifrar_mensaje
from steganography.image_stego import ocultar_mensaje_imagen, extraer_mensaje_imagen
from steganography.audio_stego import ocultar_mensaje_audio, extraer_mensaje_audio
from steganography.text_stego import ocultar_cid_en_texto, extraer_cid_de_texto
from Blockchain.mod_blockchain import store_text, cuentas, retrieve_text


class EsteganografiaService:
    """Servicio de esteganografía para operaciones de ocultación y extracción."""
    
    def __init__(self):
        self.direccion_contrato = None
    
    def ocultar_mensaje(self, mensaje, ruta_entrada, ruta_salida, tipo_medio='imagen'):
        """
        Oculta un mensaje en un archivo de imagen o audio.
        
        Args:
            mensaje (str): Mensaje a ocultar
            ruta_entrada (str): Ruta del archivo original
            ruta_salida (str): Ruta donde guardar el archivo con mensaje oculto
            tipo_medio (str): 'imagen' o 'audio'
        
        Returns:
            dict: Resultado de la operación con clave, dirección del contrato, etc.
        """
        # Validaciones
        if not mensaje:
            raise ValueError("El mensaje no puede estar vacío")
        
        if not ruta_entrada or not os.path.isfile(ruta_entrada):
            raise ValueError("El archivo de entrada no existe")
        
        if not ruta_salida:
            raise ValueError("Debe especificar una ruta de salida")
        
        # Generar clave AES
        clave = get_random_bytes(32)
        clave_base64 = base64.b64encode(clave).decode('utf-8')
        
        try:
            # Cifrar mensaje
            mensaje_cifrado = cifrar_mensaje(mensaje, clave)
            
            # Ocultar en el medio correspondiente
            if tipo_medio == 'imagen':
                info_ipfs = ocultar_mensaje_imagen(ruta_entrada, mensaje_cifrado, ruta_salida)
            elif tipo_medio == 'audio':
                info_ipfs = ocultar_mensaje_audio(ruta_entrada, mensaje_cifrado, ruta_salida)
            else:
                raise ValueError("Tipo de medio no soportado. Use 'imagen' o 'audio'")
            
            if not info_ipfs or 'cid' not in info_ipfs:
                raise Exception("Error al subir a IPFS. No se generó CID.")
            
            # Ocultar CID en texto usando esteganografía
            texto_B = ocultar_cid_en_texto(info_ipfs['cid'], usar_tab=True)
            
            # Obtener cuenta para blockchain
            cuenta = cuentas()
            if not cuenta or len(cuenta) < 2:
                raise Exception("No se pudo obtener la cuenta para firmar el contrato.")
            
            # Almacenar en blockchain
            direccion_de_contrato = store_text(texto_B, cuenta[1])
            self.direccion_contrato = direccion_de_contrato
            
            return {
                'exito': True,
                'clave': clave_base64,
                'direccion_contrato': direccion_de_contrato,
                'ruta_salida': ruta_salida,
                'tipo_archivo': tipo_medio,
                'cid_ipfs': info_ipfs['cid']
            }
            
        except Exception as e:
            raise Exception(f"Error al ocultar el mensaje: {str(e)}")
    
    def extraer_mensaje_archivo(self, ruta_archivo, clave_b64, tipo_medio='imagen'):
        """
        Extrae un mensaje desde un archivo local.
        
        Args:
            ruta_archivo (str): Ruta del archivo con mensaje oculto
            clave_b64 (str): Clave AES-256 en base64
            tipo_medio (str): 'imagen' o 'audio'
        
        Returns:
            dict: Resultado con el mensaje extraído
        """
        # Validaciones
        if not ruta_archivo or not os.path.isfile(ruta_archivo):
            raise ValueError("El archivo no existe")
        
        if not clave_b64:
            raise ValueError("La clave AES-256 es requerida")
        
        try:
            clave = base64.b64decode(clave_b64)
            
            if tipo_medio == 'imagen':
                # Extraer de imagen
                mensaje_cifrado = extraer_mensaje_imagen(ruta_archivo)
                mensaje_descifrado = descifrar_mensaje(mensaje_cifrado, clave)
            elif tipo_medio == 'audio':
                # Extraer de audio
                mensaje_descifrado = extraer_mensaje_audio(ruta_archivo, clave)
            else:
                raise ValueError("Tipo de medio no soportado. Use 'imagen' o 'audio'")
            
            return {
                'exito': True,
                'mensaje': mensaje_descifrado,
                'tipo_archivo': tipo_medio
            }
            
        except Exception as e:
            raise Exception(f"Error al extraer el mensaje: {str(e)}")
    
    def extraer_mensaje_blockchain(self, direccion_contrato, clave_b64):
        """
        Extrae un mensaje desde blockchain e IPFS.
        
        Args:
            direccion_contrato (str): Dirección del contrato en blockchain
            clave_b64 (str): Clave AES-256 en base64
        
        Returns:
            dict: Resultado con el mensaje extraído y información del proceso
        """
        # Validaciones
        if not direccion_contrato:
            raise ValueError("La dirección del contrato es requerida")
        
        if not clave_b64:
            raise ValueError("La clave AES-256 es requerida")
        
        proceso_info = []
        archivos_temporales = []
        
        try:
            clave = base64.b64decode(clave_b64)
            
            # Paso 1: Recuperar texto del contrato
            proceso_info.append("🔍 Recuperando texto del contrato blockchain...")
            texto_recuperado = retrieve_text(direccion_contrato)
            
            if not texto_recuperado:
                raise Exception("No se pudo recuperar el texto del contrato")
            
            proceso_info.append(f"✅ Texto recuperado: {len(texto_recuperado)} caracteres")
            
            # Paso 2: Extraer CID del texto esteganografiado
            proceso_info.append("🔍 Extrayendo CID del texto esteganografiado...")
            
            # Crear archivo temporal con el texto
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
                temp_file.write(texto_recuperado)
                temp_file_path = temp_file.name
                archivos_temporales.append(temp_file_path)
            
            cid_extraido = extraer_cid_de_texto(temp_file_path, usar_tab=True)
            if not cid_extraido:
                raise Exception("No se pudo extraer el CID del texto")
            
            proceso_info.append(f"✅ CID extraído: {cid_extraido}")
            
            # Paso 3: Descargar archivo de IPFS
            proceso_info.append("📥 Descargando archivo desde IPFS...")
            
            # Crear archivo temporal para la descarga
            with tempfile.NamedTemporaryFile(delete=False) as temp_download:
                ruta_archivo_temp = temp_download.name
                archivos_temporales.append(ruta_archivo_temp)
            
            # Importar y usar el manejador IPFS
            from ipfs.manejador_ipfs import crear_manejador_ipfs
            manejador_ipfs = crear_manejador_ipfs()
            
            # Descargar archivo
            exito_descarga, mensaje_descarga = manejador_ipfs.descargar_archivo(cid_extraido, ruta_archivo_temp)
            
            if not exito_descarga:
                raise Exception(f"Error al descargar archivo desde IPFS: {mensaje_descarga}")
            
            proceso_info.append(f"✅ {mensaje_descarga}")
            
            # Paso 4: Determinar tipo de archivo y extraer mensaje
            with open(ruta_archivo_temp, 'rb') as f:
                file_content = f.read()
            
            # Detectar tipo de archivo
            tipo_archivo = self._detectar_tipo_archivo(file_content)
            proceso_info.append(f"📁 Archivo detectado como: {tipo_archivo}")
            
            # Extraer mensaje según el tipo
            if tipo_archivo == 'imagen':
                mensaje_descifrado = self._extraer_mensaje_imagen_temp(file_content, clave, archivos_temporales)
            elif tipo_archivo == 'audio':
                mensaje_descifrado = self._extraer_mensaje_audio_temp(file_content, clave, archivos_temporales)
            else:
                raise Exception("Tipo de archivo no soportado")
            
            proceso_info.append("✅ ¡Proceso completado exitosamente!")

            print(f"Mensaje descifrado: {mensaje_descifrado}")

            return {
                'exito': True,
                'mensaje': mensaje_descifrado,
                'tipo_archivo': tipo_archivo,
                'proceso_info': proceso_info,
                'cid_ipfs': cid_extraido
            }
            
        except Exception as e:
            proceso_info.append(f"❌ Error: {str(e)}")
            raise Exception(f"Error durante el proceso: {str(e)}")
        
        finally:
            # Limpiar archivos temporales
            self._limpiar_archivos_temporales(archivos_temporales)
    
    def _detectar_tipo_archivo(self, file_content):
        """Detecta el tipo de archivo basado en sus primeros bytes."""
        primeros_bytes = file_content[:20]
        
        # Firmas de archivos de imagen
        if (primeros_bytes.startswith(b'\xff\xd8\xff') or  # JPEG
            primeros_bytes.startswith(b'\x89PNG') or       # PNG
            primeros_bytes.startswith(b'GIF8') or          # GIF
            primeros_bytes.startswith(b'BM')):             # BMP
            return 'imagen'
        
        # Firmas de archivos de audio
        elif (primeros_bytes.startswith(b'RIFF') or        # WAV
              primeros_bytes.startswith(b'ID3') or         # MP3
              primeros_bytes.startswith(b'\xff\xfb') or    # MP3
              primeros_bytes.startswith(b'OggS') or        # OGG
              primeros_bytes.startswith(b'fLaC')):         # FLAC
            return 'audio'
        
        else:
            raise Exception("Tipo de archivo no reconocido")
    
    def _extraer_mensaje_imagen_temp(self, file_content, clave, archivos_temporales):
        """Extrae mensaje de una imagen desde contenido temporal."""
        # Crear archivo temporal con extensión apropiada
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_image:
            temp_image.write(file_content)
            ruta_imagen_temp = temp_image.name
            archivos_temporales.append(ruta_imagen_temp)
        
        # Extraer mensaje cifrado de la imagen
        mensaje_cifrado = extraer_mensaje_imagen(ruta_imagen_temp)
        
        # Descifrar mensaje
        mensaje_descifrado = descifrar_mensaje(mensaje_cifrado, clave)

        return mensaje_descifrado
        
       
    
    def _extraer_mensaje_audio_temp(self, file_content, clave, archivos_temporales):
        """Extrae mensaje de un audio desde contenido temporal."""
        # Verificar si es WAV
        if not file_content.startswith(b'RIFF'):
            raise Exception("Solo se aceptan archivos de audio en formato WAV")
        
        # Crear archivo temporal con extensión apropiada
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
            temp_audio.write(file_content)
            ruta_audio_temp = temp_audio.name
            archivos_temporales.append(ruta_audio_temp)
        
        # Extraer mensaje del audio
        mensaje_descifrado = extraer_mensaje_audio(ruta_audio_temp, clave)
        
        return mensaje_descifrado
    
    def _limpiar_archivos_temporales(self, archivos_temporales):
        """Limpia archivos temporales."""
        for archivo in archivos_temporales:
            try:
                if os.path.exists(archivo):
                    os.unlink(archivo)
            except:
                pass
    
    def obtener_ultima_direccion_contrato(self):
        """Obtiene la última dirección de contrato generada."""
        return self.direccion_contrato
    
    def validar_archivo_entrada(self, ruta_archivo, tipo_medio):
        """
        Valida que el archivo de entrada sea compatible con el tipo de medio.
        
        Args:
            ruta_archivo (str): Ruta del archivo a validar
            tipo_medio (str): 'imagen' o 'audio'
        
        Returns:
            bool: True si el archivo es válido
        """
        if not os.path.isfile(ruta_archivo):
            return False
        
        try:
            with open(ruta_archivo, 'rb') as f:
                primeros_bytes = f.read(20)
            
            if tipo_medio == 'imagen':
                return (primeros_bytes.startswith(b'\xff\xd8\xff') or  # JPEG
                       primeros_bytes.startswith(b'\x89PNG') or       # PNG
                       primeros_bytes.startswith(b'GIF8') or          # GIF
                       primeros_bytes.startswith(b'BM'))              # BMP
            
            elif tipo_medio == 'audio':
                return primeros_bytes.startswith(b'RIFF')  # WAV
            
            return False
            
        except:
            return False


# Funciones de utilidad para Flask
def crear_servicio_esteganografia():
    """Crea una instancia del servicio de esteganografía."""
    return EsteganografiaService()


def validar_clave_aes(clave_b64):
    """
    Valida que la clave AES esté en formato base64 correcto.
    
    Args:
        clave_b64 (str): Clave en base64
    
    Returns:
        bool: True si la clave es válida
    """
    try:
        decoded = base64.b64decode(clave_b64)
        return len(decoded) == 32  # 256 bits = 32 bytes
    except:
        return False


def generar_clave_aes():
    """
    Genera una nueva clave AES-256.
    
    Returns:
        str: Clave en formato base64
    """
    clave = get_random_bytes(32)
    return base64.b64encode(clave).decode('utf-8')


def obtener_extensiones_permitidas(tipo_medio):
    """
    Obtiene las extensiones de archivo permitidas para un tipo de medio.
    
    Args:
        tipo_medio (str): 'imagen' o 'audio'
    
    Returns:
        list: Lista de extensiones permitidas
    """
    if tipo_medio == 'imagen':
        return ['.bmp', '.png', '.jpg', '.jpeg']
    elif tipo_medio == 'audio':
        return ['.wav']
    else:
        return []
