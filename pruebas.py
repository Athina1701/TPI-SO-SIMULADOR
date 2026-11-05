from operator import attrgetter, itemgetter


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


def limpiarMemoria(): # me refiero a unir particiones libres contiguas.
  pass

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
#en mi opinion, tira fruta la ia resepecto a disponibleEnMemoria como segundo parametro de retorno.Asi que voy a probar sin
# actualizacion: en definitiva, no es lo mismo, no actualiza el valor si no lo pongo como parametro de retorno.


#main: #esto es para saber si funciona


p1 = Proceso("p1", 1, 3, 10, "nuevo")
p2 = Proceso("p2", 1, 6, 30, "nuevo")
p3 = Proceso("p3", 2, 4, 70, "nuevo")

procesos = [ p1 ,p2, p3]
tamanoDisponible = 450


"""
estorbo =  { "id": 3, "comienzo": 90 , "tamanio": 100, "procesoAsignado": "p7" }
memoria.append(estorbo)
tamanoDisponible = tamanoDisponible - estorbo["tamanio"]"""
"""es para probar que tal funciona"""

#esto es para saber si funciona
"""
for p in procesos:
  hayEspacio, tamanoDisponible = CargarEnMemoria(p, tamanoDisponible )
  print("cargó: ", hayEspacio)
print("fragmentacion:" , tamanoDisponible)
print(memoria)
"""

""" Dio bien, hizo bien el calculo. Peron fijarse que creó una particion con tamaño 0, o sea que, al cargar el proceso, debo preguntar si quedó memoria aún. o sea: 
“tamanio": memoria[i].get("tamanio") - proceso.tamano = 0 ????
para evitar que cree la particion. Además: crerar funcion para devolver espacio disponible, al terminar un proceso.
---------------- otra cosa: creo que seria mejor tener una variable aparte que indique la disponibilidad de memmoria, y que se le vaya restando o sumando a esta: memoriaDisponible = 450.
prpceso cargado: memoriaDispo - tamaño proceso cargado.
para no estar usando:  memoria[i].get("tamanio") - proceso.tamano, 

#digamos que ya arreglé lo anterior
"""
memoria = [
  {"id": 1, "comienzo": 0, "tamanio": 50, "procesoAsignado": p1.id},
  {"id": 2, "comienzo": 50, "tamanio": 70, "procesoAsignado": p2.id },
  {"id": 3, "comienzo": 120, "tamanio": 100, "procesoAsignado": None},
  {"id": 5, "comienzo": 220, "tamanio": 30, "procesoAsignado": None},
  {"id": 6, "comienzo": 250, "tamanio": 50, "procesoAsignado": p3.id},
  {"id": 4, "comienzo": 300, "tamanio": 50, "procesoAsignado": None},
  ]



def JuntarParticiones(memoria): #revisar, se lo puede mejorar (el indice i+1 me hace ruido)
  """#OJO: esta funcion NO compacta espacios libres. Esta por una cuestion tecnica de como se maneja lamemoria en nuestro codigo: 
    porque: como memoria es una lista con elementos (las particiones), cuando se libera un proceso, y luego se libera otro que estaba ocuapndo un espacio junto al anterior, de seguido, 
    cuando llegue otro proceso mas gande, y quiera ocupar  ese espacio entre medio no va a poder, porque en nuestro codigo queda como 2 particiones separadas, entonces detectaria como que no es suficiente espacio para el proceso
  """
  longitudMemoria = len(memoria) 
  if longitudMemoria > 1: #seria al pedo ejecutar si solo hay una paarticion
    memoria = sorted(memoria, key = itemgetter("comienzo") ) #primero ordeno memoria segun el comienzo de c/particion. 
    memoriaCopy = []
    i = 0
    while i < longitudMemoria : # -1 para no pasarme del rango al iterar con i+1
      particionNueva = memoria[i] #me quedo con id, comienzo y el procsoAsignado = none.
      if memoria[i].get("procesoAsignado") is None and (i < (longitudMemoria -1)): #particion actual libre: Si. entonces me fijo las siguientes
        
        while memoria[i+1].get("procesoAsignado") is None: #si da True, es pq puedo unirlas
          #particionNueva = {"id": memoria[i].get("id"), "comienzo" memoria[i].get("comienzo") , memoria[i+1].get("tamanio") }
          particionNueva["tamanio"] += memoria[i +1].get("tamanio")
          i += 1

      memoriaCopy.append(particionNueva) #ya sea una particion ocupada o no, la copio a la nueva lista de memoria.
      i += 1
    print("\n dentro dela funcion: ",memoriaCopy)
  return memoriaCopy #si o si debo retornar las variables que fueron reasignadas en la funcion
                    #al llamar a la funcion, le asigno la funcion a memoria, asi se queda con el valor de memoriaCopy

"""implementacion: """
"""
print("\n" ,memoria)
memoria = JuntarParticiones(memoria)
#si os i debo retornar las variables que fueron reasignadas en la funcion

for p in memoria:
  print("\n",p)
  #Funciona. Pero: revisar lo de los ID"""


def EliminarDeCola(cola, fProceso): #recibe la cola y el proceso a eliminar.
   # no creo que pueda hacer uno general para todas las colas
   cola.remove(fProceso) #elimina el proceso puntual de la cola que se le pase. 
   #NOTA: esta funcion "remove" permite eliminar por nombre del elemento, si quisisera eliminar por indice de la lista: "del cola[indice]".
  
print (memoria)

part =   {"id": 2, "comienzo": 50, "tamanio":200, "procesoAsignado": p2.id }
EliminarDeCola(memoria, part["id"] )

print (memoria) #la funcion asi tal cual, elimina SOLO SI ES IDENTICO al que esta en cola. asi q, cuidado