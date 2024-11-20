import logging

log = logging.getLogger('manage-p2')

class VM: 
  def __init__(self, name):
    self.name = name
    log.debug('init VM ' + self.name)

  def create_vm (self, image, interfaces):
    # nota: interfaces es un array de diccionarios de python
    #       aÃ±adir los campos que se necesiten
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