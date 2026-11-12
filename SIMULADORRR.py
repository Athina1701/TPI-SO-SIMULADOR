
#ARCHIVO PRINCIPAL: SIMULADOR 
#Esta muy cargaado de anotaciones, al terminarlo, habria que "limpiarlo"

#hice una copia pq voy a cambiar muchas cosas del anterior

#esto podria estar en "informacion"
"""
TA: tiempo de arribo
TI: tiempo de irrupcion
TR: tiempo de retorno
TE: tiempo de espera
estados: "nuevo", "listo", "suspendido", "ejecutando" , "terminado"

Las presentaciones de salida deberán realizarse cada vez que llega un nuevo proceso
y se termina un proceso en ejecución.
"""
from operator import attrgetter, itemgetter

class Proceso:
  def __init__(self, id, TA, TI, tamano, estado):
    self.id = id
    self.TA = TA
    self.TI = TI
    self.resguardoTI = TI
    self.tamano = tamano
    self.estado = estado
    self.TR = 0. # TR = T_fin – TA
    self.TE = 0. # TE = TR – TI, donde TI es la duración de la ráfaga de CPU requerida).
#HACER: al tomar los procesos del archivo, debo validar los tiposde datos. tamaño debe ser numerico, en el archivo me lo entrega como string, o al menoS eso entiendo, lo tengo que pasar

#
nuevos = []
listos = []
listosSuspendidos = []
terminados = []
#cola de ejecucion, lo aplico como un diccionario:
ejecucion = { "enUso": False, "procEjecutandose": None, "tiempoEjecucion": 0 }


def existeArchivo(nombreArchivo):
  try:
    with open(nombreArchivo, 'r') as archi:
      primerLinea = archi.readline()
      if primerLinea == "":
        print("El archivo esta vacio.")
        return False
      return True
  except FileNotFoundError:
    print("El archivo no fue encontrado.")
    return False
    #si es false, se le da otra chance para cargar, o que se cree desde 0. #HACERRRR

def cargarNuevos(nombreArchivo, colaNuevos):
    global cantProcesos
    with open(nombreArchivo, 'r') as archi:
    #cargar procesos
      for linea in archi: 
        if linea != "": 
          #cada linea es un proceso.
          # El proceso está cargado en archivo como: id,TA,TI,memoria.
          linea = linea.strip().split(",") #strip para sacar \n y split para separar por comas.
          procesoNuevo = Proceso(linea[0], int(linea[1]), int(linea[2]), int(linea[3]), "nuevo")
          # nombre = linea 0 , TA = linea 1, 
          #pNuevo = Proceso(p1,3, 5, 20, "nuevo")

          #TE = TR – TI, tengo 2 opciones: ya resto el TI aca y al terminar el proceso le sumo el retorno (que se calcula cuando termina)
          #procesoNuevo.TE = - procesoNuevo.TI
          #o la segunda opcion: ir sumando TE +1 por cada vez que el timpo pasa

          colaNuevos.append(procesoNuevo) # proc cargado a la lista.

          cantProcesos += 1  
          if cantProcesos > 10: #vigila que no se pase de 10 proc.
            print("Se ha llegado al limite de procesos a cargar. Cantidad actual: ", cantProcesos)
            break

        else: 
          continue #esto por si hay un renglon vacio.

  #ordena procesos. ordeno la cola de nuevos por TA, si hay dos con TA iguales, ordeno por id.
    colaNuevos.sort(key=attrgetter("TA", "TI"))
     #OTRA FORMA: colaNuevos = sorted(nuevos, key = attrgetter('TA', 'TI') ) #revisar #probe y funciona. 

def EliminarDeCola(cola, proceso): #recibe la cola y el proceso a eliminar.
  """colaCopy = list(cola)
  for i, proc in enumerate(colaCopy):
      if proc.get("id") == proceso.id:
          del cola[i]
          return True
  return False"""
  #otra froma de: la anterior no parece eliminar correctamente
  seEncontroProc = False
  indice = 0
  while indice < len(cola):
    proc = cola[indice]
    if proc.id == proceso.id:
      resguardoIndice = indice
      seEncontroProc = True
      break
    indice += 1
  if seEncontroProc:
    del cola[resguardoIndice]



