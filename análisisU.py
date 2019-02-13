import json
import tkinter as tk
from tkinter import filedialog
from music21 import *
import csv
from copy import deepcopy


class Matriz:
    set_name = ""
    row = []
    id = 0

    def __init__(self, name, row, id):
        self.set_name = name
        self.row = row
        self.id = id


class Conjunto:
    id = 0
    elementos = []
    padres = []
    ivector = []
    forte_name = ""
    set_class = ""
    normal_order = []
    forma_prima = []
    card = 0

    def __init__(self, ident, elements, parents):
        a_c = chord.Chord(elements)
        self.id = ident
        self.elementos = elements
        self.padres = parents
        self.ivector = a_c.intervalVector
        self.forte_name = a_c.forteClass
        self.set_class = a_c.forteClassTnI
        self.normal_order = a_c.normalOrder
        self.forma_prima = a_c.primeForm
        self.card = len(elements)


class NodoRedTransitiva:
    set_class_ref = ""
    prime_form = []
    card = 0
    same_card_ref = []
    transit_card_npm1 = []

    def __init__(self, name, prime):
        self.set_class_ref = name
        self.prime_form = prime
        self.card = len(prime)
        self.same_card_ref = []
        self.transit_card_npm1 = []

    def add_same_card_r(self, fname):
        if fname not in self.set_class_ref:
            self.set_class_ref.append(fname)

    def add_transit_card_npm1(self, fname):
        if fname not in self.transit_card_npm1:
            self.transit_card_npm1.append(fname)


