from solcx import compile_standard, install_solc
from web3 import Web3
import json

# Instala compilador Solidity 0.8.0 si no está
# install_solc('0.8.0')

# Leer contrato Solidity
with open("blockchain/TextStorage.sol", "r") as file:
    contract_source = file.read()

# Compilar contrato
compiled_sol = compile_standard({
    "language": "Solidity",
    "sources": {"TextStorage.sol": {"content": contract_source}},
    "settings": {"outputSelection": {"*": {"*": ["abi", "evm.bytecode"]}}}
}, solc_version="0.8.0")

#obtener ABI y Bytecode
#ABI
#El ABI es una descripción en JSON
#define cómo interactuar con el contrato inteligente desde aplicaciones externas (Python) funciones, parametros
abi = compiled_sol['contracts']['TextStorage.sol']['TextStorage']['abi']

#bytecode
#El Bytecode es el código de máquina para la EVM (Ethereum Virtual Machine)
#que el contrato ejecuta cuando se despliega.
#Es lo que efectivamente se sube a la blockchain cuando despliegas el contrato, Es el resultado final de compilar el código Solidity.
#maquina pura cadena de haxdecimal
bytecode = compiled_sol['contracts']['TextStorage.sol']['TextStorage']['evm']['bytecode']['object']

# Conectar a Ganache GUI
ganache_url = "http://127.0.0.1:7545"
w3 = Web3(Web3.HTTPProvider(ganache_url))

# Obtener lista de cuentas
# accounts = w3.eth.accounts

# Crear contrato en Python
# Representa la clase del contrato Solidity compilado.
# todavía NO está desplegado en la blockchain.
# Sabe cómo es el contrato (gracias a la ABI).
# Sabe cómo desplegarlo (gracias al Bytecode).
TextStorage = w3.eth.contract(abi=abi, bytecode=bytecode)

# FUNCIONES:
#desplegar contrato
# deployer_Acount es la cuenta que pagara el gas y firmara la trasaccionde del despliegue
def deploy_contract(deployer_account):
    """Desplegar un nuevo contrato desde una cuenta específica."""
    # Blockchain, despliega este contrato usando esta cuenta
    tx_hash = TextStorage.constructor().transact({'from': deployer_account})
    #Esperar confirmación de la red 
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    #devuelve datos como la direccion del contrato, si fue exitosa o no y el total de gas consumido
    # print(f"Nuevo contrato desplegado en: {tx_receipt.contractAddress}")
    return tx_receipt.contractAddress

#Almacenar texto
#cambio pendiente -> redcucir el gasto de gas a solo una vez desplegar el contrato y inicicalizar el texto
#$NT: se crea un nuevo contrato cada vez que llamamos a la funcion
def store_text(text, deployer_account):
    """Desplegar un nuevo contrato y almacenar texto en él."""
    new_contract_address = deploy_contract(deployer_account)
    new_contract_instance = w3.eth.contract(address=new_contract_address, abi=abi)

    # Almacenar texto en el nuevo contrato
    tx_hash = new_contract_instance.functions.storeText(text).transact({'from': deployer_account})
    w3.eth.wait_for_transaction_receipt(tx_hash)

    #print(f"Texto '{text}' almacenado en nuevo contrato: {new_contract_address}")
    return new_contract_address

#Recuperar texto
def retrieve_text(contract_addr):
    """Recuperar texto desde una dirección de contrato específica."""
    contract = w3.eth.contract(address=contract_addr, abi=abi)
    result = contract.functions.retrieveText().call()#no gasta gas es solo lectura
    #print(f"Texto recuperado desde {contract_addr}: {result}")
    return result

#Obtener lista de cuentas
def cuentas():
    """Lista de cuentas disponibles."""
    return w3.eth.accounts

