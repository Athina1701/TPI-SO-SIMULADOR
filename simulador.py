
#ARCHIVO PRINCIPAL: simulador.py 
#Version Limpiada. Dejé el archivo anterior por si tienen dudas con alguna funcion o cualquier otra cosa. Puede ver los comentarios 

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
ejecucion = { "enUso": False, "procEjecutandose": None }


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
    #Cargar procesos
      for linea in archi:
        linea = linea.strip() #NOTA: NO SE COMO VAN A CARAGR LSO PROCESOS EN EL RCHIVO. VOY A TENR QUE HACER UN AFUNCION QUE ANALICE LA LINEA DE ARCHIVO
        if linea: 
          # El proces deberia estar cargado en archivo como: id,TA,TI,memoria.
          linea = linea.split(",")
          procesoNuevo = Proceso(linea[0], int(linea[1]), int(linea[2]), int(linea[3]), "nuevo")
          colaNuevos.append(procesoNuevo) 
          cantProcesos += 1  
          if cantProcesos >= 10: #vigila que no se pase de 10 proc.
            print("Se ha llegado al limite de procesos a cargar. Cantidad actual: ", cantProcesos)
            break
        else: 
          continue #esto por si hay un renglon vacio.
    #Ordenar cola de procesos, segun tiempo de arribo.
    colaNuevos.sort(key=attrgetter("TA", "TI"))

def EliminarDeCola(cola, proceso): #recibe la cola y el proceso a eliminar.
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
    print("-" * 49)
    for p in cola:
        print(f"| {p.id:<5} | {p.TA:>4} | {p.TI:>4} | {p.tamano:>10} | {p.estado:<10} |")


def MostrarMemoria(fMemoria, fragmentacion):
  print(f"| {'ID_Particion':<12} | {'Comienzo':^4} | {'Tamaño KB':^8} | {'Proceso Asignado':^16} |")
  print("-" * 60)
  print(f"| {'Par_0':<12} | {'450':^8} | {'100':^9} | {' SIST. OPERATIVO':^16} |")
  fMemoria.sort(key=itemgetter("comienzo")) 
  for part in fMemoria:
    pAsignado = part["procesoAsignado"]
    if pAsignado is None:
      pAsignado = "Libre"
    print(f"| Par_{part["id"]:<8} | {part["comienzo"]:^8} | {part["tamanio"]:^9} | {pAsignado:^16} |")
  print(">Cantidad restante disponible en memoria: ", disponibleEnMemoria, "\n")

  if fragmentacion: 
    MostrarFragmentacion(fragmentacion)


def PresentacionDeSalida(): #muestro todas las colas
  print("\n\n             -------- TIEMPO ACTUAL: ", tActual, " ---------\n")
  print(" >Cantidad de Procesos Faltantes a terminar: ", cantProcesos)
  print(" >Grado De Multiprogramación: ", GM, "\n")

  #Mostrar Memoria-----------------------------------------------------------------
  print("\n-----Tabla de PARTICIONES de MEMORIA-----")
  MostrarMemoria(memoria, fragmentacion)

  #-------------------------------------------------------------------------
  print("\n-----Cola de Procesos NUEVOS-----")
  print(f"| {'ID_P':<5} | {'TA':^4} | {'TI':^4} | {'Tamaño KB':^10} | {'Estado':<10} |")
  print("-" * 49)
  for p in nuevos:
    #if p.TA <= tActual:
    print(f"| {p.id:<5} | {p.TA:>4} | {p.TI:>4} | {p.tamano:>10} | {p.estado:<10} |")
#---------------------------------------------------------------------------
  texto = "\n-----Cola de Procesos LISTOS-----"
  MostrarCola(listos, texto)
  texto = "\n-----Cola de Procesos LISTOS y SUSPENDIDOS-----"
  MostrarCola(listosSuspendidos, texto)
  #-------------------------------------------------------------------------
  if terminados: 
    texto = "\n-----Cola de Procesos TERMINADOS-----"
    print(texto)
    print(f"| {'ID_P':<5} | {'TA':^4} | {'TI':^4} | {'Tamaño KB':^10} | {'Estado':<10} |")
    print("-" * 49)
    for p in terminados:
        print(f"| {p.id:<5} | {p.TA:>4} | {p.resguardoTI:>4} | {p.tamano:>10} | {p.estado:<10} |")

  #Mostrar cola de Ejecucion------------------------------------------------
  print("\n-----Estado del PROCESADOR Actualmente-----\n")
  print(f"| {'Proceso Ejecutandose':^20} | {'Tiempo de Irrupción':^19} | ")
  print("-" * 46)
  if ejecucion["enUso"] == True:
    pEjecutandose = ejecucion["procEjecutandose"]
    print(f"| {pEjecutandose.id :^20} | {pEjecutandose.TI :^19} |\n")
  else: 
    print(f"| {'Ninguno':^20} | {'0':^19} |\n")
    print("\n>(Actualmente no hay procesos ejecutandose)--\n")
  print("-" * 100 , "\n")


