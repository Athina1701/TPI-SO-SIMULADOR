# Simulador de Sistemas Operativos

Trabajo práctico universitario en Python. Simula planificación de CPU **SRTF**
y administración de memoria **Best Fit**, con particiones variables. Incluye un
dashboard oscuro con CustomTkinter y el menú tradicional por consola.

## Requisitos e instalación

- Python **3.12 o posterior**, con Tkinter. Se verificó con Python 3.13 en Windows.
- CustomTkinter 5.2.2; sus dependencias se instalan mediante `pip`.
- No se agregaron bibliotecas de animación ni dependencias de pruebas.

Desde la carpeta del proyecto, en la terminal PowerShell de VS Code:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Si se utiliza Python 3.12, reemplazar `-3.13` por `-3.12`. No es necesario activar
el entorno ni modificar la política de PowerShell.
En VS Code: `Ctrl+Shift+P` → **Python: Select Interpreter** → seleccionar
`.venv\Scripts\python.exe`.

## Ejecución

Interfaz gráfica:

```powershell
.\.venv\Scripts\python.exe main_gui.py
```

Consola tradicional, incluida la entrada manual y el guardado de procesos:

```powershell
.\.venv\Scripts\python.exe simulador_equipo2.py
```

También se puede abrir `main_gui.py` y seleccionar **Run Python File in Terminal**,
con el intérprete del entorno virtual.

## Carga manual desde la interfaz

En el panel de controles, seleccionar **Cargar procesos manualmente**. Completar
ID, TA, TI y tamaño en KB y pulsar **Agregar proceso**. La tabla conserva el orden
de ingreso y muestra un contador de hasta diez procesos. Las reglas de validación
son las mismas que utiliza la carga de archivos; los errores aparecen dentro de
la ventana y conservan los campos ingresados.

Seleccionar una fila para **Editar seleccionado** o **Eliminar seleccionado**.
Al editar, pulsar **Guardar cambios** o **Cancelar edición**. La edición conserva
la posición original. **Limpiar lista** solicita confirmación.

**Usar estos procesos** prepara la simulación sin crear archivos; luego se utiliza
**Iniciar** en el dashboard. **Reiniciar** restaura la lista utilizada, aunque se
haya modificado después el borrador manual. Cerrar el editor conserva el borrador
y no cambia la simulación actual. La carga de otra lista se habilita cuando la
simulación no está ejecutándose.

Opcionalmente, **Guardar como TXT** exporta la tabla en orden de ingreso con el
formato `ID TA TI tamaño`, compatible con la carga tradicional. Solicita confirmación
antes de sobrescribir. Para exportar, los ID no deben contener espacios ni comas,
porque son separadores del formato; esos identificadores sí pueden utilizarse
directamente para simular. Guardar no es necesario para utilizar la lista.

## Archivos de procesos

Cada línea contiene `ID TA TI tamaño`. Se aceptan espacios, tabulaciones o comas.
Las líneas vacías se ignoran y no se incluyen encabezados. Un mismo registro debe
utilizar uno de esos formatos, sin mezclarlos.

```text
P1 0 5 100
P2,1,2,80
P3 4 3 200
```

| Campo | Significado |
|---|---|
| ID | Identificador del proceso. |
| TA | Tiempo de arribo. |
| TI | Duración original de la ráfaga de CPU. |
| tamaño | Memoria requerida, en KB. |

El identificador debe ser un texto no vacío y único entre los procesos aceptados
(la comparación distingue mayúsculas y minúsculas). Se recortan los espacios de
los campos. TA, TI y tamaño deben ser enteros; TA debe ser no negativo, TI positivo
y el tamaño debe estar entre 1 y 450 KB, ambos inclusive.

