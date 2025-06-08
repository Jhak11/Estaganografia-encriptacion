def guardar_cid_en_texto(cid, ruta_archivo, usar_tab=True):
    """
    Guarda el CID en un archivo de texto con formato.
    Args:
        cid (str): Hash CID obtenido al subir archivo a IPFS.
        ruta_archivo (str): Ruta donde guardar el archivo de texto.
        usar_tab (bool): Si True, usa tabuladores; si False, usa espacios.
    """
    separador = '\t' if usar_tab else '    '  # 4 espacios si no usa tab
    contenido = f"CID{separador}{cid}\n"
    with open(ruta_archivo, 'w', encoding='utf-8') as f:
        f.write(contenido)