#--------------------------MEMORIA-------------------------------------
# La memoria se maneja como una lista de diccionarios:
memoria = [ { "id": 1, "comienzo": 0, "tamanio": 450, "procesoAsignado": None } , ]
contadorIDparticion = 2
disponibleEnMemoria = 450
#----------------------manejo de memoria-----------------------
def CargarEnMemoria(fproceso):
  global disponibleEnMemoria, contadorIDparticion
  fFragmentacion= [] #cada vez que se intente cargar un proceso: puede o no haber fragmentacion
  longitudMemoria = len(memoria) 
  if longitudMemoria > 0:
    memoria.sort(key=itemgetter("tamanio")) #ordeno la lista para hacer ASIGNACION BEST FIT
    
    for i in range(longitudMemoria):
      if memoria[i].get("procesoAsignado") is None:
        if fproceso.tamano <= memoria[i].get("tamanio"):
            sobraEspacio = memoria[i].get("tamanio") - fproceso.tamano # si hay fragmentacion interna al asignar el proceso, creo otra particion
            disponibleEnMemoria =  disponibleEnMemoria - fproceso.tamano 
            if sobraEspacio > 0:
              particionNueva = { "id": (contadorIDparticion), "comienzo": memoria[i].get("comienzo") + fproceso.tamano, "tamanio": sobraEspacio , "procesoAsignado": None }
              memoria.append(particionNueva)
              contadorIDparticion += 1

            memoria[i]["tamanio"] = fproceso.tamano
            memoria[i]["procesoAsignado"] = fproceso.id            
            return True, fFragmentacion #True: proceso cargado.
        else: #no ingresó porque la particion era pequeña:
          fFragmentacion.append(memoria[i]) 
        
    return False, fFragmentacion 

def MostrarFragmentacion(fFragmentacion):
  fragTotal = 0
  print("---Hubo FRAGMENTACIÓN en las particiones: ")
  for part in fFragmentacion:
    print(f"      -Particion: {part["id"]} ; Tamaño: {part["tamanio"]}")
    fragTotal += part["tamanio"]
  print("---Fragmentacion Externa total en la memoria: ", fragTotal, ", en el Tiempo = ", tActual, "\n")


def JuntarParticiones(fmemoria):
  #ACLARACION: esta funcion NO COMPACTA espacios libres. Esta por una cuestion tecnica de como se maneja la memoria en nuestro codigo: 
  #Por cada proceso que se guarda en memoria se crea un nuevo diccionario, cuando el proceso se desasigna, el diccionario queda LIBRE, y se junta SOLO si el siguiente diccionario LIBRE es sucesivo en memoria al anterior (o sea: PART 1: Comienzo: 50, tamaño:50 → Si PART 2: comienzo: 100, y esta libre; se unen.) Asi un proceso mas grande, que la particion antes de juntarse, puede usar el espacio disponible """
  memoriaCopy = [] 
  longitudMemoria = len(fmemoria) 
  if longitudMemoria > 1: 
    fmemoria.sort(key=itemgetter("comienzo"))  #Ordeno segun direccion de inicio de cada particion, para facilitar.
    i = 0
    while i < longitudMemoria:  
      particionNueva = fmemoria[i].copy()
      if fmemoria[i].get("procesoAsignado") is None and (i < (longitudMemoria -1)): #particion actual libre?→ Si → Entonces me fijo las siguientes.
        while ( i+1 < longitudMemoria) and (fmemoria[i+1].get("procesoAsignado") is None) : #si da True, es pq puedo unirlas
          particionNueva["tamanio"] += fmemoria[i +1].get("tamanio")
          i += 1
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
      print("> Se expropió un proceso. \n")
    else: 
      print("\n> Un proceso intentó ejecutarse: La CPU está ocupada por un proceso con menor TI")
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
    print("estado del proceso terminado: antes: ", proceso.id,  proceso.estado) 

  else: 
      print("Hubo un error al finalizar el proceso.")

  return fMemoria, disponibleEnMemoria
 #pasarlo a cola de terminados y disminuir cant procesos. aca llamaria a la funcion LiberarMemoria

def DisminuirTI(colaEjecucion, fMemoria, disponibleEnMemoria ):
    fProceso  = colaEjecucion["procEjecutandose"]
    fProceso.TI -=1
    if fProceso.TI == 0: 
      print(f"\n>Terminó el proceso: {fProceso.id} (Tiempo = {tActual}) ")
      fMemoria, disponibleEnMemoria = TerminarProceso( fProceso, fMemoria )
      return True, fMemoria, disponibleEnMemoria
    return False, fMemoria, disponibleEnMemoria


def CalcularPromediosTEyTR():
  #tiempos promedios:
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
  rendimiento = totalProcTerm / (tActual)
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
procesoActual = None


