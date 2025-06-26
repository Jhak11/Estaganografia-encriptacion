"""
Módulo de cifrado AES-256
Contiene las funciones para cifrar y descifrar mensajes usando AES en modo ECB.
"""

from Crypto.Cipher import AES
import base64

def pad(texto):
    """
    Añade padding al texto para que sea múltiplo de 16 bytes.
    
    Args:
        texto (str): Texto a rellenar
        
    Returns:
        str: Texto con padding añadido
    """
    while len(texto) % 16 != 0:
        texto += ' '
    return texto

def cifrar_mensaje(mensaje, clave):
    """
    Cifra un mensaje usando AES-256 en modo ECB.
    
    Args:
        mensaje (str): Mensaje a cifrar
        clave (bytes): Clave AES de 32 bytes
        
    Returns:
        str: Mensaje cifrado codificado en base64
    """
    # Añadimos padding
    mensaje = pad(mensaje)
    # Creamos el cifrador
    cipher = AES.new(clave, AES.MODE_ECB)
    # Convertimos y ciframos 
    cifrado = cipher.encrypt(mensaje.encode('utf-8'))  # convierte a bytes y luego lo cifra
    # Codificamos en base 64 y luego convertimos a texto
    return base64.b64encode(cifrado).decode('utf-8')  # codifica en base 64(junta bloques) y devuelve bytes q luego convertimos a texto con decode

def descifrar_mensaje(mensaje_cifrado_b64, clave):
    """
    Descifra un mensaje AES-256 codificado en base64.
    
    Args:
        mensaje_cifrado_b64 (str): Mensaje cifrado en base64
        clave (bytes): Clave AES de 32 bytes
        
    Returns:
        str: Mensaje descifrado o mensaje de error
    """
    try:
        # Decodificación base64
        mensaje_cifrado = base64.b64decode(mensaje_cifrado_b64)  # convierte a los bytes originales del cifrado
        # Creación del AES
        cipher = AES.new(clave, AES.MODE_ECB)  # creamos un objeto cifrador
        # Descifrado 
        descifrado = cipher.decrypt(mensaje_cifrado)  # mensaje_cifrado ya está en bytes
        # Conversión a texto
        return descifrado.decode('utf-8').rstrip(' ')  # rstrip elimina espacios
    except Exception as e:
        return f"[Error al descifrar]: {e}"