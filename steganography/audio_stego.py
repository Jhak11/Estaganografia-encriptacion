"""
Módulo de esteganografía en audio WAV
Funciones para ocultar y extraer mensajes en archivos de audio usando técnica LSB.
"""

import wave
import struct
from encrypto.aes_cipher import cifrar_mensaje, descifrar_mensaje
from ipfs.manejador_ipfs import crear_manejador_ipfs


def ocultar_mensaje_audio(ruta_audio, mensaje, ruta_salida, clave):
    """
    Oculta un mensaje cifrado dentro de un archivo de audio WAV usando LSB
    y sube el resultado a IPFS.
    
    Args:
        ruta_audio (str): Ruta del archivo de audio original
        mensaje (str): Mensaje a ocultar
        ruta_salida (str): Ruta donde guardar el audio con mensaje oculto
        clave (bytes): Clave AES para cifrar el mensaje
        
    Returns:
        dict: Información de IPFS con cid y url, o None si falla
        
    Raises:
        ValueError: Si el mensaje es demasiado largo para el archivo de audio
    """
    mensaje_cifrado = cifrar_mensaje(mensaje, clave)
    # Convierte a bits y agrega un marcador
    mensaje_binario = ''.join(f'{ord(c):08b}' for c in mensaje_cifrado + '#')
    
    # Abre el archivo en modo lectura binaria
    with wave.open(ruta_audio, 'rb') as audio:
        parametros = audio.getparams()
        n_frames = audio.getnframes()
        n_canales = audio.getnchannels()
        audio_datos = audio.readframes(n_frames)
        
        frames = list(struct.unpack('<' + 'h' * n_frames * n_canales, audio_datos))
    
    # El mensaje no debe superar el número de muestras disponibles
    if len(mensaje_binario) > len(frames):
        raise ValueError("El mensaje es demasiado largo para este archivo de audio.")
    
    # Recorre cada bit del mensaje y lo esconde en el LSB de cada muestra de audio
    for i in range(len(mensaje_binario)):
        frames[i] = (frames[i] & ~1) | int(mensaje_binario[i])
    
    # Genera el nuevo audio con el mensaje oculto
    with wave.open(ruta_salida, 'wb') as audio_out:
        audio_out.setparams(parametros)
        audio_out.writeframes(struct.pack('<' + 'h' * len(frames), *frames))

    
    #Subir a IPFS
    manejador = crear_manejador_ipfs()
    exito, mensaje, cid = manejador.subir_archivo(ruta_salida)
    
    if exito and cid:
        info_ipfs = {
            'cid': cid,
            'url': manejador.obtener_url_publica(cid),
            'mensaje': mensaje
        }
        
    return info_ipfs

def extraer_mensaje_audio(audio_ruta, clave):
    """
    Extrae y descifra un mensaje oculto de un archivo de audio WAV.
    
    Args:
        audio_ruta (str): Ruta del archivo de audio con mensaje oculto
        clave (bytes): Clave AES para descifrar el mensaje
        
    Returns:
        str: Mensaje descifrado o mensaje de error
    """
    # Abre el audio en modo binario
    with wave.open(audio_ruta, 'rb') as audio:
        n_frames = audio.getnframes()
        n_canales = audio.getnchannels()
        audio_datos = audio.readframes(n_frames)

        # Extrae el (LSB) de cada muestra de audio.
        frames = list(struct.unpack('<' + 'h' * n_frames * n_canales, audio_datos))
    
    # Cadena de LSB
    bits = ''.join(str(f & 1) for f in frames)
    # Agrupa 8 bits -> convierte a decimal -> char - ASCII = 
    chars = [chr(int(bits[i:i+8], 2)) for i in range(0, len(bits), 8)]

    mensaje = ''
    # Concatenamos hasta encontrar el marcador
    for c in chars:
        if c == '#':
            break
        mensaje += c
    
    # Mandamos a descifrar
    return descifrar_mensaje(mensaje, clave)