#menu: #mejorar la salida de texto
print("Bienvenido al Simulador... ETC...!") #la idea es agregar: breve descripcion de lo q es el simu, Nro de grupo e integrantes

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
    volverAMenu = informacion() #en info: ampliar detalles del simu, explicar las abreviaciones, quiza explicar como cargar el archivo y que formato de procesos admite
    if volverAMenu:
      continue

#-------------------------------------------------
  elif opcion == 2:
    print("""\n           > COMENZANDO EL SIMULADOR...
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
      print("\n>>> Archivo Procesado Correctamente <<<\n")
      cargarNuevos(archivo, nuevos)
      print(">" * 100)
      #Muestro los procesos cargados:
      texto = "\n---- Procesos En El Archivo Cargados Al Simulador: ----\n"
      MostrarCola(nuevos, texto)
      print(">" * 100)
      
      while cantProcesos > 0:
        llegoProcNuevo = False 
        if GM < 5:
          if nuevos:
            for proceso in list(nuevos): 
              if proceso.TA <= tActual:
                fragmentacion = CargarListos(proceso, listos, nuevos) 
                GM += 1
                llegoProcNuevo = True 
                if proceso.TA == tActual:
                  print(f"\n > Llegó un NUEVO proceso: {proceso.id}. (Tiempo Actual = {tActual} )")
                else: 
                  print(f"\n > Se admitió un proceso de Cola de Nuevos: {proceso.id}. (Tiempo Actual = {tActual} )")
                if GM >= 5:
                  break
          else:
            print("---Cola de Nuevos Vacia---")

            if ejecucion["enUso"]:
              print(f"> Proceso ejecutándose: {ejecucion["procEjecutandose"].id} (Tiempo Actual = {tActual} ) ") #borrar

        if listos:
          procesoActual = listos[0] #la lista ya esta ordenada por TI, entonces solo tomo el pimrer elemento
          if procesoActual.TA <= tActual: 
            EjecutarProceso(procesoActual, ejecucion, listos)
        else:
          print("--Por el momento, no hay procesos en cola de listos para ejecutar--")

        if llegoProcNuevo:
          PresentacionDeSalida()

        AumentarTiempo(listos, listosSuspendidos)
#--------------------Una vez aumentado el tiempo: Control de ejecucion:-------------------------------------------------
        #finalizó la ejecucion del proceso?
        procFinalizado, memoria, disponibleEnMemoria = DisminuirTI(ejecucion, memoria, disponibleEnMemoria) 
        if procFinalizado:
          if listos:
            procesoActual= listos[0] #Siguiente proceso a ejecutar
            if procesoActual.TA <= tActual:
              EjecutarProceso(procesoActual, ejecucion, listos)
          else:
            print("--Por el momento, no hay procesos en cola de listos para ejecutar--")
  #-----------------------Termina control de ejecucion---------------

          for p in list(listosSuspendidos): #hay un proceso suspendido en espera de ser cargado.
            fragmentacion = CargarListos(p, listos, listosSuspendidos)

          if cantProcesos == 0:
            print("\n\n               >>> Estado Final del Simulador <<<")
          #ahora que noto, vuelvo a mostrar todo per aumenta el tiempo tambien, entonces cuando hago el calculo de promedios me calcula con un tiempo extra. en vez de ser cantProc / tActual con Tactual siendo el tiempo que terminó el utlimo proceso, hace con tActual +1
          PresentacionDeSalida() #mostrar cada vez que se termina un proceso
          #lo pongo a lo ultimo pq considero que en el mismo TActual se debe mover un proceso suspendido a listo

      #------finalizado el bucle, cantProcesos = 0. Hago los informes:
      print("\n                        -----El Simulador Finalizó-----")
      print ("-"* 100)
      print("\n                        ------COMENZANDO INFORMES------\n")

      TEprom, TRprom = CalcularPromediosTEyTR()
      rendimientoSistema = CalcularRendimientoSistema(terminados, tActual)


      print("----Tiempos de ESPERA y RETORNO para Cada Proceso:-----\n")
      print(f"{'ID_P':<5} | {'Estado':<10} | {'T_Arribo':<9} | {'T_Espera':<9} | {'T_Retorno':<10} |")
      print ("-"* 50)
      terminados.sort(key=attrgetter("TA"))
      for p in terminados:
        print(f"{p.id:<5} | {p.estado:<10} | {p.TA:<9} | {round(p.TE):<9} | {round(p.TR):<10} |")

      print(f"""\n                --- Tiempos Promedios: ---
      
>--Tiempo de Espera Promedio: {TEprom:.1f}

>--Tiempo de Retorno Promedio:  {TRprom:.1f}""") # :.1f es para limitar los decimales

      print(f"""\n           ---- Rendimiento del Sistema: ----

>-Rendimiento: {rendimientoSistema:.1f} trabajos terminados por unidad de tiempo
 (Total de Procesos Terminados respecto del Tiempo Transcurrido)
""")
      print("""\n                               -------Fin De INFORMES-------
                              Gracias por usar el Simulador!\n""")
      print("-" * 100)
      break

  

        



        






  






    


