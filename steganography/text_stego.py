import re

def ocultar_cid_en_texto(cid: str, usar_tab: bool = True) -> str:
    """
    Oculta el CID en un texto plano usando esteganografía por espacio en blanco.
    Retorna el texto completo como una cadena, sin escribir a archivo.

    Modo usar_tab:
      - '0' -> espacio ' '
      - '1' -> tabulación '\t'

    Modo no usar_tab:
      - '0' -> espacio único ' '
      - '1' -> cuatro espacios '    '
    """
    # Convertir cada carácter en binario de 8 bits
    ws_binario = ''.join(f'{ord(c):08b}' for c in cid)

    # Generar la secuencia de espacios/tabs
    if usar_tab:
        estego = ''.join('\t' if bit == '1' else ' ' for bit in ws_binario)
    else:
        estego = ''.join('    ' if bit == '1' else ' ' for bit in ws_binario)

    # Ensamblar líneas
    lines = [
        "Encabezado visible o texto señuelo",
        estego,
        "Fin del archivo"
    ]
    return "\n".join(lines) + "\n"


def extraer_cid_de_texto(ruta_archivo: str, usar_tab: bool = True) -> str:
    """
    Extrae el CID desde un archivo de texto con esteganografía de espacios/tabulaciones.
    Solo analiza la segunda línea (la que contiene los espacios/tabulaciones ocultos).
    Valida que el CID extraído tenga formato CIDv0 o CIDv1.
    """
    # Leer todo el contenido en binario y separar líneas
    with open(ruta_archivo, 'rb') as f:
        content = f.read().split(b'\n')

    if len(content) < 2:
        raise ValueError("El archivo no contiene la línea esteganográfica esperada.")

    line2 = content[1]  # bytes de la línea oculta
    bits = []

    if usar_tab:
        # Solo espacio (0x20) y tab (0x09)
        for b in line2:
            if b == 0x20:
                bits.append('0')
            elif b == 0x09:
                bits.append('1')
    else:
        # Decodificar como latin1 para contar espacios
        text_line = line2.decode('latin1')
        idx = 0
        while idx < len(text_line):
            if text_line.startswith('    ', idx):
                bits.append('1')
                idx += 4
            elif text_line[idx] == ' ':
                bits.append('0')
                idx += 1
            else:
                idx += 1

    bit_str = ''.join(bits)
    # Recortar bits sobrantes para múltiplos de 8
    sobra = len(bit_str) % 8
    if sobra:
        bit_str = bit_str[:-sobra]

    # Reconstruir cadena de caracteres
    chars = [chr(int(bit_str[i:i+8], 2)) for i in range(0, len(bit_str), 8)]
    cid = ''.join(chars).strip()

    # Validar formato CIDv0 o CIDv1
    pattern = r"^(Qm[1-9A-HJ-NP-Za-km-z]{44}|b[afy][A-Za-z0-9]{50,})$"
    if not re.match(pattern, cid):
        raise ValueError(f"CID extraído inválido: {cid!r}")

    return cid