Los archivos nuevos se guardan en **UTF-8**, tanto desde la consola como desde
la interfaz. Se leen archivos UTF-8 con o sin BOM; si el texto no es UTF-8 válido,
se intenta Windows-1252 para conservar la compatibilidad con archivos anteriores.
Esta alternativa no detecta cualquier codificación: otros formatos deben convertirse
a UTF-8. Los identificadores con `ñ`, `á`, `é` y `ü` se conservan al guardar y cargar.

Se cargan como máximo **diez registros válidos en orden de lectura** y después se
ordenan por TA y TI. Los inválidos se rechazan y no ocupan un lugar ni reservan su
identificador. Tras aceptar diez procesos, los demás registros no vacíos se cuentan
como **no procesados por límite**, con su línea original, sin validarlos ni contarlos
como errores. Las líneas vacías se omiten conservando la numeración original.

### Informe de carga

Ante rechazos, registros sin procesar o ausencia de procesos válidos se abre un
informe azul, desplazable, de solo lectura y no modal. Muestra el formato
`ID TA TI tamaño`, los identificadores aceptados y los conteos de aceptados,
rechazados y no procesados. Cada rechazo incluye línea original, ID recuperable
y todos los motivos específicos. Un registro con varios problemas cuenta como
un solo rechazo. El informe completo no se recorta al límite del panel de eventos.

Se permite ejecutar solo los procesos aceptados, incluso con el informe abierto.
Si no hay válidos, se limpia la simulación anterior y se deshabilitan inicio y avance.
Cancelar el selector o no poder leer un archivo conserva la carga anterior; los
errores de lectura se explican en español, sin exponer excepciones de Python.

Consola y ventana usan el mismo cargador y `validarRegistro()`. La inicialización
por API aplica esa misma validación antes de modificar el estado; una carga inválida
no se aplica parcialmente. Los algoritmos y las métricas no se modificaron.

El archivo `tests/lotes/validos_invalidos.txt` combina **5 procesos aceptados y
13 registros rechazados**, con líneas vacías, diferentes separadores y todos los
motivos de validación. Puede abrirse directamente desde la ventana.

`procesos.txt` es el ejemplo del proyecto. Los seis lotes del PDF están disponibles,
sin cambios de orden, en `tests/lotes/lote1.txt` a `lote6.txt`; pueden abrirse desde
la ventana. El lote 5 descarta el proceso de 451 KB; el lote 6 tiene doce registros
y solo se cargan los primeros diez.

## Controles

| Control | Comportamiento |
|---|---|
| Cargar archivo | Previsualiza procesos y prepara una simulación con reloj cero. Disponible con reproducción detenida. |
| Iniciar | Comienza la reproducción automática desde preparado. |
| Pausar | Detiene la reproducción; los paneles ya reflejan la última iteración calculada. |
| Continuar | Reanuda desde el mismo estado. |
| Avanzar 1 unidad | Ejecuta una iteración y actualiza los paneles inmediatamente, sin esperas visuales. |
| Reiniciar | Cancela callbacks y prepara nuevamente el archivo cargado; borra resultados, eventos e historial del Gantt. |
| Velocidad | Ajusta la reproducción entre 0,25× y 4×, sin cambiar resultados ni el tamaño del paso lógico. |

A 1× se intenta avanzar una unidad por segundo. Solo el intervalo de reproducción
automática marca el ritmo: no hay esperas por destellos, resaltados ni transiciones.
La velocidad depende también de la carga gráfica; no representa una medición de tiempo real.
La ventana y los paneles permiten desplazamiento cuando no entra toda la información.

## Reglas conservadas

**SRTF:** los listos se ordenan por tiempo de CPU restante. La expropiación ocurre
solo ante un TI estrictamente menor. Ante igualdad no se expropia y se conserva
el orden de inserción. Los arribos simultáneos se ordenan por TA y luego TI.

**Best Fit:** se selecciona el menor hueco libre suficiente, mediante ordenamiento
estable por tamaño. El sobrante se convierte en otra partición libre. Al liberar,
se fusionan las entradas libres consecutivas; no se desplazan procesos ni se compacta.
Hay **450 KB de usuario** y **100 KB reservados al sistema operativo**.

