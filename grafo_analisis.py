from music21 import *
import tkinter as tk
from tkinter import filedialog
import auxiliares
import csv
import json
from copy import deepcopy


class NodoAnalisis:
    elementos = []
    formaPrima = []
    nombreForte = ""
    vectorIntervalico = []
    disposicion = []
    permutacion = []
    id = 0
    posicion_en_lista = []
    set_class = ""
    # posiblemente eliminables después
    entrada = []
    salida = []

    def __init__(self, conjunto, ident):
        """
        inicialización del conjunto nodo
        :param conjunto: objeto acorde de music21
        :param ident: identidad asignada después de verificar que no existe
        """
        if type(conjunto) is list:
            a = chord.Chord(conjunto)
            conjunto = a
        self.disposicion = []
        self.permutacion = []
        self.elementos = conjunto.normalOrder
        self.formaPrima = conjunto.primeForm
        self.nombreForte = conjunto.forteClass
        self.vectorIntervalico = conjunto.intervalVector
        self.id = ident
        self.set_class = conjunto.forteClassTnI
        self.convertir_disposicion(conjunto)

    def convertir_disposicion(self, elementos):
        """
        Toma los elementos de un conjunto en formato de acorde de music21 y 
        los convierte en la disposición en alturas (númericas) y la permutación (clases de altura)
        :param elementos: elemento music21
        :return: null, afecta directamente los atributos disposión y permutación
        """
        conjunto = auxiliares.convertir_a_midi(elementos)
        self.disposicion.append(conjunto)
        self.permutacion.append(auxiliares.convertir_a_permutacion(conjunto))

    def asignar_entrada(self, ident):
        """
        este procedimiento ingresa la identidad del acorde anterior, ha de ser usado en el mecanismo de generación del 
        grafo.
        :param ident: identidad 
        :return: null
        """
        self.entrada.append(ident)

    def asignar_salida(self, ident):
        """
        este procedimiento ingresa la identidad del acorde posterior, ha de ser usado en el mecanismo de generación del
        grafo.
        :param ident: identidad
        :return: null
        """
        self.salida.append(ident)


class MatrizAuxiliar:

    id = 0
    matriz = []
    nombre = ""

    def __init__(self, ident, matriz, nombre):
        self.id = ident
        self.matriz = matriz
        self.nombre = nombre