texto = "es para indicar el titulo. Ejemplo: 'Cola de nuevos', 'Cola de listos', etc."

def MostrarCola(cola, texto):
    print(texto)
    print(f"| {'ID_P':<5} | {'TA':^4} | {'TI':^4} | {'Tamaño KB':^10} | {'Estado':<10} |")
    print("-" * 50)
    for p in cola:
        print(f"| {p.id:<5} | {p.TA:>4} | {p.TI:>4} | {p.tamano:>10} | {p.estado:<10} |")

  #lo que hace el ''TA':>4' es rellenar con espacios vacios a la izq, si el texto tiene menos de 4 caracteres.
  #print("-" * 50) lo que hace es imprimir 50 guiones, para separar el titulo del  contenido

def MostrarMemoria(fMemoria, fragmentacion):
  print(f"{'ID_Particion':<12} | {'Comienzo':^4} | {'Tamaño KB':^8} | {'Proceso Asignado':^16} | {'Fragmentacion':<13}")
  print("-" * 70)
  print(f"{'Par_0':<12} | {'450':^8} | {'100':^9} | {' SIST. OPERATIVO':^16} | {' ':<13}")
  fMemoria.sort(key=itemgetter("comienzo")) 
  for part in fMemoria:
    pAsignado = part["procesoAsignado"]
    if pAsignado is None:
      pAsignado = "Libre"
    print(f"Par_{part["id"]:<8} | {part["comienzo"]:^8} | {part["tamanio"]:^9} | {pAsignado:^16} | {0:^13}")
  print("Cantidad restante disponible en memoria: ", disponibleEnMemoria, "\n")
  print("cantidad de particiones: ", len(memoria))
  if fragmentacion: #pregunta por lista NO vacia
    MostrarFragmentacion(fragmentacion)


"""El simulador deberá presentar como salida la siguiente información:
 El estado del procesador (proceso que se encuentra corriendo en ese instante)
 La tabla de particiones de memoria, la cual deberá contener (Id de partición, dirección de comienzo de
partición, tamaño de la partición, id de proceso asignado a la partición, fragmentación)
 El estado de la cola de procesos listos y listos/suspendidos."""

def PresentacionDeSalida(): #muestro todas las colas
  print("\n             -------- TTIEMPO ACTUAL: ", tActual, " ---------\n")
  #Mostrar cola de Ejecucion
  if tActual != 0:
    print("\n-----Estado del PROCESADOR Actualmente-----\n")
    print(f"| {'Proceso Ejecutandose':^20} | {'Tiempo de Irrupción':^19} | ")
    print("-" * 50)
    if ejecucion["enUso"] == True:
      pEjecutandose = ejecucion["procEjecutandose"]
      print(f"| {pEjecutandose.id :^20} | {pEjecutandose.TI :^19} |")
    else: 
      print(f"| {'Ninguno':^20} | {'0':^19} |")
      print("\n--(Actualmente no hay procesos ejecutandose)--")

  #Mostrar Memoria-----------------------------------------------------------------
  print("\n-----Tabla de PARTICIONES de MEMORIA-----")
  #mostrar: id part, dir de comienzo, tamaño, id proceso asignado, fragmentacion?????
  #mostrar tabla
  MostrarMemoria(memoria, fragmentacion)
  print(" Cantidad de Procesos Actualmente: ", cantProcesos)
  #-----------------------------------------------------------------------------------
  print("\n-----Cola de Procesos NUEVOS-----")
  print(f"| {'ID_P':<5} | {'TA':^4} | {'TI':^4} | {'Tamaño KB':^10} | {'Estado':<10} |")
  print("-" * 50)
  for p in nuevos:
    #if p.TA <= tActual:
    print(f"| {p.id:<5} | {p.TA:>4} | {p.TI:>4} | {p.tamano:>10} | {p.estado:<10} |")