**Multiprogramación:** máximo de cinco procesos entre listos, suspendidos y CPU.
Un proceso admitido sin hueco suficiente queda suspendido. Los suspendidos se
reintentan después de una finalización y de la selección del siguiente listo.

Cada iteración conserva este orden: admisiones, selección o expropiación,
presentación correspondiente, avance de reloj y TE, consumo de una unidad de CPU,
finalización, nueva selección y reintento de suspendidos. Puede haber selecciones
transitorias que no consumen CPU.

Las estadísticas se obtienen de las funciones del motor:

- **TR:** tiempo desde el arribo hasta la finalización: `TR = finalización − TA`.
- **TE:** `tiempo en Listos + tiempo en Listos/Suspendidos`. No aumenta en
  Nuevos, Ejecución ni Terminado. Excluir Nuevos es una decisión del equipo;
  por ese motivo no siempre coincide con `TR − TI original`.
- **Rendimiento:** procesos terminados divididos por tiempo total simulado,
  incluida la inactividad de CPU.

## Visualizaciones

- **RAM:** bloques proporcionales y colores estables por proceso. El dibujo y la
  tabla muestran inmediatamente las particiones reales del motor después de cada
  paso, incluidas asignaciones, divisiones, liberaciones y fusiones. El SO ocupa
  el tramo 450–550 KB. Se reutilizan los elementos de Canvas, sin efectos temporales.
- **CPU:** proceso seleccionado, tiempo restante e indicador estático de ocupación.
  Los avisos textuales conservan las selecciones y expropiaciones reales, sin pulsos
  ni transiciones de iluminación.
- **Colas:** tarjetas con colores consistentes que reflejan inmediatamente los cambios
  de estado. No se resaltan temporalmente ni se retrasa la reproducción para mostrarlas.
- **Gantt:** utiliza exclusivamente `ejecucion_cpu` para tramos ocupados. Si no
  hubo ese evento durante una unidad realmente avanzada, se registra CPU libre.
  Las selecciones y expropiaciones no crean intervalos. Se unen tramos contiguos
  del mismo proceso y se conserva todo el historial, con desplazamiento horizontal.
  Al señalar un bloque se muestran inicio, fin y duración.
- **Eventos y estadísticas:** secuencia y tiempo de cada evento; tablas con columnas
  y barras de desplazamiento; métricas en tarjetas y detalle por proceso.
  El registro textual conserva las últimas 600 líneas; ese límite no recorta el Gantt.

La reproducción automática usa `after()` con un intervalo independiente del reloj
simulado. RAM, CPU, colas y Gantt se actualizan sin temporizadores decorativos. No hay `sleep()` ni hilos de trabajo. Solo se permite una simulación por
proceso, porque el motor conserva su estado global original.

## Organización

| Archivo | Responsabilidad |
|---|---|
| `simulador_equipo2.py` | Modelo, algoritmos, estado, consultas, eventos y consola. |
| `interfaz.py` | Ventana, controles, tablas y actualización directa de CPU y colas. |
| `memoria_visual.py` | Dibujo incremental e inmediato del estado de RAM. |
| `visualizaciones.py` | Historial completo y dibujo incremental de Gantt. |
| `main_gui.py` | Inicio de la aplicación gráfica. |
| `tests/` | Pruebas automatizadas y los seis archivos de lotes. |

La ventana usa `cargarProcesosArchivo()`, `iniciarSimulacion()`,
`ejecutarIteracion(mostrarConsola=False)`, `obtenerEstado()`, `obtenerEventos()`
y `reiniciarSimulacion()`. Las consultas devuelven copias independientes.
`ejecutarIteracion()` sin argumentos conserva la presentación por consola.

## Pruebas

