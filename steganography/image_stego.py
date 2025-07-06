"""
Módulo de esteganografía en imágenes
Funciones para ocultar y extraer mensajes en imágenes usando técnica LSB.
"""

import stepic
from PIL import Image
import os
from ipfs.manejador_ipfs import crear_manejador_ipfs


    
def convertir_a_bmp_si_necesario(ruta_original):
    """
    Convierte una imagen a formato BMP si no lo es ya.
    
    Args:
        ruta_original (str): Ruta de la imagen original
        
    Returns:
        str: Ruta de la imagen BMP (original o convertida) o None si hay error
    """
    if ruta_original.lower().endswith(".bmp"):  # comprueba si termina en bmp
        return ruta_original  # No necesita conversión
    
    try:
        imagen = Image.open(ruta_original)
        ruta_bmp = ruta_original.rsplit('.', 1)[0] + "_temp.bmp"  # borramos la extensión orig y colocamos bmp
        imagen.save(ruta_bmp, format="BMP")
        return ruta_bmp
    except Exception as e:
        # En lugar de messagebox.showerror, lanzamos una excepción
        # que será manejada por la aplicación PyQt5
        raise Exception(f"No se pudo convertir la imagen a BMP: {e}")



def ocultar_mensaje_imagen(ruta_imagen, mensaje_cifrado, ruta_salida):
    """
    Oculta un mensaje cifrado en una imagen usando esteganografía LSB
    y sube el resultado a IPFS.
    
    Args:
        ruta_imagen (str): Ruta de la imagen original
        mensaje_cifrado (str): Mensaje cifrado a ocultar
        ruta_salida (str): Ruta donde guardar la imagen con mensaje oculto
        
    Returns:
        dict: Información de IPFS con cid y url, o None si falla
        
    Raises:
        Exception: Si hay error en el proceso de esteganografía
    """
    # Convertir imagen si es necesario
    ruta_bmp = convertir_a_bmp_si_necesario(ruta_imagen)
    if ruta_bmp is None:
        raise Exception("No se pudo convertir la imagen a BMP")
    
    try:
        # Proceso de esteganografía
        imagen = Image.open(ruta_bmp)
        imagen_estego = stepic.encode(imagen, mensaje_cifrado.encode('utf-8'))
        imagen_estego.save(ruta_salida, 'BMP')
        
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

        
    finally:
        # Eliminar imagen temporal si se creó
        if ruta_bmp != ruta_imagen and os.path.exists(ruta_bmp):
            os.remove(ruta_bmp)

def extraer_mensaje_imagen(ruta_imagen):
    """
    Extrae un mensaje oculto de una imagen.
    
    Args:
        ruta_imagen (str): Ruta de la imagen con mensaje oculto
        
    Returns:
        str: Mensaje extraído (aún cifrado)
        
    Raises:
        Exception: Si hay error en la extracción
    """
    imagen = Image.open(ruta_imagen)
    mensaje_cifrado = stepic.decode(imagen)  # sacamos bytes y pasamos a texto
    return mensaje_cifrado