#---------------------------------------------------------------------
  texto = "\n-----Cola de Procesos LISTOS-----"
  MostrarCola(listos, texto)
  texto = "\n-----Cola de Procesos LISTOS y SUSPENDIDOS-----"
  MostrarCola(listosSuspendidos, texto)
  texto = "\n-----Cola de Procesos TERMINADOS-----"
  print(texto)
  print(f"| {'ID_P':<5} | {'TA':^4} | {'TI':^4} | {'Tamaño KB':^10} | {'Estado':<10} |")
  print("-" * 50)
  for p in terminados:
      print(f"| {p.id:<5} | {p.TA:>4} | {p.resguardoTI:>4} | {p.tamano:>10} | {p.estado:<10} |")


#---------------------------------------------------------------
# Por el momento, la memoria se maneja d esta forma. Es lo que se me ocurrió
# Es una lista de diccionarios. Las particiones son los diccionarios

memoria = []
particionInicial = { "id": "1", "comienzo": 0, "tamanio": 450, "procesoAsignado": None, "fragmentacion": 0 }
#en la consigna piden al fragmentacion. Pero no entiendo para qué, si es variable
#hay que revisar en el def cargarmemoria, los ID porque se repiten.
memoria.append(particionInicial)
""" o lo que es lo mismo:
memoria = [ { "id": 1, "comienzo": 0, "tamanio": 450, "procesoAsignado": None } , ]
"""

disponibleEnMemoria = 450 #este debo ir disminuyendolo, y aumentarlo al liberar memoria.

#-----------------------------------
#actualizacion: saque a DisponibleEnMemoria como parametro, para usarla como global, y se actualice automaticamente
def CargarEnMemoria(fproceso): #REVISAR #por las, poner como parametro memoria
  global disponibleEnMemoria
  fFragmentacion= [] #la idea es reiniciar la lista de fragmentacion 
  longitudMemoria = len(memoria) 
  if longitudMemoria > 0: #por las dudas no sea una lista vacia. pero capaz no sea necesario
    memoria.sort(key=itemgetter("tamanio")) #ordeno la lista para hacer ASIGNACION BEST FIT
    for i in range(longitudMemoria):  #itero sobre cada particion, para saber cual esta libre
      if memoria[i].get("procesoAsignado") is None: #no hay proceso asignado a la particion
        
        if fproceso.tamano <= memoria[i].get("tamanio"):
            sobraEspacio = memoria[i].get("tamanio") - fproceso.tamano # si hay fragmentacion interna al asignar el proceso, creo otra particion
            disponibleEnMemoria =  disponibleEnMemoria - fproceso.tamano 
            if sobraEspacio > 0: #o sea, hay espacio libre para crear una particion libre.
              # def asignar id
              particionNueva = { "id": (longitudMemoria+1), "comienzo": memoria[i].get("comienzo") + fproceso.tamano, "tamanio": sobraEspacio , "procesoAsignado": None }
              memoria.append(particionNueva)
              #revisar el "id": (logitudMemoria+1). Quiza sea mejor preguntar por el id de la particion anterior y sumarle 1

            # de memoria[i] (o sea, la particion que esta libre en la cual voy a poner el proceso actual) me quedo con el id y el comienzo, el resto de los datos actualizo:
            memoria[i]["tamanio"] = fproceso.tamano
            memoria[i]["procesoAsignado"] = fproceso.id            
            return True, fFragmentacion #manda un mensaje de que el proceso se cargo en memoria.
        else: #no ingresó pq la particion era pequeña:
          #fragmentacion:
          fFragmentacion.append(memoria[i]) #guardo la particion la cual el proceso no pudo entrar
        
    return False, fFragmentacion  #no hubo espacio, por tanto no se cargó.

