#!/usr/bin/env python

from lib_vm import VM, NET
import logging, sys, json, os
from subprocess import call

# Carga de configuración desde el archivo JSON
with open('manage-p2.json', 'r') as file:
    data_json = json.load(file)
if data_json["number_of_servers"]>5 or data_json["number_of_servers"]<1:
    print("Número de servidores inválido, introduzca en su archivo de configuración un número de servidores de 1 a 5.")
else:
    number_of_servers = data_json["number_of_servers"]


debug = data_json["debug"]

if debug == True:
	logging.basicConfig(level =logging.DEBUG)
		
else:
	logging.basicConfig(level =logging.INFO)

logger = logging.getLogger('manage-p2')

def init_log():
    # Creacion y configuracion del logger
    logging.basicConfig(level=logging.DEBUG)
    log = logging.getLogger('auto_p2')
    ch = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', "%Y-%m-%d %H:%M:%S")
    ch.setFormatter(formatter)
    log.addHandler(ch)
    log.propagate = False

def pause():
    input("-- Press <ENTER> to continue...")

# Main
init_log()
logger.info('CDPS - mensaje info1')

def create(number_of_servers):
  
    logger.debug("Iniciando creación del escenario.")
    image = "./cdps-vm-base-pc1.qcow2"
    number_of_servers = int(number_of_servers)

    # Crear las redes LAN1 y LAN2
    logger.debug("Creando redes LAN1 y LAN2.")
    lan1 = NET('LAN1')
    lan1.create_net()
    lan2 = NET('LAN2')
    lan2.create_net()

    # Crear Cliente c1
    logger.debug("Creando cliente c1.")
    interfaces_c1 = [{"addr": "10.1.1.2", "mask": "255.255.255.0"}]
    c1 = VM("c1")
    c1.create_vm(image, interfaces_c1)

    # Crear Balanceador lb
    logger.debug("Creando balanceador lb.")
    lb_interfaces = [
        {"addr": "10.1.1.1", "mask": "255.255.255.0"},
        {"addr": "10.1.2.1", "mask": "255.255.255.0"}
    ]
    lb = VM("lb")
    lb.create_vm(image, lb_interfaces)

    # Crear Servidores Web
    logger.debug(f"Creando {number_of_servers} servidores web.")
    for i in range(1, number_of_servers+1): 
        server_name = f"s{i}" 
        logger.debug(f"Creando servidor {server_name}.")
        server_interfaces = [{"addr": f"10.1.2.1{i}", "mask": "255.255.255.0"}] 
        server = VM(server_name)
        server.create_vm(image, server_interfaces)
    
    logger.debug("Escenario creado correctamente.")

def start(server):
    logger.debug(f"Iniciando arranque para: {server}.")
    if server == "all":
        logger.debug("Arrancando cliente c1.")
        c1 = VM('c1')
        c1.start_vm()

        logger.debug("Arrancando balanceador lb.")
        lb = VM('lb')
        lb.start_vm()

        logger.debug(f"Arrancando {number_of_servers} servidores web.")
        for n in range(1, number_of_servers+1):
            server_name = f"s{n}"
            logger.debug(f"Arrancando servidor {server_name}.")
            server = VM(server_name)
            server.start_vm()

    else:
        logger.debug(f"Arrancando máquina específica: {server}.")
        vm = VM(server)
        vm.start_vm()

    logger.debug("Arranque completado.")

def stop(server):
    logger.debug(f"Deteniendo: {server}.")
    if server == "all":
        logger.debug("Deteniendo cliente c1.")
        c1 = VM('c1')
        c1.stop_vm()

        logger.debug("Deteniendo balanceador lb.")
        lb = VM('lb')
        lb.stop_vm()

        logger.debug(f"Deteniendo {number_of_servers} servidores web.")
        for n in range(1, number_of_servers+1):
            server_name = f"s{n}"
            logger.debug(f"Deteniendo servidor {server_name}.")
            vm = VM(server_name)
            vm.stop_vm()

    else:
        logger.debug(f"Deteniendo máquina específica: {server}.")
        vm = VM(server)
        vm.stop_vm()

    logger.debug("Detención completada.")

def destroy():
    logger.debug("Iniciando destrucción del escenario.")
    logger.debug("Liberando cliente c1.")
    c1 = VM('c1')
    c1.destroy_vm()

    logger.debug("Liberando balanceador lb.")
    lb = VM('lb')
    lb.destroy_vm()

    logger.debug(f"Liberando {number_of_servers} servidores web.")
    for n in range(0, number_of_servers+1):
        server_name = f"s{n+1}"
        logger.debug(f"Liberando servidor {server_name}.")
        server = VM(server_name)
        server.destroy_vm()

    # Eliminar redes
    logger.debug("Eliminando redes LAN1 y LAN2.")
    eth0 = NET('LAN1')
    eth0.destroy_net()
    eth1 = NET('LAN2')
    eth1.destroy_net()

    logger.debug("Escenario eliminado correctamente.")
#MEJORAS:
def watch(): 
	os.system("xterm -title monitor -e watch sudo virsh list --all & ")


def help(): # print de los comandos y su uso
    mensaje = """
        Lista de comandos:
        create (<number_of_servers>): Crea la red y el número de servidores especificado.
        start (<server_name>): Arranca todas las máquinas o una específica.
        stop (<server_name>): Detiene todas las máquinas o una específica.
        destroy: Elimina todas las máquinas y redes configuradas.
        watch: Muestra el estado de todas las máquinas virtuales.
        help: Muestra esta lista de comandos y su funcionalidad.
    """
    print(mensaje)
    


# Manejo de argumentos
arguments = sys.argv
if len(arguments) == 2:
    if arguments[1] == "create":
        create(number_of_servers)
    if arguments[1] == "start":
        start("all")
    if arguments[1] == "stop":
        stop("all")
    if arguments[1] == "destroy":
        destroy()
    if arguments[1] == "watch":
        watch()
    if arguments[1] == "help":
        help()

if len(arguments) >= 3:
    if arguments[1] == "create":
        for server in arguments[2:]:
            create(server)
    if arguments[1] == "start":
        for server in arguments[2:]:
            start(server)
    if arguments[1] == "stop":
        for server in arguments[2:]:
            stop(server)