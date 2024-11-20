#import logging
#
import logging, subprocess

from subprocess import call
#from lxml import etree
#
log = logging.getLogger('manage-p2')

class VM: 
  def __init__(self, name):
    self.name = name
    log.debug('init VM ' + self.name)
  # def edit_xml(self):
  #   template_xml = "plantilla-vm-pc1.xml"
  #   output_xml = f"{self.name}.xml"

  def create_vm (self, image, interfaces):
    # nota: interfaces es un array de diccionarios de python
    #       añadir los campos que se necesiten
    #que copie base-pc1.qcow2 y plantilla
    call(["qemu-img","create", "-f", "qcow2", "-b", "./cdps-vm-base-pc1.qcow2",  self.name + ".qcow2"])
    call(["cp", "plantilla-vm-pc1.xml", self.name + ".xml"])
   # edit_xml(self.name) #edit_xml está creado arriba: sin terminar
    call(["sudo", "virsh", "define", self.name + ".xml"])

    #
    log.debug("create_vm " + self.name + " (image: " + image + ")")
    for i in interfaces:
      log.debug("  if: addr=" + i["addr"] + ", mask=" + i["mask"]) 

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