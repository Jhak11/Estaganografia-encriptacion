// Variables globales
let lastContractAddress = '';

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    updateFileAccepts();
});

// Event Listeners
function initializeEventListeners() {
    // Tabs
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const tab = this.textContent.includes('Enviar') ? 'send' : 'receive';
            showTab(tab);
        });
    });

    // Cambio de tipo de medio en envío
    document.querySelectorAll('input[name="tipo_medio"]').forEach(radio => {
        radio.addEventListener('change', updateFileAccepts);
    });

    // Cambio de tipo de archivo en recepción
    document.querySelectorAll('input[name="tipo_archivo"]').forEach(radio => {
        radio.addEventListener('change', updateFileAccepts);
    });

    // Formularios
    document.getElementById('send-form').addEventListener('submit', handleSendForm);
    document.getElementById('extract-file-form').addEventListener('submit', handleExtractFileForm);
    document.getElementById('extract-blockchain-form').addEventListener('submit', handleExtractBlockchainForm);
}

// Funciones de UI
function showTab(tab) {
    // Actualizar botones
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelector(`.tab-btn:nth-child(${tab === 'send' ? 1 : 2})`).classList.add('active');

    // Actualizar contenido
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    document.getElementById(`${tab}-tab`).classList.add('active');
}

function toggleMethod() {
    const method = document.querySelector('input[name="metodo"]:checked').value;
    
    document.getElementById('archivo-method').style.display = method === 'archivo' ? 'block' : 'none';
    document.getElementById('blockchain-method').style.display = method === 'blockchain' ? 'block' : 'none';
}

function updateFileAccepts() {
    const sendTipo = document.querySelector('input[name="tipo_medio"]:checked')?.value;
    const receiveTipo = document.querySelector('input[name="tipo_archivo"]:checked')?.value;
    
    // Archivo de envío
    if (sendTipo) {
        const sendFile = document.getElementById('archivo');
        sendFile.accept = sendTipo === 'imagen' ? '.bmp,.png,.jpg,.jpeg' : '.wav';
    }
    
    // Archivo de recepción
    if (receiveTipo) {
        const receiveFile = document.getElementById('archivo-extract');
        receiveFile.accept = receiveTipo === 'imagen' ? '.bmp,.png,.jpg,.jpeg' : '.wav';
    }
}

function showLoading() {
    document.getElementById('loading').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loading').style.display = 'none';
}

function showError(message) {
    alert('Error: ' + message);
}

function showSuccess(message) {
    alert('Éxito: ' + message);
}

// Funciones de formularios
async function handleSendForm(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const mensaje = formData.get('mensaje').trim();
    
    if (!mensaje) {
        showError('El mensaje no puede estar vacío');
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch('/ocultar_mensaje', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.exito) {
            showSendResult(result);
            e.target.reset();
        } else {
            showError(result.mensaje || 'Error al ocultar el mensaje');
        }
    } catch (error) {
        showError('Error de conexión: ' + error.message);
    } finally {
        hideLoading();
    }
}

async function handleExtractFileForm(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const clave = formData.get('clave').trim();
    
    if (!clave) {
        showError('La clave AES-256 es requerida');
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch('/extraer_mensaje_archivo', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.exito) {
            showReceiveResult(result.mensaje);
            e.target.reset();
        } else {
            showError(result.mensaje || 'Error al extraer el mensaje');
        }
    } catch (error) {
        showError('Error de conexión: ' + error.message);
    } finally {
        hideLoading();
    }
}

async function handleExtractBlockchainForm(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const direccion = formData.get('direccion').trim();
    const clave = formData.get('clave').trim();
    
    if (!direccion || !clave) {
        showError('La dirección del contrato y la clave son requeridas');
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch('/extraer_mensaje_blockchain', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.exito) {
            showReceiveResult(result.mensaje);
            if (result.proceso_info) {
                showProcessInfo(result.proceso_info);
            }
            e.target.reset();
        } else {
            showError(result.mensaje || 'Error al extraer el mensaje');
        }
    } catch (error) {
        showError('Error de conexión: ' + error.message);
    } finally {
        hideLoading();
    }
}

// Funciones de resultado
function showSendResult(result) {
    const resultBox = document.getElementById('send-result');
    const claveInput = document.getElementById('clave-generada');
    const contratoInput = document.getElementById('direccion-contrato');
    const downloadLink = document.getElementById('download-link');
    
    claveInput.value = result.clave;
    contratoInput.value = result.direccion_contrato;
    
    // Guardar dirección para uso posterior
    lastContractAddress = result.direccion_contrato;
    
    // Configurar enlace de descarga
    if (result.archivo_descarga) {
        downloadLink.href = result.archivo_descarga;
        downloadLink.style.display = 'block';
    } else {
        downloadLink.style.display = 'none';
    }
    
    resultBox.style.display = 'block';
    resultBox.scrollIntoView({ behavior: 'smooth' });
}

function showReceiveResult(mensaje) {
    const resultBox = document.getElementById('receive-result');
    const mensajeTextarea = document.getElementById('mensaje-extraido');
    
    mensajeTextarea.value = mensaje;
    resultBox.style.display = 'block';
    resultBox.scrollIntoView({ behavior: 'smooth' });
}

function showProcessInfo(steps) {
    const processInfo = document.getElementById('process-info');
    const processSteps = document.getElementById('process-steps');
    
    processSteps.innerHTML = '';
    steps.forEach(step => {
        const stepDiv = document.createElement('div');
        stepDiv.textContent = step;
        stepDiv.style.marginBottom = '5px';
        stepDiv.style.fontFamily = 'Courier New, monospace';
        stepDiv.style.fontSize = '12px';
        processSteps.appendChild(stepDiv);
    });
    
    processInfo.style.display = 'block';
}

// Funciones de utilidad
function copyKey() {
    const claveInput = document.getElementById('clave-generada');
    claveInput.select();
    document.execCommand('copy');
    showSuccess('Clave copiada al portapapeles');
}

function useLastContract() {
    const direccionInput = document.getElementById('direccion-blockchain');
    
    if (lastContractAddress) {
        direccionInput.value = lastContractAddress;
        showSuccess('Dirección del último contrato cargada');
    } else {
        showError('No hay dirección de contrato disponible');
    }
}

// Funciones auxiliares
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

