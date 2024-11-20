#!/usr/bin/env python

from lib_vm import VM, NET
import logging, sys, json

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
    programPause = input("-- Press <ENTER> to continue...")

with open('manage-p2.json', 'r') as file:
    data_json = json.load(file)

if data_json["number_of_servers"]>5 or data_json["number_of_servers"]<1:
    print("Número de servidores inválido, introduzca en su archivo de configuración un número de servidores de 1 a 5.")
else:
    num_serv = data_json["number_of_servers"]

# debug = data_json["debug"]

# if debug == True:
# 	logging.basicConfig(level =logging.DEBUG)
		
# else:
# 	logging.basicConfig(level =logging.INFO)
     
# Main
init_log()
print('CDPS - mensaje info1')
#print('Cristina Rodríguez, Elsa Sastre y Lucía Martínez')

# Ejemplo de creacion de una maquina virtual
s1 = VM('s1')
pause()

ifs = []
ifs.append( { "addr": "10.11.12.10", "mask": "255.255.255.0" } )
ifs.append( { "addr": "10.11.13.10", "mask": "255.255.255.0" } )
s1.create_vm('cdps-vm.qcow2', ifs )
pause()

s1.start_vm()
pause()

s1.stop_vm()
pause()

s1.destroy_vm()