#CargarEnMemoria mas o menos estaria hecho. pero hay que hacer otra funcion que sea liberar memoria. y en el caso que se liberen dos particiones contiguas. unirlas en una sola particion. para poder ingresar un proceso mas grande.
#Solucion: Version 1: uso un ordenador de lista

#if fragmentacion: #en el codigo ppal.
def MostrarFragmentacion(fFragmentacion):
  fragTotal = 0
  print("---Hubo FRAGMENTACIÓN en las particiones: ---")
  for part in fFragmentacion:
    print(f"      -Particion: {part["id"]} ; Tamaño: {part["tamanio"]}")
    fragTotal += part["tamanio"]
  print("--Fragmentación total en la memoria: ", fragTotal, "\n")


def JuntarParticiones(fmemoria): #revisar, se lo puede mejorar (el indice i+1 me hace ruido)
  """#OJO: esta funcion NO compacta espacios libres. Esta por una cuestion tecnica de como se maneja la memoria en nuestro codigo: 
    porque: como memoria es una lista con elementos (las particiones), cuando se libera un proceso, y luego se libera otro que estaba ocuapndo un espacio sucesivo al anterior, de seguido, 
    cuando llegue otro proceso mas gande, y quiera ocupar  ese espacio entre medio no va a poder, porque en nuestro codigo queda como 2 particiones separadas, entonces detectaria como que no es suficiente espacio para el proceso
  """
  #se dice que es recomendable hacer la copia antes del if. para que no devuelva algo vacio,
  memoriaCopy = [] #no funciona porque no esto haciendo una copia como tal de memoria. estoy modificando sobre las mimsa s direcciones de memoria original.

  longitudMemoria = len(fmemoria) 
  if longitudMemoria > 1: #seria al pedo ejecutar si solo hay una particion
    fmemoria.sort(key=itemgetter("comienzo"))  #primero ordeno memoria segun el comienzo de c/particion.
    i = 0

    while i < longitudMemoria:  
      particionNueva = fmemoria[i].copy() #me quedo con id, comienzo y el procsoAsignado = none.
      if fmemoria[i].get("procesoAsignado") is None and (i < (longitudMemoria -1)): #particion actual libre: Si. entonces me fijo las siguientes
        #-1 para no pasarme del rango al iterar con i+1
        while ( i+1 < longitudMemoria) and (fmemoria[i+1].get("procesoAsignado") is None) : #si da True, es pq puedo unirlas
          #que no se toque el orden de la pregunta.
          particionNueva["tamanio"] += fmemoria[i +1].get("tamanio")
          i += 1
          continue #no le afecta en nada
      #en este caso, no hace falta eliminar la particion de la memoria, porque ya estoy colocando solo las nuevas particiones en otra lista de memoria.
      memoriaCopy.append(particionNueva) #ya sea una particion ocupada o no, la copio a la nueva lista de memoria.
      i += 1
  else:
    memoriaCopy= fmemoria
    #borrar los print
  print("\n----cantidad de particiones en JUNTARMEMORIA: ", len(fmemoria))
  print("cantidad de particiones en JUNTARMEMORIA de la mem original: ", len(memoria))

  print("cantidad de particiones de la copia: ", len(memoriaCopy))

  return memoriaCopy #si o si debo retornar las variables que fueron reasignadas en la funcion      

def LiberarMemoria(fproceso, memoria): #revisar #este se usaria al teminar un proceso
  global disponibleEnMemoria, fragmentacion
  for particion in memoria: #me fijo en que lugar esta el proceso a quitar
    if str(particion.get("procesoAsignado")) == str(fproceso.id) :
      #El str es para pasar ambos a tipo string para que no de error de tipos. Solo por las dudas. 
      particion["procesoAsignado"] = None
      #ojo que: no elimino el elemento de la lista "memoria", solo cambio el estado, ya está desocupado.
      disponibleEnMemoria += fproceso.tamano
      memoria = JuntarParticiones(memoria)
      return True, memoria
    fragmentacion = [] #reinicio las fragmentaciones que pudieron haber ocurrido.
  #si terminó de iterar es pq no encontró el proceso, por eso retorna False, deberia poner tmb un texto que idga que no se encontró
  return False, memoria #no se encontró el proceso en memoria.


