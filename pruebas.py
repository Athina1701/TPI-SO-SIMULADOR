

class Proceso:
  def __init__(self, id, TA, TI, tamano, estado):
    self.id = id
    self.TA = TA
    self.TI = TI
    self.tamano = tamano
    self.estado = estado
    self.TR = 0. # TR = T_fin – TA
    self.TE = 0. # TE = TR – TI, donde TI es la duración de la ráfaga de CPU requerida).


memoria = []
particionInicial = { "id": 1, "comienzo": 0, "tamanio": 450, "procesoAsignado": None }
memoria.append(particionInicial)




def CargarEnMemoria(proceso, disponibleEnMemoria):
  logitudMemoria = len(memoria) #itero sobre cada particion 
  if logitudMemoria > 0: #por las dudas no sea una lista vacia. pero capaz no sea necesario
    for i in range(logitudMemoria):
      if memoria[i].get("procesoAsignado") is None: #no hay proceso asignado a la particion
        if proceso.tamano <= memoria[i].get("tamanio"):
            disponibleEnMemoria =  disponibleEnMemoria - proceso.tamano 
            if disponibleEnMemoria != 0: #o sea, que aun espacio en memoria  
                particionNueva = { "id": (logitudMemoria+1), "comienzo": memoria[i].get("comienzo") + proceso.tamano, "tamanio": disponibleEnMemoria , "procesoAsignado": None }
                memoria.append(particionNueva)

          # de memoria[i] (o sea, la particion que esta libre y el cual entra el proceso) me quedo con el id y el comienzo, el resto de los datos actualizo:
            memoria[i]["tamanio"] = proceso.tamano
            memoria[i]["procesoAsignado"] = proceso.id

            return True, disponibleEnMemoria #manda un mensaje de que el proceso se cargo en memoria.
    return False, disponibleEnMemoria #no hubo espacio, por tanto no se cargó.

"main:"

p1 = Proceso("p1", 1, 3, 100, "nuevo")
p2 = Proceso("p2", 1, 6, 350, "nuevo")
p3 = Proceso("p3", 2, 4, 70, "nuevo")

procesos = [ p1 ,p2, p3]
tamanoDisponible = 450

estorbo =  { "id": 3, "comienzo": 90 , "tamanio": 100, "procesoAsignado": "p7" }
memoria.append(estorbo)
tamanoDisponible = tamanoDisponible - estorbo["tamanio"]
"""es para probar que tal funciona"""

for p in procesos:
  hayEspacio, tamanoDisponible = CargarEnMemoria(p, tamanoDisponible )
  print("cargó: ", hayEspacio)
print("fragmentacion:" , tamanoDisponible)
print(memoria)


""" Dio bien, hizo bien el calculo. Peron fijarse que creó una particion con tamaño 0, o sea que, al cargar el proceso, debo preguntar si quedó memoria aún. o sea: 
“tamanio": memoria[i].get("tamanio") - proceso.tamano = 0 ????
para evitar que cree la particion. Además: crerar funcion para devolver espacio disponible, al terminar un proceso.
---------------- otra cosa: creo que seria mejor tener una variable aparte que indique la disponibilidad de memmoria, y que se le vaya restando o sumando a esta: memoriaDisponible = 450.
prpceso cargado: memoriaDispo - tamaño proceso cargado.
para no estar usando:  memoria[i].get("tamanio") - proceso.tamano, 

#digamos que ya arreglé lo anterior
"""


