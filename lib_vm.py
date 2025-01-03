import logging
import os
from subprocess import call
from lxml import etree

log = logging.getLogger('manage-p2')

def edit_xml(virtualm):
  if virtualm  == "c1":
    bridge_aux = "LAN1"
  elif virtualm == "lb":
    bridge_aux = "LAN1" 
  else:
    bridge_aux = "LAN2"
  

  cwd = os.getcwd()
  path = cwd + "/" + virtualm

  tree = etree.parse(path + ".xml")

  root = tree.getroot()

  name = root.find("name")
  name.text = virtualm

  sourceFile = root.find("./devices/disk/source")
  sourceFile.set("file", path + ".qcow2")

  interface = root.find("./devices/interface")
  interface.set("type", "bridge")

  bridge = root.find("./devices/interface/source")
  bridge.set("bridge", bridge_aux) 

  virtualport = etree.SubElement(interface, "virtualport")
  virtualport.set("type", "openvswitch")

  interface = root.find("./devices/interface")
  etree.SubElement(interface, "virtualport", type="openvswitch")

  if virtualm == "lb":
    devices = root.find("./devices")
    interface_lan2 = etree.SubElement(devices, "interface", type="bridge")
    etree.SubElement(interface_lan2, "source", bridge="LAN2")
    etree.SubElement(interface_lan2, "model", type="virtio")
    etree.SubElement(interface_lan2, "virtualport", type="openvswitch")



  #como lb tiene dos interfaces habria que añadir la segunda? o con lo de temporal funciona?

  fout = open(path + ".xml", "w")
  fout.write(etree.tounicode(tree, pretty_print = True))
  fout.close()

  '''
  if virtualm == "lb":
    fin = open(path + ".xml",'r')   #fin es el XML correspondiente a lb, en modo solo lectura
    fout = open("tmp.xml",'w')  #fout es un XML temporal abierto en modo escritura
    for line in fin:
      if "</interface>" in line:
        fout.write("</interface>\n <interface type='bridge'>\n <source bridge='"+"LAN2"+"'/>\n <model type='virtio'/>\n<virtualport type = 'openvswitch'/>\n </interface>\n ")
      #si el XML de lb contiene un interface (que lo va a contener, ya que previamente se le habrá añadido el bridge LAN1), se le añade al XML temporal otro bridge: LAN2
      else:
        fout.write(line)
    fin.close()
    fout.close()

    call(["cp","./tmp.xml", path + ".xml"])  #sustituimos es XML por el temporal, que es el que contiene las dos LAN
    call(["rm", "-f", "./tmp.xml"])
  '''
def configure(virtualm):

  cwd = os.getcwd()
  path = cwd + "/" + virtualm

  fout = open("hostname", 'w')
  fout.write(virtualm + "\n")
  fout.close()
  call(["sudo", "virt-copy-in", "-a", virtualm + ".qcow2", "hostname", "/etc"])
  call(["rm", "-f", "hostname"])

  call("sudo virt-edit -a {virtualm}.qcow2 /etc/hosts -e 's/127.0.1.1.*/127.0.1.1" + virtualm + "/", shell=True) #

  fout = open("interfaces", 'w')
  if virtualm == "lb":
    fout.write("auto lo \niface lo inet loopback\n auto eth0\n iface eth0 inet static\n address 10.1.1.1\n netmask 255.255.255.0\nauto eth1\niface eth1 inet static\n  address 10.1.2.1\n netmask 255.255.255.0\n")
  else:
    if virtualm == "c1":
      fout.write("auto lo \niface lo inet loopback\n auto eth0\n iface eth0 inet static\n address 10.1.1.2\n netmask 255.255.255.0\n gateway 10.1.1.1\n")

    else:
      fout.write("auto lo \niface lo inet loopback\n auto eth0\n iface eth0 inet static\n address 10.1.2.1"+str(virtualm)[1]+"\n netmask 255.255.255.0\n gateway 10.1.2.1\n") #
  
  fout.close()
  call(["sudo", "virt-copy-in", "-a", virtualm + ".qcow2", "interfaces", "/etc/network"])
  call(["rm", "-f", "interfaces"])
  if virtualm == "lb":
        call("sudo virt-edit -a lb.qcow2 /etc/sysctl.conf -e 's/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/'", shell=True) #0 en vez de 1


class VM:
  def __init__(self, name):
    self.name = name
    log.debug('init VM ' + self.name)

  def create_vm (self, image, interfaces):
    # nota: interfaces es un array de diccionarios de python
    #       añadir los campos que se necesiten
    log.debug("create_vm " + self.name + " (image: " + image + ")")
    for i in interfaces:
      log.debug("  if: addr=" + i["addr"] + ", mask=" + i["mask"])
    call(["qemu-img","create", "-f", "qcow2", "-F", "qcow2", "-b", "./cdps-vm-base-pc1.qcow2",  self.name + ".qcow2"])
    call(["cp", "plantilla-vm-pc1.xml", self.name + ".xml"])
    virtualm = self.name
    edit_xml(virtualm)
    call(["sudo", "virsh", "define", self.name +".xml"])
    log.debug("Máquinas "+self.name+" definida con éxito.")
    #virtualm = self.name
    configure(virtualm)
    
  def start_vm (self):
    log.debug("start_vm " + self.name)
    call(["sudo", "virsh", "start", self.name])
    os.system("xterm -e 'sudo virsh console "+ self.name +"' &")

  def show_console_vm (self):
    log.debug("show_console_vm " + self.name)
    os.system("xterm -e 'sudo virsh console "+ self.name +"' &")

  def stop_vm (self):
    log.debug("stop_vm " + self.name)
    call(["sudo","virsh", "shutdown", self.name])

  def destroy_vm (self):
    log.debug("destroy_vm " + self.name)
    call(["sudo", "virsh", "destroy", self.name])
    call(["sudo", "virsh", "undefine", self.name])
    call(["rm", "-f", self.name+".qcow2"])
    call(["rm", "-f", self.name+".xml"])

class NET:
  def __init__(self, name):
    self.name = name
    log.debug(f"Initializing network: {self.name}")

  def create_net(self):
    log.debug('create_net ' + self.name)
    call(["sudo", "ovs-vsctl", "add-br", self.name])
    call(["sudo", "ifconfig", self.name, "up"])
    call(["sudo", "ifconfig", "LAN1", "10.1.1.3/24"])
    call(["sudo", "ip", "route", "add", "10.1.0.0/16", "via", "10.1.1.1"])
    #call(["sudo", "ifconfig", "LAN1", "10.1.1.3/24"])
    # call(["sudo", "ip", "link", "set", "dev", self.name, "up"])  
   
  def destroy_net(self):
    log.debug('destroy_net ' + self.name)
    call(["sudo", "ifconfig", self.name, "down"])
   # call(["sudo", "ip", "link", "set", "dev", self.name, "down"])
    call(["sudo", "ovs-vsctl", "del-br", self.name])