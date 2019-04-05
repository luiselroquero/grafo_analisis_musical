from music21 import *
import tkinter as tk
from tkinter import filedialog
import auxiliares
import csv
import json
from copy import deepcopy


class NodeAnalysis:
    elements = []
    primeForm = []
    forteName = ""
    intervalVector = []
    disposition = []
    permutation = []
    id = 0
    position_in_list = []
    set_class = ""
    # posiblemente eliminables después
    inFrom = []
    outTo = []

    def __init__(self, set_u, ident):
        """
        inicialization of the set-node
        :param set_u: chord object from music21
        :param ident: assigned identity after checking it does not exist previously
        """
        if type(set_u) is list:
            a = chord.Chord(set_u)
            set_u = a
        self.disposition = []
        self.permutation = []
        self.elements = set_u.normalOrder
        self.primeForm = set_u.primeForm
        self.forteName = set_u.forteClass
        self.intervalVector = set_u.intervalVector
        self.id = ident
        self.set_class = set_u.forteClassTnI
        self.convertir_disposicion(set_u)

    def convertir_disposicion(self, elements):
        """
        Takes the elements of a set in chord format from music21 and converts them into
        a disposition of pitches in MIDI numbers and as a numeric representation of permutation in pitch classes
        :param elements: elemento music21
        :return: null, afecta directamente los atributos disposión y permutación
        """
        set_u = auxiliares.convertir_a_midi(elements)
        self.disposition.append(set_u)
        self.permutation.append(auxiliares.convertir_a_permutacion(set_u))

    def asign_entry(self, ident):
        """
        This procedure stores the identity of the previous set, It is intended as a mechanism to generate
        the graph.
        :param ident: identity
        :return: null
        """
        self.inFrom.append(ident)

    def asign_out(self, ident):
        """
        This procedure stores the identity of the destination set. It is intended as a mechanism to generate the
        graph.
        :param ident: identity
        :return: null
        """
        self.outTo.append(ident)


class AuxiliaryMatrix:

    id = 0
    matrix = []
    name = ""

    def __init__(self, ident, matrix, name):
        self.id = ident
        self.matrix = matrix
        self.name = name


