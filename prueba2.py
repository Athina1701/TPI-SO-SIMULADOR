from operator import attrgetter, itemgetter

"""dispoMemoria = 450

print("antes: ", dispoMemoria)

def cambiar(dispoMemoria):
    dispoMemoria -= 100
    print("durante: ", dispoMemoria)


cambiar(dispoMemoria)
print("despues: ", dispoMemoria)
"""
"""dispoMemoria = [450, 50, 100]

print("antes: ", dispoMemoria)

def cambiar(dispoMemoria):
    dispoMemoria[2] -= 100
    print("durante: ", dispoMemoria)


cambiar(dispoMemoria)
print("despues: ", dispoMemoria)
"""
memoria = []
#-----------------------------------
#actualizacion: saque a DisponibleEnMemoria como parametro, para usarla como global, y se actualice automaticamente
def CargarEnMemoria(fproceso): #REVISAR #por las, poner como parametro memoria
  global disponibleEnMemoria
  longitudMemoria = len(memoria) 
  if longitudMemoria > 0: #por las dudas no sea una lista vacia. pero capaz no sea necesario
    memoria.sort(key=itemgetter("tamanio")) #ordeno la lista para hacer ASIGNACION BEST FIT
    for i in range(longitudMemoria):  #itero sobre cada particion, para saber cual esta libre
      if memoria[i].get("procesoAsignado") is None: #no hay proceso asignado a la particion
        if fproceso.tamano <= memoria[i].get("tamanio"):
            sobraEspacio = memoria[i].get("tamanio") - fproceso.tamano
            disponibleEnMemoria =  disponibleEnMemoria - fproceso.tamano 
            if sobraEspacio > 0: #o sea, hay espacio libre para crear una particion libre.
              # def asignar id
              particionNueva = { "id": (longitudMemoria+1), "comienzo": memoria[i].get("comienzo") + fproceso.tamano, "tamanio": sobraEspacio , "procesoAsignado": None }
              memoria.append(particionNueva)
              #revisar el "id": (logitudMemoria+1). Quiza sea mejor preguntar por el id de la particion anterior y sumarle 1

            # de memoria[i] (o sea, la particion que esta libre en la cual voy a poner el proceso actual) me quedo con el id y el comienzo, el resto de los datos actualizo:
            memoria[i]["tamanio"] = fproceso.tamano
            memoria[i]["procesoAsignado"] = fproceso.id
            return True #manda un mensaje de que el proceso se cargo en memoria.
        #no ingresó pq la particion era pequeña:
        #else: 
        #  fragmentacion += memoria[i]["tamanio"] #siquiera hace falta, en mi opinion
    return False  #no hubo espacio, por tanto no se cargó.

#CargarEnMemoria mas o menos estaria hecho. pero hay que hacer otra funcion que sea liberar memoria. y en el caso que se liberen dos particiones contiguas. unirlas en una sola particion. para poder ingresar un proceso mas grande.
#Solucion: Version 1: uso un ordenador de lista
def JuntarParticiones(memoria): #revisar, se lo puede mejorar (el indice i+1 me hace ruido)
  """#OJO: esta funcion NO compacta espacios libres. Esta por una cuestion tecnica de como se maneja la memoria en nuestro codigo: 
    porque: como memoria es una lista con elementos (las particiones), cuando se libera un proceso, y luego se libera otro que estaba ocuapndo un espacio sucesivo al anterior, de seguido, 
    cuando llegue otro proceso mas gande, y quiera ocupar  ese espacio entre medio no va a poder, porque en nuestro codigo queda como 2 particiones separadas, entonces detectaria como que no es suficiente espacio para el proceso
  """
  #se dice que es recomendable hacer la copia antes del if. para que no devuelva algo vacio,
  memoriaCopy = [] #no funciona porque no esto haciendo una copia como tal de memoria. estoy modificando sobre las mimsa s direcciones de memoria original.

  longitudMemoria = len(memoria) 
  if longitudMemoria > 1: #seria al pedo ejecutar si solo hay una particion
    memoria.sort(key=itemgetter("comienzo"))  #primero ordeno memoria segun el comienzo de c/particion.
    i = 0

    while i < longitudMemoria:  
      particionNueva = memoria[i].copy() #me quedo con id, comienzo y el procsoAsignado = none.
      if memoria[i].get("procesoAsignado") is None and (i < (longitudMemoria -1)): #particion actual libre: Si. entonces me fijo las siguientes
        #-1 para no pasarme del rango al iterar con i+1
        while ( i+1 < longitudMemoria) and (memoria[i+1].get("procesoAsignado") is None) : #si da True, es pq puedo unirlas
          #que no se toque el orden de la pregunta.
          particionNueva["tamanio"] += memoria[i +1].get("tamanio")
          i += 1
      #en este caso, no hace falta eliminar la particion de la memoria, porque ya estoy colocando solo las nuevas particiones en otra lista de memoria.
      memoriaCopy.append(particionNueva) #ya sea una particion ocupada o no, la copio a la nueva lista de memoria.
      i += 1
  else:
    memoriaCopy= memoria
  return memoriaCopy #si o si debo retornar las variables que fueron reasignadas en la funcion

         

def LiberarMemoria(fproceso, memoria): #revisar #este se usaria al teminar un proceso
  global disponibleEnMemoria
  for particion in memoria: #me fijo en que lugar esta el proceso a quitar
    if str(particion.get("procesoAsignado")) == str(fproceso.id) :
      #El str es para pasar ambos a tipo string para que no de error de tipos. Solo por las dudas. 
      particion["procesoAsignado"] = None
      #ojo que: no elimino el elemento de la lista "memoria", solo cambio el estado, ya está desocupado.
      disponibleEnMemoria += fproceso.tamano
      memoria = JuntarParticiones(memoria)
      return True, memoria
  #si terminó de iterar es pq no encontró el proceso, por eso retorna False, deberia poner tmb un texto que idga que no se encontró
  return False, memoria #no se encontró el proceso en memoria.
#CAMBIAR A RETURN FALSE