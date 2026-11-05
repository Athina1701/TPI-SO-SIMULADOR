"""dispoMemoria = 450

print("antes: ", dispoMemoria)

def cambiar(dispoMemoria):
    dispoMemoria -= 100
    print("durante: ", dispoMemoria)


cambiar(dispoMemoria)
print("despues: ", dispoMemoria)
"""
dispoMemoria = [450, 50, 100]

print("antes: ", dispoMemoria)

def cambiar(dispoMemoria):
    dispoMemoria[2] -= 100
    print("durante: ", dispoMemoria)


cambiar(dispoMemoria)
print("despues: ", dispoMemoria)