Sin abrir ventanas:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Las 27 pruebas gráficas se omiten explícitamente en ese modo. Para ejecutar
la suite completa desde una sesión de escritorio:

```powershell
$env:SIMULADOR_PRUEBAS_GUI = "1"
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
Remove-Item Env:SIMULADOR_PRUEBAS_GUI
```

La suite contiene 96 pruebas mediante `unittest`. Comprueba los seis lotes por
API, menú y ventana; secuencias de CPU, asignaciones y métricas individuales;
casos pequeños con resultados calculados manualmente; invariantes de memoria y
colas; consultas independientes; orden de eventos; controles de velocidad a 0,25×,
1× y 4×; pasos consecutivos sin temporizadores de efectos; reinicios; controles;
tablas; redimensionado; Gantt e inactividad.
Las entradas con TI no positivo se rechazan antes de simular. También se prueban
los informes de hasta 650 errores, los números de línea y la inicialización sin
cambios parciales ante datos inválidos.
La carga manual se verifica mediante ventanas reales: altas, validaciones, límite,
ediciones, bajas, confirmaciones, reinicio y exportación/recarga. Se comparan todos
los estados y eventos de los seis lotes entre la carga manual y la carga desde TXT.
También se verifica la liberación del proceso con ID `None`, el reintento del
menú ante texto no numérico, la compatibilidad de codificaciones, la exportación
con acentos desde consola y ventana, y los mensajes ante errores de guardado
y simulación.

Una comprobación de optimización verifica que cien redibujados estables de RAM
no crean elementos nuevos de Canvas. Mide trabajo evitado, no FPS.

Resultados de referencia conservados:

| Lote | Terminados | Tiempo final | TE promedio | TR promedio | Rendimiento |
|---|---:|---:|---:|---:|---:|
| 1 | 5 | 22 | 0,4 | 2,6 | 0,227273 |
| 2 | 5 | 56 | 14 | 25,2 | 0,089286 |
| 3 | 8 | 55 | 12,125 | 19,375 | 0,145455 |
| 4 | 10 | 56 | 9,5 | 15,9 | 0,178571 |
| 5 | 2 | 9 | 1,5 | 6 | 0,222222 |
| 6 | 10 | 45 | 11,3 | 19,3 | 0,222222 |

## Alcance y limitaciones conocidas

La validación de archivos ya rechaza TI no positivo, TA negativo, tamaños fuera
de rango e identificadores vacíos o duplicados. Estas correcciones corresponden
solo a la entrada de datos y a la inicialización; las reglas de SRTF, Best Fit y
las fórmulas permanecen intactas. Las funciones internas de bajo nivel requieren
procesos válidos y no deben utilizarse para eludir el cargador o la inicialización.

El criterio de TE está confirmado: P8 del lote 3 tiene TE=6; los tres tiempos
adicionales transcurridos en Nuevos forman parte de TR, pero no de TE. Esta
diferencia es intencional y no constituye un error pendiente.

El menú informa las opciones no numéricas y permite reintentarlas sin cerrar el
programa. Los fallos de guardado y los errores internos de simulación se informan
con mensajes en español, sin mostrar el texto técnico de las excepciones.

Se conserva un efecto de presentación: `MostrarMemoria()` ordena la lista original
por dirección y puede influir en empates de Best Fit. El modo silencioso ejecuta
esa operación y captura el texto; no la omite. Separarla completamente requeriría
mantener explícitamente ese orden y repetir las referencias.

Los avisos de fragmentación describen los huecos insuficientes del intento actual,
no una estadística histórica. Los promedios requieren procesos terminados y el
rendimiento requiere tiempo positivo; la ventana comprueba esas condiciones.

La cobertura no abarca todas las entradas posibles. No se verificaron Linux/macOS,
todas las escalas de DPI ni simulaciones de millones de unidades. La apariencia y
fluidez dependen del equipo. Los registros rechazados se informan explícitamente;
no se introdujeron cambios algorítmicos.
