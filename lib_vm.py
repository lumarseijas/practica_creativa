#import logging
#
import logging, subprocess, os
#os es para gestionar archivos temporales ;)

from subprocess import call
#from lxml import etree
#
import logging, subprocess, os, tempfile, shutil
log = logging.getLogger('manage-p2')

class VM: 
  def __init__(self, name):
    self.name = name
    log.debug('init VM ' + self.name)
  # def edit_xml(self):
  #

  def create_vm (self, image, interfaces):
    # nota: interfaces es un array de diccionarios de python
    #       añadir los campos que se necesiten
    #que copie base y plantilla
    call(["qemu-img","create", "-f", "qcow2", "-b", "./cdps-vm-base-pc1.qcow2",  self.name + ".qcow2"])
    call(["cp", "plantilla-vm-pc1.xml", self.name + ".xml"])
   # edit_xml(self.name) #edit_xml está creado arriba: sin terminar
    call(["sudo", "virsh", "define", self.name + ".xml"])

    #
    log.debug("create_vm " + self.name + " (image: " + image + ")")
    for i in interfaces:
      log.debug("  if: addr=" + i["addr"] + ", mask=" + i["mask"]) 
    self.configure_vm_files(interfaces)

  def configure_vm_files(self, interfaces):
    log.debug(f"Configuring VM files for {self.name}")

    temp_dir = tempfile.mkdtemp()
    try:
      # Crear archivos de configuración
      hostname_path, interfaces_path = self._create_config_files(temp_dir, interfaces)
      # Copiar archivos a la VM
      self._copy_config_to_vm(hostname_path, interfaces_path)
      # Modificar /etc/hosts y habilitar enrutamiento si es necesario
      self._configure_vm_hosts_and_routing(is_router=(self.name == "lb"))
    finally:
      # Limpiar el directorio temporal
      shutil.rmtree(temp_dir)

  def _create_config_files(self, temp_dir, interfaces):
    """Crea los archivos /etc/hostname y /etc/network/interfaces."""
    log.debug(f"Creating config files for {self.name} in {temp_dir}")

    # Crear /etc/hostname
    hostname_path = os.path.join(temp_dir, "hostname")
    with open(hostname_path, "w") as f:
      f.write(self.name + "\n")

    # Crear /etc/network/interfaces
    interfaces_path = os.path.join(temp_dir, "interfaces")
    with open(interfaces_path, "w") as f:
      f.write("auto lo\niface lo inet loopback\n\n")
      for idx, iface in enumerate(interfaces):
        f.write(f"auto eth{idx}\n")
        f.write(f"iface eth{idx} inet static\n")
        f.write(f"  address {iface['addr']}\n")
        f.write(f"  netmask {iface['mask']}\n")
        if "gateway" in iface:
          f.write(f"  gateway {iface['gateway']}\n")
        f.write("\n")
    
    return hostname_path, interfaces_path

  def _copy_config_to_vm(self, hostname_path, interfaces_path):
    """Copia los archivos de configuración a la imagen de la VM."""
    log.debug(f"Copying config files to {self.name}")
    # Copiar /etc/hostname
    call(["sudo", "virt-copy-in", "-a", f"{self.name}.qcow2", hostname_path, "/etc/"])
    # Copiar /etc/network/interfaces
    call(["sudo", "virt-copy-in", "-a", f"{self.name}.qcow2", interfaces_path, "/etc/network/"])

  def _configure_vm_hosts_and_routing(self, is_router=False):
    """Configura /etc/hosts y habilita el enrutamiento si es router."""
    log.debug(f"Configuring /etc/hosts and routing for {self.name}")
    # Modificar /etc/hosts
    call([
      "sudo", "virt-edit", "-a", f"{self.name}.qcow2", "/etc/hosts",
      "-e", f"s/127.0.1.1.*/127.0.1.1 {self.name}/"
    ])
    # Habilitar enrutamiento si es balanceador
    if is_router:
      call([
        "sudo", "virt-edit", "-a", f"{self.name}.qcow2", "/etc/sysctl.conf",
        "-e", "'s/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/'"
      ])

  def start_vm (self):
    log.debug("start_vm " + self.name)
    call(["sudo", "virsh", "start", self.name])

  def show_console_vm (self):
    log.debug("show_console_vm " + self.name)

  def stop_vm (self):
    log.debug("stop_vm " + self.name)
    call(["sudo", "virsh", "shutdown", self.name])

  def destroy_vm (self):
    log.debug("destroy_vm " + self.name)
    call(["sudo", "virsh", "destroy", self.nombre])

class NET:
  def __init__(self, name):
    self.name = name
    log.debug('init net ' + self.name)

  def create_net(self):
      log.debug('create_net ' + self.name)

  def destroy_net(self):
      log.debug('destroy_net ' + self.name)