def ocultar_cid_en_texto(cid, ruta_salida_texto, usar_tab=True):
    """
    Oculta el CID en un texto plano usando esteganografía por espacio en blanco.
    
    Ejemplo: cada carácter del CID se representa como espacio(0) o tabulación(1).
    """
    ws_binario = ''.join(f'{ord(c):08b}' for c in cid)
    if usar_tab:
        estego = ''.join('\t' if bit == '1' else ' ' for bit in ws_binario)
    else:
        estego = ''.join(' ' if bit == '0' else '    ' for bit in ws_binario)  # 4 espacios = bit 1

    with open(ruta_salida_texto, 'w', encoding='utf-8') as f:
        f.write("Encabezado visible o texto señuelo\n")
        f.write(estego + "\n")
        f.write("Fin del archivo\n")


def extraer_cid_de_texto(ruta_archivo, usar_tab=True):
    """
    Extrae el CID desde el archivo de texto oculto usando esteganografía inversa.
    """
    with open(ruta_archivo, 'r', encoding='utf-8') as f:
        lineas = f.readlines()
    
    oculto = ''
    for linea in lineas:
        if usar_tab:
            bits = ''.join('1' if c == '\t' else '0' for c in linea if c in [' ', '\t'])
        else:
            trozos = linea.split(' ')
            bits = ''.join('1' if len(x) >= 4 else '0' for x in trozos if x.strip() == '')

        oculto += bits

    caracteres = [chr(int(oculto[i:i+8], 2)) for i in range(0, len(oculto), 8)]
    return ''.join(caracteres).strip()