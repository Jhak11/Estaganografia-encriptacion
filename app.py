"""
Punto de entrada principal de la aplicación Flask
Canal de comunicación seguro con esteganografía
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
import tempfile
import traceback
from werkzeug.utils import secure_filename

# Importar el servicio de esteganografía
from Controller.serv_flask import (
    EsteganografiaService, 
    validar_clave_aes, 
    obtener_extensiones_permitidas
)

app = Flask(__name__, 
            template_folder='WEB/templates',
            static_folder='WEB/static')

# Configuración
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB máximo
app.config['UPLOAD_FOLDER'] = 'temp_uploads'
app.config['OUTPUT_FOLDER'] = 'temp_outputs'

# Crear carpetas temporales si no existen
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Instancia del servicio
servicio_estego = EsteganografiaService()

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/ocultar', methods=['POST'])
def ocultar_mensaje():
    """Endpoint para ocultar mensaje en imagen o audio"""
    try:
        # Validar datos del formulario
        mensaje = request.form.get('mensaje', '').strip()
        tipo_medio = request.form.get('tipoMedio', 'imagen')
        nombre_salida = request.form.get('nombreSalida', '').strip()
        
        if not mensaje:
            return jsonify({'exito': False, 'mensaje': 'El mensaje no puede estar vacío'})
        
        if not nombre_salida:
            return jsonify({'exito': False, 'mensaje': 'Debe especificar un nombre de archivo de salida'})
        
        # Validar archivo subido
        if 'archivoEntrada' not in request.files:
            return jsonify({'exito': False, 'mensaje': 'No se ha seleccionado ningún archivo'})
        
        archivo = request.files['archivoEntrada']
        if archivo.filename == '':
            return jsonify({'exito': False, 'mensaje': 'No se ha seleccionado ningún archivo'})
        
        # Validar extensión
        extensiones_permitidas = obtener_extensiones_permitidas(tipo_medio)
        ext_archivo = os.path.splitext(archivo.filename)[1].lower()
        
        if ext_archivo not in extensiones_permitidas:
            return jsonify({
                'exito': False, 
                'mensaje': f'Extensión no permitida. Use: {", ".join(extensiones_permitidas)}'
            })
        
        # Guardar archivo temporal
        nombre_archivo = secure_filename(archivo.filename)
        ruta_entrada = os.path.join(app.config['UPLOAD_FOLDER'], nombre_archivo)
        archivo.save(ruta_entrada)
        
        # Generar ruta de salida
        if not nombre_salida.endswith(ext_archivo):
            nombre_salida += ext_archivo
        
        ruta_salida = os.path.join(app.config['OUTPUT_FOLDER'], secure_filename(nombre_salida))
        
        # Validar archivo de entrada
        if not servicio_estego.validar_archivo_entrada(ruta_entrada, tipo_medio):
            return jsonify({
                'exito': False, 
                'mensaje': f'El archivo no es un {tipo_medio} válido'
            })
        
        # Ocultar mensaje
        resultado = servicio_estego.ocultar_mensaje(
            mensaje=mensaje,
            ruta_entrada=ruta_entrada,
            ruta_salida=ruta_salida,
            tipo_medio=tipo_medio
        )
        
        # Limpiar archivo temporal de entrada
        if os.path.exists(ruta_entrada):
            os.remove(ruta_entrada)

        resultado['nombre_archivo'] = os.path.basename(ruta_salida)  # para mostrar o descargar

        
        
        return jsonify(resultado)
        
    except Exception as e:
        print(f"Error en ocultar_mensaje: {str(e)}")
        traceback.print_exc()
        return jsonify({'exito': False, 'mensaje': str(e)})

@app.route('/extraer-archivo', methods=['POST'])
def extraer_mensaje_archivo():
    """Endpoint para extraer mensaje desde archivo local"""
    try:
        # Validar datos del formulario
        tipo_medio = request.form.get('tipoMedioExtraccion', 'imagen')
        clave_b64 = request.form.get('claveExtraccion', '').strip()
        
        if not clave_b64:
            return jsonify({'exito': False, 'mensaje': 'La clave AES-256 es requerida'})
        
        if not validar_clave_aes(clave_b64):
            return jsonify({'exito': False, 'mensaje': 'La clave AES-256 no es válida'})
        
        # Validar archivo subido
        if 'archivoExtraccion' not in request.files:
            return jsonify({'exito': False, 'mensaje': 'No se ha seleccionado ningún archivo'})
        
        archivo = request.files['archivoExtraccion']
        if archivo.filename == '':
            return jsonify({'exito': False, 'mensaje': 'No se ha seleccionado ningún archivo'})
        
        # Validar extensión
        extensiones_permitidas = obtener_extensiones_permitidas(tipo_medio)
        ext_archivo = os.path.splitext(archivo.filename)[1].lower()
        
        if ext_archivo not in extensiones_permitidas:
            return jsonify({
                'exito': False, 
                'mensaje': f'Extensión no permitida. Use: {", ".join(extensiones_permitidas)}'
            })
        
        # Guardar archivo temporal
        nombre_archivo = secure_filename(archivo.filename)
        ruta_archivo = os.path.join(app.config['UPLOAD_FOLDER'], nombre_archivo)
        archivo.save(ruta_archivo)
        
        # Validar archivo
        if not servicio_estego.validar_archivo_entrada(ruta_archivo, tipo_medio):
            return jsonify({
                'exito': False, 
                'mensaje': f'El archivo no es un {tipo_medio} válido'
            })
        
        # Extraer mensaje
        resultado = servicio_estego.extraer_mensaje_archivo(
            ruta_archivo=ruta_archivo,
            clave_b64=clave_b64,
            tipo_medio=tipo_medio
        )
        
        # Limpiar archivo temporal
        if os.path.exists(ruta_archivo):
            os.remove(ruta_archivo)
        
        return jsonify(resultado)
        
    except Exception as e:
        print(f"Error en extraer_mensaje_archivo: {str(e)}")
        traceback.print_exc()
        return jsonify({'exito': False, 'mensaje': str(e)})

@app.route('/extraer-blockchain', methods=['POST'])
def extraer_mensaje_blockchain():
    """Endpoint para extraer mensaje desde blockchain e IPFS"""
    try:
        # Validar datos del formulario
        direccion_contrato = request.form.get('direccionContratoExtraccion', '').strip()
        clave_b64 = request.form.get('claveBlockchain', '').strip()
        
        if not direccion_contrato:
            return jsonify({'exito': False, 'mensaje': 'La dirección del contrato es requerida'})
        
        if not clave_b64:
            return jsonify({'exito': False, 'mensaje': 'La clave AES-256 es requerida'})
        
        if not validar_clave_aes(clave_b64):
            return jsonify({'exito': False, 'mensaje': 'La clave AES-256 no es válida'})
        
        # Extraer mensaje desde blockchain
        resultado = servicio_estego.extraer_mensaje_blockchain(
            direccion_contrato=direccion_contrato,
            clave_b64=clave_b64
        )
        
        return jsonify(resultado)
        
    except Exception as e:
        print(f"Error en extraer_mensaje_blockchain: {str(e)}")
        traceback.print_exc()
        return jsonify({'exito': False, 'mensaje': str(e)})
    
@app.route('/ultima-direccion', methods=['GET'])
def obtener_ultima_direccion():
    """Devuelve la última dirección de contrato registrada"""
    try:
        ultima_direccion = servicio_estego.obtener_ultima_direccion_contrato()
        return jsonify({'exito': True, 'direccion': ultima_direccion})
    except Exception as e:
        return jsonify({'exito': False, 'mensaje': str(e)})

@app.route('/descargar/<filename>')
def descargar_archivo(filename):
    """Endpoint para descargar archivos generados"""
    try:
        filename = secure_filename(filename)
        ruta_archivo = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        
        if not os.path.exists(ruta_archivo):
            return jsonify({'error': 'Archivo no encontrado'}), 404
        
        return send_file(ruta_archivo, as_attachment=True)
        
    except Exception as e:
        print(f"Error en descargar_archivo: {str(e)}")
        return jsonify({'error': 'Error al descargar archivo'}), 500

@app.errorhandler(413)
def archivo_muy_grande(error):
    """Manejo de archivos demasiado grandes"""
    return jsonify({'exito': False, 'mensaje': 'El archivo es demasiado grande (máximo 50MB)'}), 413

@app.errorhandler(500)
def error_interno(error):
    """Manejo de errores internos"""
    return jsonify({'exito': False, 'mensaje': 'Error interno del servidor'}), 500

# Función para limpiar archivos temporales antiguos
def limpiar_archivos_temporales():
    """Limpia archivos temporales antiguos"""
    import time
    
    carpetas = [app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER']]
    
    for carpeta in carpetas:
        if os.path.exists(carpeta):
            for archivo in os.listdir(carpeta):
                ruta_archivo = os.path.join(carpeta, archivo)
                if os.path.isfile(ruta_archivo):

                    # Eliminar archivos más antiguos de 1 hora
                    tiempo_actual = time.time()
                    tiempo_archivo = os.path.getmtime(ruta_archivo)
                    if tiempo_actual - tiempo_archivo > 350:  # 1 hora
                        try:
                            os.remove(ruta_archivo)
                            print(f"Archivo temporal eliminado: {ruta_archivo}")
                        except:
                            pass

if __name__ == '__main__':
    # Limpiar archivos temporales al inicio
    limpiar_archivos_temporales()
    
    # Ejecutar aplicación
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )