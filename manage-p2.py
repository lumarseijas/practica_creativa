#!/usr/bin/env python

from lib_vm import VM, NET
import logging
import sys

# Inicialización del log
def init_log():
    logging.basicConfig(level=logging.DEBUG)
    log = logging.getLogger('manage-p2')
    ch = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', "%Y-%m-%d %H:%M:%S")
    ch.setFormatter(formatter)
    log.addHandler(ch)
    log.propagate = False
    return log

log = init_log()

# Parámetros de configuración de las VMs
base_image = "cdps-vm-base-pc1.qcow2"
vm_names = ["C1", "Host", "S1", "S2", "S3"]

# Función para crear el escenario (create)
def create():
    log.info("Creando el escenario...")
    
    # Crear redes (bridges) para LAN1 y LAN2
    lan1 = NET("LAN1")
    lan2 = NET("LAN2")
    lan1.create()
    lan2.create()
    
    # Configurar cada VM con su dirección IP
    for vm_name in vm_names:
        vm = VM(vm_name)
        ifs = []
        if vm_name in ["C1", "Host"]:
            ifs.append({"addr": "10.1.1.{}".format(2 if vm_name == "C1" else 3), "mask": "255.255.255.0"})
        else:
            ifs.append({"addr": "10.1.2.{}".format(10 + int(vm_name[-1])), "mask": "255.255.255.0"})
        
        # Crear la VM con la imagen base y la configuración de interfaces
        vm.create_vm(base_image, ifs)
        log.info(f"Máquina virtual {vm_name} creada.")

# Función para arrancar las VMs (start)
def start():
    log.info("Arrancando las máquinas virtuales...")
    for vm_name in vm_names:
        vm = VM(vm_name)
        vm.start_vm()
        log.info(f"Máquina virtual {vm_name} arrancada.")

# Función para parar las VMs (stop)
def stop():
    log.info("Parando las máquinas virtuales...")
    for vm_name in vm_names:
        vm = VM(vm_name)
        vm.stop_vm()
        log.info(f"Máquina virtual {vm_name} parada.")

# Función para destruir las VMs (destroy)
def destroy():
    log.info("Destruyendo el escenario...")
    for vm_name in vm_names:
        vm = VM(vm_name)
        vm.destroy_vm()
        log.info(f"Máquina virtual {vm_name} destruida.")

    # Eliminar las redes
    NET("LAN1").destroy()
    NET("LAN2").destroy()
    log.info("Redes LAN1 y LAN2 eliminadas.")

# Ejecución principal del script
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: manage-p2.py <orden>")
        print("<orden> debe ser: create, start, stop, destroy")
        sys.exit(1)

    command = sys.argv[1]
    
    if command == "create":
        create()
    elif command == "start":
        start()
    elif command == "stop":
        stop()
    elif command == "destroy":
        destroy()
    else:
        log.error("Orden desconocida. Usa create, start, stop o destroy.")
        sys.exit(1)
