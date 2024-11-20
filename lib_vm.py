import logging
#
from subprocess import call
#
log = logging.getLogger('manage-p2')

#comparacion con la del año pasado: nombre es name, MV es VM
class VM: 
  def __init__(self, name):
    self.name = name
    log.debug('init VM ' + self.name)

  def create_vm (self, image, interfaces):
    # nota: interfaces es un array de diccionarios de python
    #       añadir los campos que se necesiten
    #LU:
    #campos a crear: que copie base-pc1.qcow2 y plantilla
    call(["qemu-img","create", "-f", "qcow2", "-b", "./cdps-vm-base-pc1.qcow2",  self.name + ".qcow2"])
    call(["cp", "plantilla-vm-pc1.xml", self.name + ".xml"])
    #
    log.debug("create_vm " + self.name + " (image: " + image + ")")
    for i in interfaces:
      log.debug("  if: addr=" + i["addr"] + ", mask=" + i["mask"]) 

  def start_vm (self):
    log.debug("start_vm " + self.name)

  def show_console_vm (self):
    log.debug("show_console_vm " + self.name)

  def stop_vm (self):
    log.debug("stop_vm " + self.name)

  def destroy_vm (self):
    log.debug("destroy_vm " + self.name)

class NET:
  def __init__(self, name):
    self.name = name
    log.debug('init net ' + self.name)

  def create_net(self):
      log.debug('create_net ' + self.name)

  def destroy_net(self):
      log.debug('destroy_net ' + self.name)