#----------------------------------------------------------------------------fin Memoria

def CargarListosYSuspendidos(fProceso, colaActual): #hacer
  fProceso.estado = "suspendido"
  listosSuspendidos.append(fProceso) #este lo agrega al final de la cola, no se si seria mejor acomodar segun TI.
  EliminarDeCola(colaActual, fProceso)

def AgregarAListos(fProceso, colaListos):
  fProceso.estado = "listo"
  mayorTI = True
  #cargar segun TI
  listosCopy = list(colaListos)
  for proc in listosCopy: 
    if (fProceso.TI < proc.TI): #el proceso nuevo a cargar tiene menor tiempo de irrupción
        indice = colaListos.index(proc) 
        colaListos.insert(indice, fProceso)
        mayorTI = False
        break
  if mayorTI: 
    colaListos.append(fProceso) #lo agrego al final, pq es el que mayor TI tiene

#antes de cargar a listos, pregunto pot el tiempo actual
def CargarListos(fProceso, colaListos, colaActual):
      #se actualliza estado del proceso a listo
      #a tener en cuenta: cargar los procesos segun TI.
      # quiza deba hacer una funcion aparte para eso
  hayEspacio, fFragmentacion = CargarEnMemoria(fProceso) #retorna v o f.
  if hayEspacio:
    #cargar a listos
    AgregarAListos(fProceso, colaListos)
    #elimina de la cola anterior, porque ya se cargo a listos o suspendidos.
    EliminarDeCola(colaActual, fProceso)  #POR EL MOMENTO DEJO INACTIVO, PARA SABER SI ES ESTE EL PROBLEMA, ELIMINO AFUERA
      #con "cola actual" me refiero a la cola de la que se elimina, puede ser cola de ejecucion, de nuevos, de suspendidos.
  
  #no hay espacio: 
  elif (fProceso.estado != "suspendido"): #si es igual a suspendido es pq ya estaba en la lista de suspendidos. no hace falta volvcer a ponerlo.
    #cargar en suspendidos, solo si es que NO estaba en suspendidos
    CargarListosYSuspendidos(fProceso, colaActual)

  return fFragmentacion
  
  #si es == suspendido, no hago nada.
  #if not hayespacio: huboFragmentacion = True.
  #return huboFragmentacion



#def seleccionarProcesoSRTF(): # no hace falta porque ya esta ordenada la cola, o eso deberia. El orden se debe hacer en la cola de listos.

#ejecucion = { "enUso": False, "procEjecutandose": None, "tiempoEjecucion": 0 }
def EjecutarProceso(procActual, colaEjecucion, colaListos): #hacer
  #cambia estado a "ejecucion". Se llama a la funcion para cargar en cola de listos si es que hay otro proc en ejecucion.
  #Nota: sí, tengo que agregarlo a la cola de lsitos, pero no tengo que preguntar si hay espacio en memoria, porque el proceso ya esta asignado en memoria
  #overhead:
  if colaEjecucion["enUso"] == True: #HAY proc EJecutandose: preguntar por TI y sacar proceso
    
    procesoEjecutandose = colaEjecucion["procEjecutandose"]
    #procesoEjecutandose.TI = colaEjecucion["tiempoEjecucion"] #creo qu eesta linea no hace falta. Es para ctualizar TI, pero spone que igual se va ir restando directamente del proceso actualemnte enejecucuion
    
    if procActual.TI < procesoEjecutandose.TI: #lo saco al anterior de la cola ejecutandose
      #llamo a la funcion de agragar a listos, sin preguntar por memoria.
      AgregarAListos(procesoEjecutandose, colaListos) #aca adentro ya se actualiza su estado
      #si no entra en el if es pq el proceso Actual es igual al del ejecutandose.
      EliminarDeCola(colaListos, procActual)
      procActual.estado = "ejecutandose"
      colaEjecucion["procEjecutandose"] = procActual
      print("se expropió un proceso")
    else: 
      print("\n Un proceso intentó ejecutarse: La CPU está ocupada por un proceso con menor TI")
  #Si en este if, no entra, es pq no hay procesos ejecutandose: colaEjecucion["enUso"] == False:
  else:
      colaEjecucion["enUso"] = True
      EliminarDeCola(colaListos, procActual)
      procActual.estado = "ejecutandose"
      colaEjecucion["procEjecutandose"] = procActual
  #no pongo en else, pq en ambos casos debo asignar el proceso actual en la cola de listos