class RedTransitiva:
    elementos_cargados = []
    red_transitiva_set_class = []
    added = []
    matriz = []

    def cargar_elementos(self):
        """
        Carga un archivo con los conjuntos
        :return: null
        """
        raiz = tk.Tk()
        raiz.withdraw()
        ruta = filedialog.askopenfilename()
        f = open(ruta, "r")
        s = f.read()
        base_de_datos = json.loads(s)
        for i in range(len(base_de_datos)):
            b = Conjunto(i, base_de_datos[str(i)]['conjunto'], base_de_datos[str(i)]['padres'])
            self.elementos_cargados.append(b)

    def cargar_red(self):
        raiz = tk.Tk()
        raiz.withdraw()
        #ruta = filedialog.askopenfilename()
        ruta = "relaciones_transito.txt"
        f = open(ruta, "r")
        s = f.read()
        red = json.loads(s)
        for i in red:
            acorde = chord.Chord(red[i]['prime'])
            node = NodoRedTransitiva(acorde.forteClassTnI, red[i]['prime'])
            node.same_card_ref = red[i]['rel-igual-card']
            node.transit_card_npm1 = red[i]['rel-card+1']
            self.red_transitiva_set_class.append(node)
            self.added.append(red[i])

    def cargar_matriz(self):
        ruta = "matriz_set_class.txt"
        f = open(ruta, "r")
        s = f.read()
        matriz = json.loads(s)
        contador = 0
        for set_class in matriz:
            row = Matriz(set_class, matriz[set_class]['distancias'], contador)
            self.matriz.append(row)
            contador += 1

    def obtener_id(self, conjunto):
        for i in range(len(self.matriz)):
            if conjunto == self.matriz[i].set_name:
                return self.matriz[i].id

    def obtener_valor_en_matriz(self, conjunto1, conjunto2):
        pos1 = self.obtener_id(conjunto1)
        pos2 = self.obtener_id(conjunto2)
        return self.matriz[pos1].row[pos2]

    def obtener_posicion(self, conjunto):
        for i in range(len(self.red_transitiva_set_class)):
            if self.red_transitiva_set_class[i].set_class_ref == conjunto:
                return i

    def first_card_red(self, cardinalidad):
        for i in range(0, len(self.red_transitiva_set_class)):
            if self.red_transitiva_set_class[i].card == cardinalidad:
                return i
            else:
                if i == len(self.red_transitiva_set_class) - 1:
                    return -2

    def last_card_red(self, cardinalidad):
        temp = (self.first_card(cardinalidad - 1)) - 1
        if temp == -3:
            return len(self.red_transitiva_set_class)
        else:
            return temp

    @staticmethod
    def devolver_menor(listado):
        temporal = listado[0]
        for i in listado:
            if i < temporal:
                temporal = i
        return temporal

    def distancia_igual_card(self, conjunto1, conjunto2):
        distancia = 0
        pos_conjunto1 = self.obtener_posicion(conjunto1)
        if conjunto1 == conjunto2:
            return 0
        else:
            if conjunto2 in self.red_transitiva_set_class[pos_conjunto1].same_card_ref:
                return 1
            else:
                distancia += 1
                listado = []
                for i in range(len(self.red_transitiva_set_class[pos_conjunto1].same_card_ref)):
                    listado.append(self.red_transitiva_set_class[pos_conjunto1].same_card_ref[i])
                condicion = True
                while condicion:
                    lista2 = deepcopy(listado)
                    for i in listado:
                        posicion = self.obtener_posicion(i)
                        for j in range(len(self.red_transitiva_set_class[posicion].same_card_ref)):
                            elemento = self.red_transitiva_set_class[posicion].same_card_ref[j]
                            if elemento not in lista2:
                                lista2.append(self.red_transitiva_set_class[posicion].same_card_ref[j])
                    if conjunto2 in lista2:
                        return distancia + 1
                    else:
                        distancia += 1
                        listado = deepcopy(lista2)

    def distancia_menor_mayor(self, conjuntop, conjuntog):
        distancia = 0
        pos_conjg = self.obtener_posicion(conjuntog)
        pos_conjp = self.obtener_posicion(conjuntop)
        cardin_conjg = self.red_transitiva_set_class[pos_conjg].card
        cardin_conjp = self.red_transitiva_set_class[pos_conjp].card
        diferencia = abs(cardin_conjg - cardin_conjp)
        rel_totales = deepcopy(self.red_transitiva_set_class[pos_conjp].transit_card_npm1)
        rel_sig_card = deepcopy(self.red_transitiva_set_class[pos_conjp].transit_card_npm1)
        if diferencia > 1:
            for i in range(diferencia - 1):
                distancia += 1
                # este bloque agrega los nodos de la siguiente cardinalidad
                nexti = []
                for j in rel_sig_card:
                    pos = self.obtener_posicion(j)
                    for k in self.red_transitiva_set_class[pos].transit_card_npm1:
                        nexti.append(k)
                for j in nexti:
                    rel_totales.append(j)
                rel_sig_card = deepcopy(nexti)
            if conjuntog in rel_sig_card:
                distancia = distancia + 1
                return distancia
            else:
                distancia += 1
                distancias = []
                for i in rel_sig_card:
                    distancias.append(self.distancia_igual_card(i, conjuntog))
                return distancia + self.devolver_menor(distancias)
        else:
            if conjuntog in rel_sig_card:
                return 1
            else:
                distancias = []
                for i in rel_sig_card:
                    distancias.append(self.distancia_igual_card(i, conjuntog))
                return 1 + self.devolver_menor(distancias)

    def distancia_vlpcs(self, conjunto1, conjunto2):
        pos1 = self.obtener_posicion(conjunto1)
        pos2 = self.obtener_posicion(conjunto2)
        if self.red_transitiva_set_class[pos1].card == self.red_transitiva_set_class[pos2].card:
            return self.distancia_igual_card(conjunto1, conjunto2)
        else:
            if self.red_transitiva_set_class[pos1].card > self.red_transitiva_set_class[pos2].card:
                return self.distancia_menor_mayor(conjunto2, conjunto1)
            else:
                return self.distancia_menor_mayor(conjunto1, conjunto2)

    def first_card(self, cardinalidad):
        for i in range(0, len(self.red_transitiva_set_class)):
            if self.red_transitiva_set_class[i].card == cardinalidad:
                return i
            else:
                if i == len(self.red_transitiva_set_class) - 1:
                    return -2

    def last_card(self, cardinalidad):
        temp = (self.first_card(cardinalidad - 1)) - 1
        if temp == -3:
            return len(self.red_transitiva_set_class)
        else:
            return temp

    @staticmethod
    def comparar_misma_card(conjunto1, conjunto2):
        # ver si tienen n-1 elementos en común
        elem_a = list(set(conjunto1) - set(conjunto2))
        elem_b = list(set(conjunto2) - set(conjunto1))
        if len(elem_a) == 1 and len(elem_b) == 1:
            dif = (elem_b[0] - elem_a[0]) % 12
            if dif == 1 or dif == 11:
                return True
            else:
                return False
        else:
            return False

    @staticmethod
    def verificar_inclusion(conjunto1, conjunto2):
        """
        :param conjunto1: menor card conj 
        :param conjunto2: mayor card conj
        :return: true or false
        """
        if set(conjunto1) - set(conjunto2) == set():
            return True
        else:
            return False

    def verificar_rel_min(self, conjunto1, conjunto2):
        """
        :param conjunto1: el de menor card 
        :param conjunto2: el de mayor card
        :return: true or false
        """
        if self.verificar_inclusion(conjunto1, conjunto2):
            elemento = list(set(conjunto2) - set(conjunto1))
            elemento = elemento[0]
            ivect = [0, 0, 0, 0, 0, 0]
            for i in range(len(conjunto1)):
                interv = (elemento - conjunto1[i]) % 12
                if interv > 6:
                    interv = abs(12 - interv)
                ivect[interv - 1] = ivect[interv - 1] + 1
            if ivect[0] != 0:
                return True
            else:
                return False
        else:
            return False

    def armar_red(self): # ESTE ES EL QUE DEBO MODIFICAR PARA QUE RESPONDA A LA NUEVA RED
        # voy a recorrer la red desde el último elemento, para cada cardinalidad voy a verificar primero las relaciones
        # de movimiento de 1 st.
        # luego se verifica la inclusión en los de siguiente cardinalidad. Esto ocurre entre 3 y 11.
        for cardin in range(1, 11):
            first_cardin = self.first_card(cardin)
            last_cardin = self.last_card(cardin)
            # Si la primera y última son iguales no hacer nada
            # comparación con los de misma cardinalidad
            for j in range(first_cardin, last_cardin):
                for k in range(first_cardin, last_cardin):
                    if self.elementos_cargados[j].set_class != self.elementos_cargados[k].set_class:
                        if self.comparar_misma_card(self.elementos_cargados[j].elementos,
                                                    self.elementos_cargados[k].elementos):
                            if not (self.elementos_cargados[j].set_class in self.added):
                                obj = NodoRedTransitiva(self.elementos_cargados[j].set_class,
                                                        self.elementos_cargados[j].forma_prima)
                                self.red_transitiva_set_class.append(obj)
                                self.added.append(self.elementos_cargados[j].set_class)
                                index = len(self.red_transitiva_set_class) - 1
                                if not (self.elementos_cargados[k].set_class in
                                        self.red_transitiva_set_class[index].same_card_ref):
                                    self.red_transitiva_set_class[index].same_card_ref.append(
                                        self.elementos_cargados[k].set_class)
                            else:
                                index = 0
                                for i in range(len(self.added)):
                                    if self.elementos_cargados[j].set_class == self.added[i]:
                                        index = i
                                        break
                                if not (self.elementos_cargados[k].set_class in
                                        self.red_transitiva_set_class[index].same_card_ref):
                                    self.red_transitiva_set_class[index].same_card_ref.append(
                                        self.elementos_cargados[k].set_class)
            # comparación con los de la siguiente cardinalidad
            first_next_card = self.first_card(cardin + 1)
            last_next_card = self.last_card(cardin + 1)
            for j in range(first_cardin, last_cardin):
                for k in range(first_next_card, last_next_card):
                    if self.verificar_rel_min(self.elementos_cargados[j].elementos,
                                              self.elementos_cargados[k].elementos):
                        index = 0
                        for i in range(len(self.added)):
                            if self.elementos_cargados[j].set_class == self.added[i]:
                                index = i
                                break
                        if not (self.elementos_cargados[k].set_class in
                                self.red_transitiva_set_class[index].transit_card_npm1):
                            self.red_transitiva_set_class[index].transit_card_npm1.append(
                                self.elementos_cargados[k].set_class)
                            # se pregunta si ya está incluido en el listado de relaciones de inclusión

    def construir_matriz(self):
        matriz = []
        for i in range(len(self.red_transitiva_set_class)):
            row = []
            for j in range(len(self.red_transitiva_set_class)):
                print(self.red_transitiva_set_class[i].set_class_ref, self.red_transitiva_set_class[j].set_class_ref)
                if self.red_transitiva_set_class[i].prime_form == self.red_transitiva_set_class[j].prime_form:
                    row.append(0)
                elif self.red_transitiva_set_class[i].card == self.red_transitiva_set_class[j].card:
                    row.append(self.distancia_igual_card(self.red_transitiva_set_class[i].set_class_ref,
                                                         self.red_transitiva_set_class[j].set_class_ref))
                elif self.red_transitiva_set_class[i].card < self.red_transitiva_set_class[j].card:
                    row.append(self.distancia_menor_mayor(self.red_transitiva_set_class[i].set_class_ref,
                                                          self.red_transitiva_set_class[j].set_class_ref))
                else:
                    row.append(self.distancia_menor_mayor(self.red_transitiva_set_class[j].set_class_ref,
                                                          self.red_transitiva_set_class[i].set_class_ref))
            matriz.append(row)
        matriz_completa = {}
        for i in range(len(matriz)):
            matriz_completa[self.red_transitiva_set_class[i].set_class_ref] = {
                'distancias': matriz[i]
            }
        s = json.dumps(matriz_completa)
        name = filedialog.asksaveasfile(mode='w', defaultextension=".txt")
        name.write(s)

    def guardar_estructura_json(self):
        relaciones_vlpcs = {}
        for i in range(len(self.red_transitiva_set_class)):
            relaciones_vlpcs[self.red_transitiva_set_class[i].set_class_ref] = {
                'prime': self.red_transitiva_set_class[i].prime_form,
                'rel-igual-card': self.red_transitiva_set_class[i].same_card_ref,
                'rel-card+1': self.red_transitiva_set_class[i].transit_card_npm1
            }
        s = json.dumps(relaciones_vlpcs)
        name = filedialog.asksaveasfile(mode='w', defaultextension=".txt")
        name.write(s)

    def guardar_estructura_csv(self, name):
        ofile = open(name + "nodos.csv", "w")
        writer = csv.writer(ofile, delimiter=';')
        s = ["Id", "Label", "Prime", "Same_card", "Card_+1"]
        writer.writerow(s)
        for i in range(len(self.red_transitiva_set_class)):
            s = [i + 1, self.red_transitiva_set_class[i].set_class_ref,
                 self.red_transitiva_set_class[i].prime_form,
                 self.red_transitiva_set_class[i].same_card_ref,
                 self.red_transitiva_set_class[i].transit_card_npm1]
            writer.writerow(s)
        ofile.close()
        aristas = []
        for i in range(len(self.red_transitiva_set_class)):
            if len(self.red_transitiva_set_class[i].same_card_ref) != 0:
                for j in self.red_transitiva_set_class[i].same_card_ref:
                    pareja = [i+1, self.obtener_posicion(j)+1]
                    aristas.append(pareja)
            if i < 208:
                for j in self.red_transitiva_set_class[i].transit_card_npm1:
                    pareja = [i+1, self.obtener_posicion(j)+1]
                    aristas.append(pareja)
        ofile = open(name + "aristas.csv", "w")
        writer = csv.writer(ofile, delimiter=';')
        s = ["Source", "Target"]
        writer.writerow(s)
        for i in aristas:
            writer.writerow(i)
        ofile.close()


'''a = RedTransitiva()
a.cargar_red()
#a.armar_red()
a.construir_matriz()


a = RedTransitiva()
a.cargar_matriz()
print(a.obtener_valor_en_matriz('7-12', '6-20'))
a = RedTransitiva()
a.cargar_red()
#print("red cargada")
#print(a.distancia_vlpcs('6-20', '7-12'))
a.construir_matriz()
# a.guardar_estructura_csv("vlpcspace")
a = RedTransitiva()
a.cargar_elementos()
a.armar_red()
a.guardar_estructura_json()
#a.guardar_estructura_csv("relaciones")
'''