import math
# from music21 import *
import análisisU as An


def spectra(conjunto, n, div):
    """retorna el espectro de un conjunto de clases de altura (Callender, 2007) 
    :param conjunto: conjunto de clases de altura 
    :param n: número de componentes a calcular (se sugiere que sea menor o igual a div
    :param div: número de divisiones de la octava para referencia
    :return: SPECTRA con n componentes
    """
    espectro = []
    for j in range(n):
        magnitud_sin = 0
        magnitud_cos = 0
        for i in conjunto:
            magnitud_sin = magnitud_sin + (math.sin(2 * math.pi * i * (j / div)))
            magnitud_cos = magnitud_cos + (math.cos(2 * math.pi * i * (j / div)))
        espectro.append(math.sqrt((math.pow(magnitud_sin, 2) + math.pow(magnitud_cos, 2))))
    espectro.pop(0)
    return espectro


def distancia_spectra(spectra1, spectra2, option):
    """devuelve la distancia euclidiana o power spectra según la opción (Callender, 2007)
    :param spectra1: Espectro del conjunto A
    :param spectra2: Espectro del conjunto B
    :param option: 1 d(a,b); 2 dpow(a,b)
    :return: distancia
    """
    suma = 0
    if option == 1:
        for i in range(len(spectra1)):
            suma = suma + math.pow(spectra1[i] - spectra2[i], 2)
        return math.sqrt(suma)
    elif option == 2:
        for i in range(len(spectra1)):
            suma = suma + math.pow(spectra1[i] - spectra2[i], 2)
        return suma
    else:
        print("opción inválida")


def spectra_pow2(vector):
    vector_r = []
    for i in range(len(vector)):
        vector_r.append(math.pow(vector[i], 2))
    return vector_r


def angle(vector1, vector2):
    """Esta operación obtiene el ángulo entre vectores interválicos (Scott y Isaacson, 1998)
    :param vector1: vector interválico del conjunto A
    :param vector2: vector interválico del conjunto B
    :return: ángulo entre los vectores y la distancia euclidiana aprovechando la conversión polar
    """
    leng = len(vector1)
    mag_x = 0
    mag_y = 0
    norm_x = []
    norm_y = []
    cos = 0
    for i in range(leng):
        mag_x = mag_x + math.pow(vector1[i], 2)
        mag_y = mag_y + math.pow(vector2[i], 2)
    mag_x = math.sqrt(mag_x)
    mag_y = math.sqrt(mag_y)
    for i in range(leng):
        norm_x.append(vector1[i]/mag_x)
        norm_y.append(vector2[i]/mag_y)
    for i in range(leng):
        cos = cos + norm_x[i] * norm_y[i]
    if cos > 1:
        cos = 1
    a = float('{0:.3g}'.format((math.acos(cos) * 180) / math.pi))
    b = float('{0:.3g}'.format(math.sqrt(mag_x**2 + mag_y**2 - (2*mag_x*mag_y*cos))))
    return a, b


def convertir_a_midi(conjunto):
    """ A partir de un acorde de Music21 se genera una lista con las alturas MIDI
    :param conjunto: Acorde Music21
    :return: lista de alturas MIDI
    """
    disp = []
    for i in conjunto:
        disp.append(i.pitch.midi)
    return disp


def convertir_a_permutacion(conjunto):
    """ Toma un listado de alturas MIDI para convertirlo en una conjunto sin repetición y con una abstracción de la 
    disposición
    :param conjunto: conjunto de alturas MIDI 
    :return: lista de clases de altura en permutación
    """
    disp = []
    for i in conjunto:
        disp.append(i % 12)
    salida = []
    for i in disp:
        if i not in salida:
            salida.append(i)
    return salida


def relacion_tn_tni_q(forte1, forte2):
    lenf1 = len(forte1)
    lenf2 = len(forte2)
    if forte1 == forte2:
        return 1
    elif lenf1 == lenf2:
        counter = 0
        if ("A" in forte1 or "B" in forte1) and ("A" in forte2 or "B" in forte2):
            if "A" in forte1:
                poslet1 = forte1.find("A")
            else:
                poslet1 = forte1.find("B")
            """if "A" in forte2:
                poslet2 = forte2.find("A")
            else:
                poslet2 = forte2.find("B")"""
            for i in range(poslet1):
                if forte1[i] == forte2[i]:
                    counter += 1
            if poslet1 == counter:
                return 2
            else:
                return 3
        else:
            return 3
    else:
        return 3


def cuantificar_q(conjunto1, conjunto2):
    return red.obtener_valor_en_matriz(conjunto1, conjunto2)


def comparar_mismo_largo(conjunto1, conjunto2):
    conteo = 0
    for i in conjunto1:
        if i in conjunto2:
            conteo += 1
    return conteo


def cuantificar_tn(conjunto1, conjunto2):
    return (conjunto2[0]-conjunto1[0]) % 12


def cuantificar_tni(conjunto1, conjunto2):
    return (conjunto1[0] + conjunto2[len(conjunto2)-1]) % 12

print("La red de relaciones se está cargando...")
red = An.RedTransitiva()
red.cargar_matriz()
print("red cargada")