""" EliminarDeCola(colaListos, procActual)
  procActual.estado = "ejecutandose"
  colaEjecucion["procEjecutandose"] = procActual
  #colaEjecucion["tiempoEjecucion"] = procesoActual.TI #no hace falta este, creo
  #NOTA: aca se deberia hacer un print general de el estado de todos los procesos y la cola de ejecucion """


#  TR = T_fin – TA. El tiempo de fin seria el TActual en que termina
def TerminarProceso(proceso, fMemoria): #hacer
  global cantProcesos, GM
  liberadoCorrectamente, fMemoria = LiberarMemoria(proceso, fMemoria)
  if liberadoCorrectamente:
    cantProcesos -=1
    GM -= 1
    proceso.estado = "terminado"
    #calcular TR del proceso
    proceso.TR = tActual - proceso.TA #en esta funcion se "aumenta" el TR del proceso
    terminados.append(proceso)

    ejecucion["enUso"] = False
    ejecucion["procEjecutandose"] = None
    #ejecucion["tiempoEjecucion"] = 0
    print("estado del proceso terminado: antes: ",  proceso.estado) 

  else: 
      print("Hubo un error al finalizar el proceso.")

  return fMemoria, disponibleEnMemoria
 #pasarlo a cola de terminados y disminuir cant procesos. aca llamaria a la funcion LiberarMemoria

def DisminuirTI(colaEjecucion, fMemoria, disponibleEnMemoria ):
    fProceso  = colaEjecucion["procEjecutandose"]
    fProceso.TI -=1
    if fProceso.TI == 0: 
      print("\n--Terminó el proceso: ", fProceso.id)
      fMemoria, disponibleEnMemoria = TerminarProceso( fProceso, fMemoria )
      print("Estado real del proceso finalizado:", proceso.estado)
      return True, fMemoria, disponibleEnMemoria
    return False, fMemoria, disponibleEnMemoria



""" Al finalizar la simulación se deberá presentar un informe estadístico con, tiempo de retorno y espera para cada
proceso y los respectivos tiempos promedios. También deberá calcular el rendimiento del sistema para la
simulación (cantidad de trabajos terminados por unidad de tiempo)"""


def CalcularPromediosTEyTR():
  #tiempos promedios:
  #TE suma de todos los TE divido la cant de procesos
  totalProcesos = len(terminados)
  TEpromedio = 0
  TRpromedio = 0
  for p in terminados:
    TEpromedio += p.TE
    TRpromedio += p.TR

  TEpromedio = TEpromedio / totalProcesos
  TRpromedio = TRpromedio / totalProcesos
  return TEpromedio, TRpromedio


def CalcularRendimientoSistema (colaTerminados, tActual):
  totalProcTerm= len(colaTerminados)
  rendimiento = totalProcTerm / tActual
  return rendimiento
#total de trabajos terminados / periodo de tiempo (o sea: cant colaTerminados divido tActual)


def AumentarTiempo(colaListos, colaSuspendidos): #hacer
  global tActual
  #aumenta tiempo actual
  #en esta funcion, deberia tambien aumentar lso tiempos de espera, o de retorno, no se, de cada proceso
  tActual +=1
  #Aumentar tiempos de espera de cada proceso:
  for proc in colaListos:
    proc.TE += 1
  for proc in colaSuspendidos:
    proc.TE += 1

