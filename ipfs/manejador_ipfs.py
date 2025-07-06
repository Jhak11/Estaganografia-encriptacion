import os
import subprocess
import json
from typing import Optional, Tuple
            

class ManejadorIPFS:
    """Manejador simplificado para operaciones IPFS locales"""
    
    def __init__(self, api_endpoint: str = "/ip4/127.0.0.1/tcp/5001"):
        """
        Inicializar el manejador IPFS
        
        Args:
            api_endpoint: Endpoint de la API local de IPFS
        """
        self.api_endpoint = api_endpoint
        self.gateway_url = "https://ipfs.io/ipfs/"
    
    def verificar_nodo(self) -> Tuple[bool, str]:
        """
        Verificar si el nodo IPFS local está funcionando
        
        Returns:
            Tuple[bool, str]: (está_funcionando, mensaje_estado)
        """
        try:
            result = subprocess.run([
                'ipfs', 'id', 
                f'--api={self.api_endpoint}'
            ], capture_output=True, text=True, check=True, timeout=10)
            
            node_info = json.loads(result.stdout)
            peer_id = node_info.get('ID', 'Desconocido')[:12] + "..."
            
            return True, f"Nodo IPFS conectado - ID: {peer_id}"
            
        except subprocess.TimeoutExpired:
            return False, "Timeout: El nodo IPFS no responde"
        except subprocess.CalledProcessError as e:
            return False, f"Error de conexión: {e.stderr.strip() if e.stderr else 'Error desconocido'}"
        except (FileNotFoundError, json.JSONDecodeError):
            return False, "IPFS no instalado o nodo no disponible"
        except Exception as e:
            return False, f"Error inesperado: {str(e)}"
    
    def subir_archivo(self, ruta_archivo: str) -> Tuple[bool, str, Optional[str]]:
        """
        Subir un archivo al nodo IPFS local
        
        Args:
            ruta_archivo: Ruta del archivo a subir
            
        Returns:
            Tuple[bool, str, Optional[str]]: (éxito, mensaje, cid)
        """
        if not os.path.exists(ruta_archivo):
            return False, "El archivo no existe", None
        
        try:
            # Subir archivo con anclado automático
            result = subprocess.run([
                'ipfs', 'add',
                f'--api={self.api_endpoint}',
                '--cid-version=1',
                '--pin=true',
                '--progress=false',
                ruta_archivo
            ], capture_output=True, text=True, check=True, timeout=30)
            
            # Extraer CID de la salida
            lines = result.stdout.strip().split('\n')
            cid = None
            for line in lines:
                if line.startswith('added '):
                    cid = line.split()[1]
                    break
            
            if cid:
                filename = os.path.basename(ruta_archivo)
                file_size = os.path.getsize(ruta_archivo)
                size_mb = file_size / (1024 * 1024)
                
                return True, f"Archivo '{filename}' ({size_mb:.2f} MB) subido exitosamente", cid
            else:
                return False, "No se pudo obtener el CID del archivo", None
                
        except subprocess.TimeoutExpired:
            return False, "Timeout: La subida tardó demasiado tiempo", None
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.strip() if e.stderr else "Error desconocido"
            return False, f"Error al subir archivo: {error_msg}", None
        except FileNotFoundError:
            return False, "Ejecutable 'ipfs' no encontrado. Instala IPFS y asegúrate de que esté en PATH", None
        except Exception as e:
            return False, f"Error inesperado: {str(e)}", None
    
    def descargar_archivo(self, cid: str, ruta_destino: str) -> Tuple[bool, str]:
        """
        Descargar un archivo desde IPFS usando su CID
        
        Args:
            cid: Content Identifier del archivo
            ruta_destino: Ruta donde guardar el archivo descargado
            
        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        if not cid or not cid.strip():
            return False, "CID no válido"
        
        try:
            # Crear directorio padre si no existe
            directorio_destino = os.path.dirname(ruta_destino)
            if directorio_destino and not os.path.exists(directorio_destino):
                os.makedirs(directorio_destino)
            
            # Descargar archivo
            subprocess.run([
                'ipfs', 'get', cid, '-o', ruta_destino,
                f'--api={self.api_endpoint}'
            ], check=True, capture_output=True, timeout=60)
            
            if os.path.exists(ruta_destino):
                file_size = os.path.getsize(ruta_destino)
                size_mb = file_size / (1024 * 1024)
                filename = os.path.basename(ruta_destino)
                
                return True, f"Archivo '{filename}' ({size_mb:.2f} MB) descargado exitosamente"
            else:
                return False, "El archivo no se descargó correctamente"
                
        except subprocess.TimeoutExpired:
            return False, "Timeout: La descarga tardó demasiado tiempo"
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode() if e.stderr else "Error desconocido"
            return False, f"Error al descargar archivo: {error_msg}"
        except Exception as e:
            return False, f"Error inesperado: {str(e)}"
    
    def anclar_archivo(self, cid: str) -> Tuple[bool, str]:
        """
        Anclar explícitamente un archivo al nodo local
        
        Args:
            cid: Content Identifier del archivo
            
        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        if not cid or not cid.strip():
            return False, "CID no válido"
        
        try:
            subprocess.run([
                'ipfs', 'pin', 'add', cid,
                f'--api={self.api_endpoint}'
            ], check=True, capture_output=True, timeout=30)
            
            return True, f"Archivo con CID {cid[:20]}... anclado exitosamente"
            
        except subprocess.CalledProcessError as e:
            if "already pinned recursively" in str(e.stderr):
                return True, "El archivo ya está anclado en el nodo"
            else:
                error_msg = e.stderr.decode() if e.stderr else "Error desconocido"
                return False, f"Error al anclar archivo: {error_msg}"
        except Exception as e:
            return False, f"Error inesperado: {str(e)}"
    
    def obtener_url_publica(self, cid: str) -> str:
        """
        Obtener URL pública del gateway para un CID
        
        Args:
            cid: Content Identifier del archivo
            
        Returns:
            str: URL pública del archivo
        """
        return f"{self.gateway_url}{cid}"
    
    def obtener_estadisticas_repo(self) -> Tuple[bool, dict]:
        """
        Obtener estadísticas del repositorio IPFS local
        
        Returns:
            Tuple[bool, dict]: (éxito, estadísticas)
        """
        try:
            result = subprocess.run([
                'ipfs', 'repo', 'stat',
                f'--api={self.api_endpoint}'
            ], capture_output=True, text=True, check=True, timeout=10)
            
            # Parsear estadísticas básicas
            stats = {}
            for line in result.stdout.strip().split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    stats[key.strip()] = value.strip()
            
            return True, stats
            
        except Exception:
            return False, {}


# Función de conveniencia para uso directo
def crear_manejador_ipfs() -> ManejadorIPFS:
    """
    Crear una instancia del manejador IPFS con configuración por defecto
    
    Returns:
        ManejadorIPFS: Instancia del manejador
    """
    return ManejadorIPFS()