class GrafoAnalisis:
    # el listado es un arrelgo de acordes en formato music21
    listado = []
    # archivo es la referencia al archivo xml
    archivo = 0
    # es el conjunto de vértices que se crean para el grafo
    vertices = []
    # es un arreglo paralelo a listado con la referencia a los vértices. se usa para crear las matrices
    referencias = []
    # listado de aristas
    aristas_base = []
    # la matriz de incidencia
    matriz_incidencia = []
    # la matriz de adyacencia
    matriz_adyacencia = []
    # arreglo de matrices auxiliares
    matrices_aux = []

    def __init__(self):
        self.listado = []
        self.archivo = 0
        self.vertices = []
        self.referencias = []
        self.aristas_base = []
        self.matriz_incidencia = []
        self.matriz_adyacencia = []
        self.matrices_aux = []

    def cargar_archivo(self):
        """
        Este procedimiento abre una ventana de diálogo para cargar un archivo xml con la sucesión de acordes a analizar
        :return: null
        """
        root = tk.Tk()
        root.withdraw()
        ruta = filedialog.askopenfilename()
        if ruta != '':
            try:
                self.archivo = converter.parse(ruta)
                a = self.archivo.flat.chordify()
                self.listado = a.flat.notes.stream()
            except ValueError:
                print("no es un tipo de archivo válido")
        else:
            print("no se cargó archivo alguno")

    def generar_nodo(self, listado, index):
        """
        genera un nodo nuevo
        :param listado: es un objeto music21 que sirve para derivar las informaciones de los nodos
        :param index: es el índice que da identidad al conjunto
        :return: null
        """
        vertice = NodoAnalisis(listado, index)
        self.vertices.append(vertice)

    def confirmar_inclusion(self, conjunto):
        """
        confirma si el conjunto ya fue incluido
        :param conjunto: conjunto a comparar
        :return: -1 si no existe el nodo, si existe devuelve el índice que lo identifica 
        """
        if type(conjunto) == list:
            conjunt = chord.Chord(conjunto)
            conjunto = conjunt
        respuesta = -1
        set_compare = conjunto.normalOrder
        for k in range(len(self.vertices)):
            if set_compare == self.vertices[k].elementos:
                respuesta = k
                break
        return respuesta

    def generar_aristas_base(self):
        """ recorre el listado de referencias para construir un listado de aristas
        :return: 
        """
        arista = []
        longitud = len(self.referencias) - 1
        for k in range(longitud):
            if k < longitud:
                arista = [self.referencias[k], self.referencias[k+1]]
            self.aristas_base.append(arista)

    def generar_matriz_adyacencia_d(self):
        """ crea la matriz de adyacencia como grafo dirigido
        :return: null
        """
        # no he considerado los loops hacia el mismo nodo. Vi en WIKI que puede ser 2 asignado en loops, pero en el de
        # discretas es un 1, por otro lado, como tengo multigrafos como posibilidad, tal vez deba sumar si aparece de
        # nuevo la relación, entonces tocaría modificar esto.
        self.matriz_adyacencia = []
        for k in range(len(self.vertices)):
            row = []
            for j in range(len(self.vertices)):
                pareja = [self.vertices[k].id, self.vertices[j].id]
                if pareja in self.aristas_base:
                    row.append(1)
                else:
                    row.append(0)
            self.matriz_adyacencia.append(row)

    def generar_matriz_incidencia(self):
        """ Crea la matriz de incidencia
        :return: null
        """
        self.matriz_incidencia = []
        for k in range(len(self.vertices)):
            row = []
            for j in range(len(self.aristas_base)):
                if self.vertices[k].id in self.aristas_base[j]:
                    if self.vertices[k].id == self.aristas_base[j][0]:
                        row.append(-1)
                    else:
                        row.append(1)
                else:
                    row.append(0)
            self.matriz_incidencia.append(row)

    def generar_grafo(self):
        """
        Una vez cargado el archivo, este procedimiento recorre el listado de acordes para convertirlos en objetos 
        conjunto sobre los cuales se harán las operaciones
        :return: null
        """
        contador = 0
        for j in range(len(self.listado)):
            respuesta = self.confirmar_inclusion(self.listado[j])
            if respuesta == -1:
                self.generar_nodo(self.listado[j], contador)
                self.referencias.append(contador)
                contador = contador + 1
            else:
                self.vertices[respuesta].convertir_disposicion(self.listado[j])
                self.referencias.append(respuesta)
        self.generar_aristas_base()
        self.generar_matriz_adyacencia_d()
        self.generar_matriz_incidencia()
        print("se generaron " + str(len(self.vertices)) + " vértices")

    def agregar_nodo(self, conjunto):
        """
        Este método permite agregar nodos manualmente cuando no se pueden agregar directamente desde music XML
        :param conjunto: listado de alturas en formato MIDI 
        :return: null
        """
        acorde = chord.Chord(conjunto)
        self.listado.append(acorde)

    def agregar_arista(self, partida, final):
        """
        Agregar una relación que no es consecutiva en el archivo XML
        :param partida: vértice de inicio
        :param final: vértice destino
        :return: null
        """
        flag1 = False
        flag2 = False
        for iterador in range(len(self.vertices)):
            if self.vertices[iterador].id == partida:
                flag1 = True
        for iterador in range(len(self.vertices)):
            if self.vertices[iterador].id == final:
                flag2 = True
        if flag1 and flag2:
            self.aristas_base.append([partida, final])
            self.generar_matriz_adyacencia_d()
            self.generar_matriz_incidencia()
        else:
            if flag1 is False and flag2 is False:
                print("Vértices no válidos")
            elif flag1 is False:
                print("el vértice de partida no existe")
            else:
                print("el vértice de llegada no existe")

    def eliminar_arista(self, index):
        """
        Elimina una relación que se generó automáticamente o por error
        :param index: 
        :return: 
        """
        if 0 <= index <= len(self.aristas_base) - 1:
            self.aristas_base.pop(index)
        else:
            print("no existe la arista")

    def unir_con_grafo(self, grafo2):
        primero = 0
        contador = len(self.vertices)
        for vertice in grafo2.vertices:
            respuesta = self.confirmar_inclusion(vertice.elementos)
            if respuesta == - 1:
                old_id = vertice.id
                vertice.id = contador
                self.vertices.append(vertice)
                self.referencias.append(contador)
                contador += 1
                for arista in grafo2.aristas_base:
                    if old_id in arista:
                        if arista[0] == old_id:
                            arista[0] = vertice.id
                        if arista[1] == old_id:
                            arista[1] = vertice.id
                if primero == 0:
                    self.agregar_arista(self.referencias[len(self.referencias) - 2], vertice.id)
                    primero += 1
            else:
                for disp in vertice.disposicion:
                    self.vertices[respuesta].disposicion.append(disp)
                for perm in vertice.permutacion:
                    self.vertices[respuesta].permutacion.append(perm)
                self.referencias.append(respuesta)
                old_id = vertice.id
                vertice.id = respuesta
                for arista in grafo2.aristas_base:
                    if old_id in arista:
                        if arista[0] == old_id:
                            arista[0] = vertice.id
                        if arista[1] == old_id:
                            arista[1] = vertice.id
                if primero == 0:
                    self.agregar_arista(self.referencias[len(self.referencias) - 2], vertice.id)
                    primero += 1
        for arista in grafo2.aristas_base:
            self.aristas_base.append(arista)
        self.generar_matriz_adyacencia_d()

    def agregar_matriz_aux(self, matriz, nombre):
        """ Agrega objetos MatrizAuxiliar al arreglo matrices_aux que pueden ser consultadas, modificadas y exportadas
        :param matriz: matriz generada por alguna función de búsqueda
        :param nombre: nombre que se le da a la matriz - tipo texto
        :return: 
        """
        a = MatrizAuxiliar(len(self.matrices_aux), matriz, nombre)
        self.matrices_aux.append(a)

    def consulta_por_nombre(self, nombre_forte):
        """
        busca el nodo que tenga el nombre forte proporcionado
        :param nombre_forte: nombre del tipo de conjunto 
        :return: Id del nodo, null de lo contrario
        """
        listado = []
        for iterador in range(len(self.vertices)):
            if self.vertices[iterador].nombreForte == nombre_forte:
                listado.append(self.vertices[iterador].id)
        return listado

    def consulta_por_id(self, ident):
        return self.vertices[ident].nombreForte
    
    def consulta_por_conjunto(self, conjunto):
        """
        busca el nodo que tenga el conjunto proporcionado
        :param conjunto: elementos del conjunto [lista] 
        :return: Id del nodo, null de lo contrario
        """
        conj = chord.Chord(conjunto)
        conju = conj.normalOrder
        for iterador in range(len(self.vertices)):
            if self.vertices[iterador].elementos == conju:
                return self.vertices[iterador].id

    def buscar_relaciones_cualidad(self):
        """ Recorre la matriz de adyacencia para encontrar relaciones de Tn/TnI o cambio de cualidad
        asigna según el caso 1 para transposición, 2 para inversión, 3 para cambio de cualidad y junto a estas, una 
        cuantificación de magnitud de la transformación según el caso.
        :return: matriz de relación que se puede añadir al arreglo de matrices auxiliares
        """
        matriz = []
        for k in range(len(self.matriz_adyacencia)):
            row = []
            for j in range(len(self.matriz_adyacencia[k])):
                if self.matriz_adyacencia[k][j] != 0:
                    conjunto1 = self.vertices[k].nombreForte
                    conjunto2 = self.vertices[j].nombreForte
                    if auxiliares.relacion_tn_tni_q(conjunto1, conjunto2) == 1:
                        item = [1, auxiliares.cuantificar_tn(self.vertices[k].elementos, self.vertices[j].elementos)]
                    elif auxiliares.relacion_tn_tni_q(conjunto1, conjunto2) == 2:
                        item = [2, auxiliares.cuantificar_tni(self.vertices[k].elementos, self.vertices[j].elementos)]
                    else:
                        conjunto1 = self.vertices[k].set_class
                        conjunto2 = self.vertices[j].set_class
                        spectra1 = auxiliares.spectra(self.vertices[k].elementos, 7, 12)
                        spectra2 = auxiliares.spectra(self.vertices[j].elementos, 7, 12)
                        item = [3, auxiliares.cuantificar_q(conjunto1, conjunto2), auxiliares.angle(spectra1, spectra2)]
                    row.append(item)
                else:
                    row.append([0])
            matriz.append(row)
        return matriz

    def obtener_conjuntos_nodos_adyacentes(self, ident):
        if ident <= len(self.matriz_adyacencia):
            lista = []
            for iterator in range(len(self.matriz_adyacencia[ident])):
                if self.matriz_adyacencia[ident][iterator] == 1:
                    lista.append([self.vertices[iterator].id, self.vertices[iterator].elementos])
            return lista
        else:
            print("no existe el nodo requerido")

    def exportar_grafo(self):
        """
        exporta a csv los vértices y las aristas
        :return: 
        """
        raiz = tk.Tk()
        raiz.attributes('-topmost', True)
        raiz.withdraw()
        name = filedialog.asksaveasfilename()
        ofile = open(name + "_nodos.csv", "w")
        writer = csv.writer(ofile, delimiter=';', lineterminator='\n')
        s = ["Id", "Label", "Forma Prima", "nombre Forte", "set Class", "disposición", "permutación",
             "vector interválico", "id2"]
        writer.writerow(s)
        for vertice in self.vertices:
            s = [vertice.id + 1, vertice.elementos, vertice.formaPrima, vertice.nombreForte, vertice.set_class,
                 vertice.disposicion, vertice.permutacion, vertice.vectorIntervalico, vertice.id]
            writer.writerow(s)
        ofile.close()
        aristas = []
        for arista in self.aristas_base:
            edge = []
            for e in arista:
                edge.append(e + 1)
            aristas.append(edge)
        ofile = open(name + "_aristas.csv", "w")
        writer = csv.writer(ofile, delimiter=';', lineterminator='\n')
        s = ["Source", "Target"]
        writer.writerow(s)
        for arista in aristas:
            s = arista
            writer.writerow(s)
        ofile.close()
        ofile = open(name + "_secuencia.csv", "w")
        writer = csv.writer(ofile, delimiter=';', lineterminator='\n')
        row = []
        for ident in self.referencias:
            row.append(ident)
        writer.writerow(row)
        ofile.close()

    def exportar_matriz_q(self):
        """
        Exporta a dos archivos csv las aristas del grafo y los valores de la matriz de cualidad
        :return: 
        """
        raiz = tk.Tk()
        raiz.attributes('-topmost', True)
        raiz.withdraw()
        name = filedialog.asksaveasfilename(defaultextension=".csv")
        ofile = open(name, "w")
        writer = csv.writer(ofile, delimiter=';', lineterminator='\n')
        s = ["Source", "Target", "Type", "Tipo", "Cantidad"]
        writer.writerow(s)
        for arista in self.aristas_base:
            info = deepcopy(self.matrices_aux[0].matriz[arista[0]][arista[1]])
            tipo = info[0]
            info.pop(0)
            s = [arista[0] + 1, arista[1] + 1, "Directed", tipo, info]
            writer.writerow(s)
        ofile.close()

    def exportar_matriz_aux(self, index):
        """
        permite exportar a dos archivos csv las aristas y la relación que hay en una matriz auxiliar 
        :param index: 
        :return: 
        """
        raiz = tk.Tk()
        raiz.attributes('-topmost', True)
        raiz.withdraw()
        name = filedialog.asksaveasfilename(defaultextension=".csv")
        ofile = open(name, "w")
        writer = csv.writer(ofile, delimiter=';', lineterminator='\n')
        s = ["Source", "Target", "Type", self.matrices_aux[index].nombre]
        writer.writerow(s)
        for arista in self.aristas_base:
            info = self.matrices_aux[index].matriz[arista[0]][arista[1]]
            s = [arista[0] + 1, arista[1] + 1, "Directed", info]
            writer.writerow(s)
        ofile.close()

    def guardar_como(self):
        """
        guarda en un archivo txt con codificación JSON un grafo
        :return: 
        """
        red = {}
        for vertice in self.vertices:
            red[vertice.id] = {
                'disposicion': vertice.disposicion,
                'elementos': vertice.elementos,
                'permutacion': vertice.permutacion,
                'conexiones': self.matriz_adyacencia[vertice.id],
                'direcciones': self.matriz_adyacencia[vertice.id],
                'referencias': self.referencias,
                'aristas': self.aristas_base
            }
        s = json.dumps(red)
        name = filedialog.asksaveasfile(mode='w', defaultextension=".txt")
        name.write(s)

    def abrir_red(self):
        """
        permite leer un archivo txt con codificación JSON en el que ya hay un grafo previamente guardado
        :return: 
        """
        raiz = tk.Tk()
        raiz.attributes('-topmost', True)
        raiz.withdraw()
        ruta = filedialog.askopenfilename()
        if ruta != '':
            try:
                f = open(ruta, "r")
                s = f.read()
                red = json.loads(s)
                for elemento in red:
                    conjunto = red[elemento]['elementos']
                    id = int(elemento)
                    nodoA = NodoAnalisis(conjunto, id)
                    nodoA.disposicion = red[elemento]['disposicion']
                    nodoA.permutacion = red[elemento]['permutacion']
                    self.vertices.append(nodoA)
                    self.matriz_adyacencia.append(red[elemento]['conexiones'])
                    self.matriz_incidencia.append(red[elemento]['direcciones'])
                self.referencias = red['0']['referencias']
                self.aristas_base = red['0']['aristas']
            except ValueError:
                print("no es un tipo de archivo válido")
        else:
            print("no se cargó archivo alguno")

    def exportar_tendencia_q(self):
        """
        Exporta a un archivo csv los valores de la matriz de cualidad
        :return: null
        """
        row1 = []
        row2 = []
        row3 = []
        row4 = []
        for arista in self.aristas_base:
            info = self.matrices_aux[0].matriz[arista[0]][arista[1]]
            if len(info) > 2:
                row1.append(info[0])
                row2.append(info[1])
                row3.append(info[2][0])
                row4.append(info[2][1])
            else:
                row1.append(info[0])
                row2.append(info[1])
                row3.append(0)
                row4.append(0)
        raiz = tk.Tk()
        raiz.attributes('-topmost', True)
        raiz.withdraw()
        name = filedialog.asksaveasfilename(defaultextension=".csv")
        ofile = open(name, "w")
        writer = csv.writer(ofile, delimiter=';', lineterminator='\n')
        s = ["Pareja", "Tipo", "VL-SCSPC", "ANGLE", "DISTANCE"]
        writer.writerow(s)
        for arista in range(len(self.aristas_base)):
            pareja = self.aristas_base[arista]
            tipo = row1[arista]
            vl_spspc = row2[arista]
            angle = row3[arista]
            distance = row4[arista]
            s = [pareja, tipo, vl_spspc, angle, distance]
            writer.writerow(s)
        ofile.close()

    def exportar_tendencia_matriz_aux(self, index):
        """
        Exporta a un archivo csv los valores asociados a cada pareja en una matriz definida por el usuario
        :param index: índice en el arreglo de matrices auxiliares
        :return: null
        """
        row1 = []
        for arista in self.aristas_base:
            info = self.matrices_aux[index].matriz[arista[0]][arista[1]]
            row1.append(info)
        raiz = tk.Tk()
        raiz.attributes('-topmost', True)
        raiz.withdraw()
        name = filedialog.asksaveasfilename()
        ofile = open(name + "línea_" + self.matrices_aux[index].nombre + ".csv", "w")
        writer = csv.writer(ofile, delimiter=';', lineterminator='\n')
        s = ["Pareja", self.matrices_aux[index].nombre]
        writer.writerow(s)
        for arista in range(len(self.aristas_base)):
            pareja = self.aristas_base[arista]
            tipo = row1[arista]
            s = [pareja, tipo]
            writer.writerow(s)
        ofile.close()