def informacion():
  print("""Este es un proyecto de la materia de Sistemas Operativos, trata de un simulador.. bla bla.."

  El archivo a ingresar puede y debe tenr la forma: ....
  Al finalizar ... etc""")
  salir = input("Para volver al menu presione 'Enter':")
  if salir == "":
    return True
  return False




#----------------------------------------------------------------------------------
#MAIN:

#declaracion de variables:

cantProcesos = 0
tActual = 0
GM = 0 # Grado de Multiprogramacion, maximo 5
fragmentacion = []


#menu: #mejorar la salida de texto
print("Bienvenido al Simulador... ETC...!")

while True:
  print("""\n------------------------------------------------------------------------
  Opciones Disponibles:
    "0. Salir: ingrese '0' para salir
    "1. Informacion (recomendable)
    "2. Comenzar Simulador
    ----------------------------------------------------------------------------------""")

  opcion = int(input("Seleccione una opción: "))
  if opcion != 1 and opcion != 2 and opcion != 0: #para controlar la entrada
    print("\n-----Ha escrito una opcion invalida----- \n")

  if opcion == 0:
    break
  elif opcion == 1:
    volverAMenu = informacion()
    if volverAMenu:
      continue

#-------------------------------------------------
  elif opcion == 2:
    print("""           > Comenzando el Simulador...
-Por favor, cargue la ruta del archivo con los procesos, en el formato: txt """)
    existe = False
    while not existe:
      archivo = input("-Cargue aquí: ")
      existe = existeArchivo(archivo)
      if not existe:
        archivo = input("""-ERROR!-Intente ingresarlo otra vez o intente con otro archivo (Ingrese '0' para volver al Menu) """)
        if archivo == "0":
          break         #REVISAR ESTO
     
    if existe:
    #Sigo con el programa, por:
    #una vez abierto el archivo:
      cargarNuevos(archivo, nuevos)
      #MOSTRAR PROCESOS CARGADOS
      """ for p in nuevos:
        print("proceso: ", p.id )
      esto era para probar si cargaba correcta,emte. Lo hace: el porblema no esta acá"""
      while cantProcesos > 0:
            #creo q aca deberia comenzar a incrementar manualemnte, o usando pop en la lista de nuevos.
        if GM < 5:
          if nuevos:
            llegoProcNuevo = False
                #...
            # list() hace una copia de la lista nuevos, esto solo lo uso para iterar, sin embargo, modifico la lista original dentro del bucle y no la copia
            for proceso in list(nuevos): #mepa q lo ideal es usar pop
              if proceso.TA <= tActual:
                fragmentacion = CargarListos(proceso, listos, nuevos) #aca se carga en listos, a memoria, o a listos y suspendidos, y se saca de la cola de nuevos
                GM += 1
                llegoProcNuevo = True #solo me interesa saber si llego un nuevo proceso, no si se cargó
                if GM >= 5:
                  break

            #if llegoProcNuevo: #una de las peticiones es mostrar la presentacion de salida cada vez que se admite un proceso
            #  PresentacionDeSalida() #lo podria poner despues de poner a ejecutar proceso
                # ↑ esto lo cambio allá abajo ↓ despues de ejecutar un proceso
          else:
            print("---Cola de Nuevos Vacia---"
                  #todo esto que viene despues se borra
            "tiempo: ", tActual,\
            "cantodad procesos:", cantProcesos, "grado multiprog: ", GM)
            print("Listos:", [p.id for p in listos])
            print("Suspendidos:", [p.id for p in listosSuspendidos])
            print("CPU ocupada:", ejecucion["enUso"])

            if ejecucion["enUso"]:
              print("Proceso ejecutándose:",
                ejecucion["procEjecutandose"].id)

            print("Memoria disponible:", disponibleEnMemoria)
            #break ACA ESTA EL PROBLEMA
            #patrece q cuando la cantidad de procesos en = 1.
             #creo q es un problema de indices. se rompe cuando cantProc = 1.

        if listos: #pregunta si la lista no esta vacia
          procesoActual = listos[0] #la lista ya esta ordenada por TI, entonces solo tomo el pimrer elemento
          if procesoActual.TA <= tActual: 
            print("----proceso actual dentro de ejecutar proc: ", procesoActual.id) #borrar
            EjecutarProceso(procesoActual, ejecucion, listos)
        else:
          print("Por el momento, no hay procesos el cola de listos para ejecutar")

        if llegoProcNuevo: #una de las peticiones es mostrar la presentacion de salida cada vez que se admite un proceso
            PresentacionDeSalida()

        AumentarTiempo(listos, listosSuspendidos)

      #Una vez aumentado el tiempo: Control de ejecucion:---------------------