class GraphAnalysis:
    # This list is an array of music21 chord-format entries
    list = []
    # reference to the xml input file
    file = 0
    # the set of nodes created in the graph
    nodes = []
    # an array simmilar to list with the reference to the id of the nodes. It is useful to create matrixes.
    references = []
    # edges list
    edges_base = []
    # Incidence matrix
    incidence_matrix = []
    # adjacency matrix
    adjacency_matrix = []
    # array of auxiliary matrixes
    aux_matrixes = []

    def __init__(self):
        self.list = []
        self.file = 0
        self.nodes = []
        self.references = []
        self.edges_base = []
        self.incidence_matrix = []
        self.adjacency_matrix = []
        self.aux_matrixes = []

    def load_file(self):
        """
        This procedure opens a dialog window to load the XML file in which the set segmentation is stored
        :return: null
        """
        root = tk.Tk()
        root.withdraw()
        ruta = filedialog.askopenfilename()
        if ruta != '':
            try:
                self.file = converter.parse(ruta)
                a = self.file.flat.chordify()
                self.list = a.flat.notes.stream()
            except ValueError:
                print("It is not a valid type")
        else:
            print("No file was loaded")

    def generate_node(self, list_u, index):
        """
        generates a new node
        :param list_u: is a music21 object used to get the all node's information
        :param index: is the identity of the node
        :return: null
        """
        node = NodeAnalysis(list_u, index)
        self.nodes.append(node)

    def confirm_inclusion(self, set_u):
        """
        confirms if the set is already part of the graph
        :param set_u: current set
        :return: -1 if the node does not exist, but if it does, it returns the node's id number
        """
        if type(set_u) == list:
            conjunt = chord.Chord(set_u)
            set_u = conjunt
        answer = -1
        set_compare = set_u.normalOrder
        for k in range(len(self.nodes)):
            if set_compare == self.nodes[k].elements:
                answer = k
                break
        return answer

    def generate_edges_base(self):
        """
        reads the references list and builds the first edges based on the order of the list
        :return: null
        """
        edge = []
        length = len(self.references) - 1
        for k in range(length):
            if k < length:
                edge = [self.references[k], self.references[k+1]]
            self.edges_base.append(edge)

    def generate_adjacency_matrix_d(self):
        """
        Creates the adjacency matrix as in a directed graph
        :return: null
        """
        self.adjacency_matrix = []
        for k in range(len(self.nodes)):
            row = []
            for j in range(len(self.nodes)):
                pair = [self.nodes[k].id, self.nodes[j].id]
                if pair in self.edges_base:
                    row.append(1)
                else:
                    row.append(0)
            self.adjacency_matrix.append(row)

    def generate_incidence_matrix(self):
        """
        Creates the incidence matrix
        :return: null
        """
        self.incidence_matrix = []
        for k in range(len(self.nodes)):
            row = []
            for j in range(len(self.edges_base)):
                if self.nodes[k].id in self.edges_base[j]:
                    if self.nodes[k].id == self.edges_base[j][0]:
                        row.append(-1)
                    else:
                        row.append(1)
                else:
                    row.append(0)
            self.incidence_matrix.append(row)

    def generate_graph(self):
        """
        Once the file is loaded, this procedure turns the chord list into set objects over which the operations
        will be made.
        :return: null
        """
        counter = 0
        for j in range(len(self.list)):
            answer = self.confirm_inclusion(self.list[j])
            if answer == -1:
                self.generate_node(self.list[j], counter)
                self.references.append(counter)
                counter = counter + 1
            else:
                self.nodes[answer].convertir_disposicion(self.list[j])
                self.references.append(answer)
        self.generate_edges_base()
        self.generate_adjacency_matrix_d()
        self.generate_incidence_matrix()
        print(str(len(self.nodes)) + " nodes were generated")

    def add_node(self, set_u):
        """
        Este método permite agregar nodos manualmente cuando no se pueden agregar directamente desde music XML
        :param set_u: list of pitches as MIDI numbers
        :return: null
        """
        acorde = chord.Chord(set_u)
        self.list.append(acorde)

    def add_edge(self, init, ending):
        """
        Adds an edge defined by the user or automated procedure
        :param init: begening node
        :param ending: ending node
        :return: null
        """
        flag1 = False
        flag2 = False
        for iterador in range(len(self.nodes)):
            if self.nodes[iterador].id == init:
                flag1 = True
        for iterador in range(len(self.nodes)):
            if self.nodes[iterador].id == ending:
                flag2 = True
        if flag1 and flag2:
            self.edges_base.append([init, ending])
            self.generate_adjacency_matrix_d()
            self.generate_incidence_matrix()
        else:
            if flag1 is False and flag2 is False:
                print("Invalid egde")
            elif flag1 is False:
                print("invalid departure node")
            else:
                print("invalid destination node")

    def delete_edge(self, index):
        """
        deletes an edge in the list edges_base.
        :param index: possition of the edge in the list edges_base
        :return: 
        """
        if 0 <= index <= len(self.edges_base) - 1:
            self.edges_base.pop(index)
        else:
            print("the edge does not exist")

    def join_with_graph(self, graph2):
        first = 0
        counter = len(self.nodes)
        for node in graph2.nodes:
            answer = self.confirm_inclusion(node.elements)
            if answer == - 1:
                old_id = node.id
                node.id = counter
                self.nodes.append(node)
                self.references.append(counter)
                counter += 1
                for edge in graph2.edges_base:
                    if old_id in edge:
                        if edge[0] == old_id:
                            edge[0] = node.id
                        if edge[1] == old_id:
                            edge[1] = node.id
                if first == 0:
                    self.add_edge(self.references[len(self.references) - 2], node.id)
                    first += 1
            else:
                for disp in node.disposition:
                    self.nodes[answer].disposition.append(disp)
                for perm in node.permutation:
                    self.nodes[answer].permutation.append(perm)
                self.nodes.append(answer)
                old_id = node.id
                node.id = answer
                for edge in graph2.edges_base:
                    if old_id in edge:
                        if edge[0] == old_id:
                            edge[0] = edge.id
                        if edge[1] == old_id:
                            edge[1] = edge.id
                if first == 0:
                    self.add_edge(self.references[len(self.references) - 2], node.id)
                    first += 1
        for edge in graph2.edges_base:
            self.edges_base.append(edge)
        self.generate_adjacency_matrix_d()

    def add_auxiliary_matrix(self, matrix, name):
        """
        Adds AuxiliaryMatrix objects to the aux_matrixes array. Those can be consulted, modified and exported.
        :param matrix: matrix or procedure to generate a matrix
        :param name: text to identify the matrix
        :return: null
        """
        a = AuxiliaryMatrix(len(self.aux_matrixes), matrix, name)
        self.aux_matrixes.append(a)

    def get_by_name(self, forte_name):
        """
        looks for the node with the provided forte name
        :param forte_name: provided name
        :return: nodes id, null otherwise
        """
        list_u = []
        for iterator in range(len(self.nodes)):
            if self.nodes[iterator].forteName == forte_name:
                list_u.append(self.nodes[iterator].id)
        return list_u

    def get_by_id(self, ident):
        return self.nodes[ident].forteName
    
    def get_by_set(self, set_u):
        """
        looks for the node with the provided set
        :param set_u: elements in the set [list]
        :return: nodes id, null otherwise
        """
        conj = chord.Chord(set_u)
        conju = conj.normalOrder
        for iterador in range(len(self.nodes)):
            if self.nodes[iterador].elements == conju:
                return self.nodes[iterador].id

    def search_quality_relations(self):
        """
        runs through the adjacency matrix to find Tn/tnI or quality change relations
        assigns a number according to the case: 1 for transposition, 2 for inversion, 3 fot quality change, and
        with the latter one, an amount according to the magnitud of the transformation.
        :return: relation matrix that can be added to the auxiliary matrix array
        """
        matrix = []
        for k in range(len(self.adjacency_matrix)):
            row = []
            for j in range(len(self.adjacency_matrix[k])):
                if self.adjacency_matrix[k][j] != 0:
                    conjunto1 = self.nodes[k].forteName
                    conjunto2 = self.nodes[j].forteName
                    if auxiliares.relacion_tn_tni_q(conjunto1, conjunto2) == 1:
                        item = [1, auxiliares.cuantificar_tn(self.nodes[k].elements, self.nodes[j].elements)]
                    elif auxiliares.relacion_tn_tni_q(conjunto1, conjunto2) == 2:
                        item = [2, auxiliares.cuantificar_tni(self.nodes[k].elements, self.nodes[j].elements)]
                    else:
                        conjunto1 = self.nodes[k].set_class
                        conjunto2 = self.nodes[j].set_class
                        spectra1 = auxiliares.spectra(self.nodes[k].elements, 7, 12)
                        spectra2 = auxiliares.spectra(self.nodes[j].elements, 7, 12)
                        item = [3, auxiliares.cuantificar_q(conjunto1, conjunto2), auxiliares.angle(spectra1, spectra2)]
                    row.append(item)
                else:
                    row.append([0])
            matrix.append(row)
        return matrix

    def get_adjacent_set_nodes(self, ident):
        if ident <= len(self.adjacency_matrix):
            list_u = []
            for iterator in range(len(self.adjacency_matrix[ident])):
                if self.adjacency_matrix[ident][iterator] == 1:
                    list_u.append([self.nodes[iterator].id, self.nodes[iterator].elements])
            return list_u
        else:
            print("the required node does not exist")

    def export_graph(self):
        """
        exports to a CSV files the nodes and edgesa csv los vértices y las aristas
        :return: null
        """
        raiz = tk.Tk()
        raiz.attributes('-topmost', True)
        raiz.withdraw()
        name = filedialog.asksaveasfilename()
        ofile = open(name + "_nodes.csv", "w")
        writer = csv.writer(ofile, delimiter=';', lineterminator='\n')
        s = ["Id", "Label", "Prime Form", "Forte Name", "Set Class", "disposition", "permutation",
             "Interval Vector", "id2"]
        writer.writerow(s)
        for vertice in self.nodes:
            s = [vertice.id + 1, vertice.elements, vertice.primeForm, vertice.forteName, vertice.set_class,
                 vertice.disposition, vertice.permutation, vertice.intervalVector, vertice.id]
            writer.writerow(s)
        ofile.close()
        edges = []
        for edge in self.edges_base:
            edg = []
            for e in edge:
                edg.append(e + 1)
            edges.append(edge)
        ofile = open(name + "_edges.csv", "w")
        writer = csv.writer(ofile, delimiter=';', lineterminator='\n')
        s = ["Source", "Target"]
        writer.writerow(s)
        for edge in edges:
            s = edge
            writer.writerow(s)
        ofile.close()
        ofile = open(name + "_sequence.csv", "w")
        writer = csv.writer(ofile, delimiter=';', lineterminator='\n')
        row = []
        for ident in self.references:
            row.append(ident)
        writer.writerow(row)
        ofile.close()

    def export_matrix_q(self):
        """
        Exports the first auxiliary matrix, the quality change relations, into a CSV file with the edges and the
        information of the relations stored in the matrix
        :return: null
        """
        raiz = tk.Tk()
        raiz.attributes('-topmost', True)
        raiz.withdraw()
        name = filedialog.asksaveasfilename(defaultextension=".csv")
        ofile = open(name, "w")
        writer = csv.writer(ofile, delimiter=';', lineterminator='\n')
        s = ["Source", "Target", "Type", "Operation", "Amount"]
        writer.writerow(s)
        for arista in self.edges_base:
            info = deepcopy(self.aux_matrixes[0].matriz[arista[0]][arista[1]])
            tipo = info[0]
            info.pop(0)
            s = [arista[0] + 1, arista[1] + 1, "Directed", tipo, info]
            writer.writerow(s)
        ofile.close()

    def export_aux_matrix(self, index):
        """
        exports the selected auxiliary matrix
        :param index: position in the auxiliary matrix array
        :return: null
        """
        raiz = tk.Tk()
        raiz.attributes('-topmost', True)
        raiz.withdraw()
        name = filedialog.asksaveasfilename(defaultextension=".csv")
        ofile = open(name, "w")
        writer = csv.writer(ofile, delimiter=';', lineterminator='\n')
        s = ["Source", "Target", "Type", self.aux_matrixes[index].name]
        writer.writerow(s)
        for edge in self.edges_base:
            info = self.aux_matrixes[index].matrix[edge[0]][edge[1]]
            s = [edge[0] + 1, edge[1] + 1, "Directed", info]
            writer.writerow(s)
        ofile.close()

    def save_as(self):
        """
        saves in a txt file with JSON codification
        :return: null
        """
        net = {}
        for node in self.nodes:
            net[node.id] = {
                'disposition': node.disposition,
                'elements': node.elements,
                'permutation': node.permutation,
                'connections': self.adjacency_matrix[node.id],
                'directions': self.incidence_matrix[node.id],
                'references': self.references,
                'edges': self.edges_base
            }
        s = json.dumps(net)
        name = filedialog.asksaveasfile(mode='w', defaultextension=".txt")
        name.write(s)

    def open_net(self):
        """
        allows to read a TXT file with JSON codification where a graph has been stored
        :return: null
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
                    conjunto = red[elemento]['elements']
                    id_u = int(elemento)
                    nodoa = NodeAnalysis(conjunto, id_u)
                    nodoa.disposition = red[elemento]['disposition']
                    nodoa.permutation = red[elemento]['permutation']
                    self.nodes.append(nodoa)
                    self.adjacency_matrix.append(red[elemento]['connections'])
                    self.incidence_matrix.append(red[elemento]['directions'])
                self.references = red['0']['references']
                self.edges_base = red['0']['edges']
            except ValueError:
                print("invalid file")
        else:
            print("no file was loaded")

    def export_tendency_q(self):
        """
        Exports a CSV file with the quality auxiliary matrix values
        :return: null
        """
        row1 = []
        row2 = []
        row3 = []
        row4 = []
        for arista in self.edges_base:
            info = self.edges_base[0].matrix[arista[0]][arista[1]]
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
        for arista in range(len(self.edges_base)):
            pareja = self.edges_base[arista]
            tipo = row1[arista]
            vl_spspc = row2[arista]
            angle = row3[arista]
            distance = row4[arista]
            s = [pareja, tipo, vl_spspc, angle, distance]
            writer.writerow(s)
        ofile.close()

    def export_tendency_aux_matrix(self, index):
        """
        Exports a CSV file with the associated values to each pair in an auxiliary matrix defined by the user
        :param index: position in the auxiliary matrix
        :return: null
        """
        row1 = []
        for edge in self.edges_base:
            info = self.aux_matrixes[index].matrix[edge[0]][edge[1]]
            row1.append(info)
        raiz = tk.Tk()
        raiz.attributes('-topmost', True)
        raiz.withdraw()
        name = filedialog.asksaveasfilename()
        ofile = open(name + "línea_" + self.aux_matrixes[index].name + ".csv", "w")
        writer = csv.writer(ofile, delimiter=';', lineterminator='\n')
        s = ["Pareja", self.aux_matrixes[index].name]
        writer.writerow(s)
        for arista in range(len(self.edges_base)):
            pareja = self.edges_base[arista]
            tipo = row1[arista]
            s = [pareja, tipo]
            writer.writerow(s)
        ofile.close()
