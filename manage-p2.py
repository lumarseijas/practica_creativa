import sys
import os
import subprocess

# Directorios y nombres de archivos
base_image = "cdps-vm-base-pc1.qcow2"
template_xml = "plantilla-vmpc1.xml"
vm_names = ["C1", "Host", "S1", "S2", "S3"]
networks = {"LAN1": "10.1.1.0/24", "LAN2": "10.1.2.0/24"}

def create():
    print("Creando el escenario...")
    
    # Crear los bridges virtuales para LAN1 y LAN2
    create_bridge("LAN1")
    create_bridge("LAN2")
    
    # Crear imágenes de diferencias y archivos XML para cada VM
    for vm_name in vm_names:
        create_diff_image(vm_name)
        create_vm_xml(vm_name)

def start():
    print("Arrancando las máquinas virtuales...")
    for vm_name in vm_names:
        start_vm(vm_name)

def stop():
    print("Parando las máquinas virtuales...")
    for vm_name in vm_names:
        stop_vm(vm_name)

def destroy():
    print("Destruyendo el escenario...")
    for vm_name in vm_names:
        destroy_vm(vm_name)
    remove_bridges()

def create_bridge(lan_name):
    print(f"Creando bridge para {lan_name}...")
    subprocess.run(["sudo", "brctl", "addbr", lan_name])
    subprocess.run(["sudo", "ip", "link", "set", lan_name, "up"])

def remove_bridges():
    print("Eliminando bridges...")
    for lan_name in networks.keys():
        subprocess.run(["sudo", "ip", "link", "set", lan_name, "down"])
        subprocess.run(["sudo", "brctl", "delbr", lan_name])

def create_diff_image(vm_name):
    diff_image = f"{vm_name}.qcow2"
    print(f"Creando imagen diferencial {diff_image}...")
    subprocess.run(["qemu-img", "create", "-f", "qcow2", "-b", base_image, diff_image])

def create_vm_xml(vm_name):
    vm_xml = f"{vm_name}.xml"
    print(f"Creando archivo XML {vm_xml} basado en la plantilla...")
    with open(template_xml) as template_file:
        template_content = template_file.read()
    vm_content = template_content.replace("VMPNAME", vm_name)
    with open(vm_xml, "w") as vm_file:
        vm_file.write(vm_content)

def start_vm(vm_name):
    print(f"Arrancando {vm_name}...")
    subprocess.run(["sudo", "virsh", "create", f"{vm_name}.xml"])

def stop_vm(vm_name):
    print(f"Parando {vm_name}...")
    subprocess.run(["sudo", "virsh", "destroy", vm_name])

def destroy_vm(vm_name):
    print(f"Eliminando archivos de {vm_name}...")
    os.remove(f"{vm_name}.qcow2")
    os.remove(f"{vm_name}.xml")

# Ejecutar el script con el parámetro <orden>
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
        print("Orden desconocida. Usa create, start, stop o destroy.")
        sys.exit(1)