#------------------------------------------------------------------------------------------------

          #ESTO SE BORRA
        print("Proceso actual:", procesoActual.id)
        print("Proceso en CPU:", ejecucion["procEjecutandose"].id)
        print("TI:", ejecucion["procEjecutandose"].TI)
        print("Estado:", ejecucion["procEjecutandose"].estado)
#---------------------------------------------------------------------------
        #finalizó la ejecucion del proceso?
        procFinalizado, memoria, disponibleEnMemoria = DisminuirTI(ejecucion, memoria, disponibleEnMemoria)  #aca dentro llamo a la funcion terminar
        if procFinalizado: #Si terminó, asigno otro proceso
          print("estado del proceso terminado: despues de Dismunuir ti", procesoActual.id, procesoActual.estado) #borrar

          if listos:
            procesoActual= listos[0] #le asigno el siguiente en la cola para ejecutar
          
            if procesoActual.TA <= tActual: #la lista ya esta ordenada por TI, por eso solo pregunto por TA
              EjecutarProceso(procesoActual, ejecucion, listos)

  #-------------termina control de ejecucion---------------

          if len(listosSuspendidos) > 0: #hay un proceso en espera de ser cargado.
            for j, p in enumerate(listosSuspendidos):
              if p.TA <= tActual:
                fragmentacion = CargarListos(p, listos, listosSuspendidos)
                #REVISAR ESTO

          PresentacionDeSalida() #mostrar cada vez que se termina un proceso
          #lo pongo a lo ultimo pq considero que en el mismo TActual se debe mover un proceso suspendido a listo

      #------finalizado el bucle, cantProcesos = 0. Hago los informes:
      print("\n                        -----El Simulador Finalizó-----")
      print ("-"* 100)
      print("\n                        -----COMENZANDO INFORMES------\n")

      TEprom, TRprom = CalcularPromediosTEyTR()
      # rendimiento = CalcularRendimientoSistema ()

      print("----Tiempos de ESPERA y RETORNO para Cada Proceso:-----\n")
      print(f"{'ID_P':<5} | {'Estado':<10} | {'T_Espera':<9} | {'T_Retorno':<10} |")
      print ("-"* 50)
      for p in terminados:
        print(f"{p.id:<5} | {p.estado:<10} | {round(p.TE):<9} | {round(p.TR):<10} |")

      print(f"""\n                ---Tiempos Promedios: ---
      
  --Tiempo de Espera Promedio: {TEprom:.1f}

  --Tiempo de Retorno Promedio:  {TRprom:.1f}""") # :.1f es para limitar los decimales

      rendimientoSistema = CalcularRendimientoSistema(terminados, tActual)

      print(f"""\n           ----Rendimiento del Sistema: ----

---Rendimiento: {rendimientoSistema:.1f} trabajos terminados por unidad de tiempo
(-Total de Procesos Terminados respecto del Tiempo Transcurrido)
""")
      print("\n                               -------Fin De INFORMES-------\n")


      print("---------------------------------Gracias por usar el Simulador!-------------------------------------\n")


      break

  

        



        






  






    


