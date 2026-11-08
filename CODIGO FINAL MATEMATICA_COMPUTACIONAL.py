import random
import tkinter as tk
from tkinter import ttk

import networkx as nx
import matplotlib
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

CANTI_MINNODOS = 7
CANTI_MAXNODOS = 16
PESO_MIN = 1
PESO_MAX = 20
PESO_MAX_PERMITIDO = 100
PROBABILIDAD_ARISTA = 0.25
INFINITO = float("inf")

COLOR_FONDO = "#EEF9F6"
COLOR_PANEL = "#FFFFFF"
COLOR_MENTA = "#76D7C4"
COLOR_MENTA_CLARO = "#D6F3EC"
COLOR_MENTA_OSCURO = "#5CC4AE"
COLOR_BARRA = "#76D7C4"
COLOR_TEXTO_BARRA = "#0F3D36"
COLOR_ACENTO = "#1F7A69"
COLOR_DESACTIVADO = "#CBE9E2"
COLOR_LINEA = "#BFE6DC"
COLOR_ENCABEZADO = "#D6F3EC"
COLOR_TEXTO = "#1C2B29"
COLOR_NODO = "#EAF8F4"
COLOR_BORDE_NODO = "#2B7A6B"
COLOR_ORIGEN = "#1E9E84"
COLOR_DESTINO = "#E76F51"
COLOR_NODOCAMINO = "#E9C46A"
COLOR_NODOACTUAL = "#F4A261"
COLOR_VISITADO = "#A8E2D5"
COLOR_ARISTA = "#B4C7C2"
COLOR_ARISTAREVISADA = "#E07A2F"
COLOR_BRILLO_REVISADA = "#FCE3CC"
COLOR_CAMINO = "#B23A48"
COLOR_BRILLO_CAMINO = "#F2D0D5"
COLOR_FILA_ACTUAL = "#FCE9D6"
COLOR_FILA_CAMINO = "#FBF1D3"
COLOR_ERROR = "#B23A48"
COLOR_OK = "#1F7A69"
FUENTE = "Century Gothic"
FUENTE_CODIGO = "Consolas"

matplotlib.rcParams["font.family"] = ["Century Gothic", "Segoe UI", "DejaVu Sans"]

def tipoGrafo(grafo):
    if grafo.is_directed():
        return "dirigido"
    else:
        return "no dirigido"

def simbolo_arista(grafo):
    if grafo.is_directed():
        return " -> "
    else:
        return " -- "


def existe_camino(grafo, nodo_inicio, nodo_fin):
    nodos_visitados = set()
    pila_pendientes = [nodo_inicio]
    while pila_pendientes:
        nodo_actual = pila_pendientes.pop()
        if nodo_actual == nodo_fin:
            return True
        if nodo_actual in nodos_visitados:
            continue
        nodos_visitados.add(nodo_actual)
        for vecino in grafo.successors(nodo_actual):
            if vecino not in nodos_visitados:
                pila_pendientes.append(vecino)
    return False


def crear_grafo(cantidad_nodos, dirigidos):
    if dirigidos:
        grafo = nx.DiGraph()
    else:
        grafo = nx.Graph()

    for i in range(1, cantidad_nodos + 1):
        grafo.add_node(i)

    return grafo

def grafo_aleatorio(cantidad_nodos, dirigidos):
    grafo = crear_grafo(cantidad_nodos, dirigidos)
    orden_nodos = list(range(1, cantidad_nodos + 1))
    random.shuffle(orden_nodos)

    for posicion in range(1, cantidad_nodos):
        nodo_destino = orden_nodos[posicion]
        nodo_origen = orden_nodos[random.randint(0, posicion - 1)]
        peso = random.randint(PESO_MIN, PESO_MAX)
        grafo.add_edge(nodo_origen, nodo_destino, weight=peso)

    for i in range(cantidad_nodos):
        for j in range(i + 1, cantidad_nodos):
            nodo_u = orden_nodos[i]
            nodo_v = orden_nodos[j]
            if grafo.has_edge(nodo_u, nodo_v) or grafo.has_edge(nodo_v, nodo_u):
                continue
            if random.random() < PROBABILIDAD_ARISTA:
                peso = random.randint(PESO_MIN, PESO_MAX)
                grafo.add_edge(nodo_u, nodo_v, weight=peso)
    return grafo


def Valitexto_peso(texto_peso):
    texto_peso = texto_peso.strip()
    if texto_peso.startswith("-"):
        return None, "No se aceptan pesos negativos."
    if not texto_peso.isdigit():
        return None, "El peso tiene que ser un número entero."
    peso = int(texto_peso)

    if peso < PESO_MIN:
        mensaje = "El peso mínimo es "
        mensaje = mensaje + str(PESO_MIN) + "."

        resultado = (None, mensaje)
        return resultado

    elif peso > PESO_MAX_PERMITIDO:
        mensaje = "El peso máximo es "
        mensaje = mensaje + str(PESO_MAX_PERMITIDO) + "."

        resultado = (None, mensaje)
        return resultado

    else:
        resultado = (peso, None)
        return resultado

def arista_manual(grafo, nodo_origen, nodo_destino, peso):
    if nodo_origen == nodo_destino:
        return False, "Un nodo no puede conectarse consigo mismo."
    if grafo.has_edge(nodo_origen, nodo_destino):
        return False, "Esa arista ya fue agregada."
    if peso < PESO_MIN or peso > PESO_MAX_PERMITIDO:
        return False, ("El peso debe ir de " + str(PESO_MIN) + " a "
                       + str(PESO_MAX_PERMITIDO) + ".")
    if grafo.is_directed() and existe_camino(grafo, nodo_destino, nodo_origen):
        return False, ("No se puede: con esa arista se formaría un ciclo, porque desde "
                       + str(nodo_destino) + " ya se llega a " + str(nodo_origen) + ".")
    grafo.add_edge(nodo_origen, nodo_destino, weight=peso)
    return True, "Se agregó la arista " + str(nodo_origen) + simbolo_arista(grafo) + str(nodo_destino) + "."


def lista_de_aristas_ordenada(grafo):
    lista_de_aristas = []
    for nodo_u, nodo_v in grafo.edges():
        if not grafo.is_directed() and nodo_u > nodo_v:
            nodo_u, nodo_v = nodo_v, nodo_u
        lista_de_aristas.append((nodo_u, nodo_v))
    lista_de_aristas.sort()
    return lista_de_aristas


def ejecutar_dijkstra(grafo, nodo_origen, nodo_destino):
    distancias = {}
    predecesores = {}
    historial = {}
    for nodo in grafo.nodes():
        distancias[nodo] = INFINITO
        predecesores[nodo] = set()
        historial[nodo] = []
    distancias[nodo_origen] = 0
    historial[nodo_origen].append((0, 0, None))

    iteracion_de_visita = {}
    pasos = [{
        "nodo": None,
        "aristas_revisadas": [],
        "mensajes": [
            "Iteración 0: el origen " + str(nodo_origen)
            + " empieza con [0, -] y los demás nodos con ∞."
        ],
    }]

    nodos_sin_visitar = set(grafo.nodes())
    numero_de_iteracion = 0
    while nodos_sin_visitar:
        nodo_actual = None
        menor_distancia = INFINITO
        for nodo in nodos_sin_visitar:
            if distancias[nodo] < menor_distancia:
                menor_distancia = distancias[nodo]
                nodo_actual = nodo

        if nodo_actual is None:
            pasos[-1]["mensajes"].append(
                "No se puede llegar a los nodos que faltan. Fin del algoritmo."
            )
            break

        numero_de_iteracion += 1
        nodos_sin_visitar.remove(nodo_actual)
        iteracion_de_visita[nodo_actual] = numero_de_iteracion
        mensajes = [
            "Iteración " + str(numero_de_iteracion) + ": se elige el nodo "
            + str(nodo_actual) + " (distancia " + str(distancias[nodo_actual])
            + ") y su etiqueta queda fija."
        ]
        aristas_revisadas = []

        for nodo_vecino in grafo.neighbors(nodo_actual):
            if nodo_vecino not in nodos_sin_visitar:
                continue
            peso_arista = grafo[nodo_actual][nodo_vecino]["weight"]
            distancia_candidata = distancias[nodo_actual] + peso_arista

            if distancia_candidata < distancias[nodo_vecino]:
                if distancias[nodo_vecino] == INFINITO:
                    texto_anterior = "∞"
                else:
                    texto_anterior = str(distancias[nodo_vecino])
                distancias[nodo_vecino] = distancia_candidata
                predecesores[nodo_vecino] = {nodo_actual}
                historial[nodo_vecino].append((numero_de_iteracion, distancia_candidata, nodo_actual))
                aristas_revisadas.append((nodo_actual, nodo_vecino))
                mensajes.append(
                    "   - Nodo " + str(nodo_vecino) + ": " + str(distancias[nodo_actual])
                    + " + " + str(peso_arista) + " = " + str(distancia_candidata)
                    + " es menor que " + texto_anterior + ". Nueva etiqueta ["
                    + str(distancia_candidata) + ", " + str(nodo_actual) + "]"
                )
            elif distancia_candidata == distancias[nodo_vecino]:
                predecesores[nodo_vecino].add(nodo_actual)
                historial[nodo_vecino].append((numero_de_iteracion, distancia_candidata, nodo_actual))
                aristas_revisadas.append((nodo_actual, nodo_vecino))
                mensajes.append(
                    "   - Nodo " + str(nodo_vecino) + ": " + str(distancias[nodo_actual])
                    + " + " + str(peso_arista) + " = " + str(distancia_candidata)
                    + " empata. También se puede llegar desde " + str(nodo_actual)
                )
            else:
                mensajes.append(
                    "   - Nodo " + str(nodo_vecino) + ": " + str(distancias[nodo_actual])
                    + " + " + str(peso_arista) + " = " + str(distancia_candidata)
                    + " no es menor que " + str(distancias[nodo_vecino]) + ". Se queda igual"
                )

        if len(mensajes) == 1:
            mensajes.append("   - No tiene vecinos por revisar.")
        if nodo_actual == nodo_destino:
            mensajes.append("Se llegó al destino " + str(nodo_destino) + ". Fin del algoritmo.")

        pasos.append({
            "nodo": nodo_actual,
            "aristas_revisadas": aristas_revisadas,
            "mensajes": mensajes,
        })
        if nodo_actual == nodo_destino:
            break

    if distancias[nodo_destino] == INFINITO:
        caminos = []
    else:
        caminos = todocaminos_minimos(predecesores, nodo_origen, nodo_destino)

    return {
        "origen": nodo_origen,
        "destino": nodo_destino,
        "distancias": distancias,
        "predecesores": predecesores,
        "historial": historial,
        "iteracion_de_visita": iteracion_de_visita,
        "pasos": pasos,
        "caminos": caminos,
    }


def todocaminos_minimos(predecesores, nodo_origen, nodo_destino):
    todos_los_caminos = []
    camino_en_construccion = [nodo_destino]

    def retroceder(nodo_actual):
        if nodo_actual == nodo_origen:
            camino_completo = list(camino_en_construccion)
            camino_completo.reverse()
            todos_los_caminos.append(camino_completo)
            return
        for nodo_predecesor in predecesores[nodo_actual]:
            camino_en_construccion.append(nodo_predecesor)
            retroceder(nodo_predecesor)
            camino_en_construccion.pop()

    retroceder(nodo_destino)
    return todos_los_caminos


def texto_camino(grafo, camino):
    texto = str(camino[0])
    for posicion in range(1, len(camino)):
        nodo_anterior = camino[posicion - 1]
        nodo_actual = camino[posicion]
        peso = grafo[nodo_anterior][nodo_actual]["weight"]
        if grafo.is_directed():
            texto += " -(" + str(peso) + ")-> " + str(nodo_actual)
        else:
            texto += " -(" + str(peso) + ")- " + str(nodo_actual)
    return texto


def etiqueta_final(historial_del_nodo, iteracion):
    distancia_actual = INFINITO
    predecesores_actuales = []
    for numero, distancia, predecesor in historial_del_nodo:
        if numero > iteracion:
            break
        if distancia < distancia_actual:
            distancia_actual = distancia
            predecesores_actuales = [predecesor]
        else:
            predecesores_actuales.append(predecesor)
    return distancia_actual, predecesores_actuales


def texto_etiqueta(distancia, lista_de_predecesores):
    if distancia == INFINITO:
        return "∞"
    texto_predecesores = ""
    for predecesor in lista_de_predecesores:
        if texto_predecesores != "":
            texto_predecesores += "/"
        if predecesor is None:
            texto_predecesores += "-"
        else:
            texto_predecesores += str(predecesor)
    return str(distancia) + "," + texto_predecesores


def nodos_caminos(caminos):
    nodos = set()
    for camino in caminos:
        for nodo in camino:
            nodos.add(nodo)
    return nodos


def construir_tabla(resultado, hasta_iteracion, mostrar_final):
    historial = resultado["historial"]
    iteracion_de_visita = resultado["iteracion_de_visita"]
    nodos_del_camino = nodos_caminos(resultado["caminos"])

    encabezado = ["Vertice"]
    for iteracion in range(0, hasta_iteracion + 1):
        encabezado.append("Iter " + str(iteracion))
    if mostrar_final:
        encabezado.append("Final")
        encabezado.append("Camino")

    filas = []
    etiquetas_de_fila = []
    for nodo in sorted(historial.keys()):
        fila = [str(nodo)]
        iteracion_permanente = iteracion_de_visita.get(nodo)
        for iteracion in range(0, hasta_iteracion + 1):
            distancia, lista_predecesores = etiqueta_final(historial[nodo], iteracion)
            texto_celda = texto_etiqueta(distancia, lista_predecesores)
            if iteracion_permanente is not None and iteracion == iteracion_permanente:
                texto_celda += "*"
            elif iteracion_permanente is not None and iteracion > iteracion_permanente:
                texto_celda = ""
            fila.append(texto_celda)

        etiqueta = ""
        if mostrar_final:
            distancia, lista_predecesores = etiqueta_final(historial[nodo], hasta_iteracion)
            texto_final = texto_etiqueta(distancia, lista_predecesores)
            if iteracion_permanente is not None:
                texto_final += "*"
            fila.append(texto_final)
            if nodo in nodos_del_camino:
                fila.append("Si")
                etiqueta = "camino"
            else:
                fila.append("")
        elif iteracion_permanente == hasta_iteracion:
            etiqueta = "actual"
        filas.append(fila)
        etiquetas_de_fila.append(etiqueta)
    return encabezado, filas, etiquetas_de_fila


def separar_aristas(grafo, aristas_marcadas):
    aristas_normales = []
    aristas_especiales = []
    pesos_normales = {}
    pesos_especiales = {}
    for nodo_u, nodo_v, datos in grafo.edges(data=True):
        esta_marcada = (nodo_u, nodo_v) in aristas_marcadas
        if not grafo.is_directed() and (nodo_v, nodo_u) in aristas_marcadas:
            esta_marcada = True
        if esta_marcada:
            aristas_especiales.append((nodo_u, nodo_v))
            pesos_especiales[(nodo_u, nodo_v)] = datos["weight"]
        else:
            aristas_normales.append((nodo_u, nodo_v))
            pesos_normales[(nodo_u, nodo_v)] = datos["weight"]
    return aristas_normales, aristas_especiales, pesos_normales, pesos_especiales


def posicion_pesos(grafo):
    if grafo.is_directed():
        return 0.3
    return 0.38


def limitar(valor, minimo, maximo):
    if valor < minimo:
        return minimo
    if valor > maximo:
        return maximo
    return valor


def calcular_medidas(eje, cantidad_nodos):
    caja = eje.get_window_extent()
    puntos_por_pixel = 72.0 / eje.figure.dpi
    ancho_pts = caja.width * puntos_por_pixel
    alto_pts = caja.height * puntos_por_pixel

    margen_vertical = 28
    margen_horizontal = 55
    ancho_leyenda = 125

    radio = (alto_pts - 2 * margen_vertical) / 2
    if ancho_pts / 2 - margen_horizontal < radio:
        radio = ancho_pts / 2 - margen_horizontal
    if radio < 30:
        radio = 30

    estiramiento = limitar((ancho_pts / 2 - margen_horizontal - ancho_leyenda) / radio, 1.0, 1.7)

    separacion_entre_nodos = 2 * 3.1416 * radio / max(cantidad_nodos, 1)
    diametro = limitar(0.45 * separacion_entre_nodos, 15, 34)

    return {
        "limite_x": (ancho_pts / 2) / (radio * estiramiento),
        "limite_y": (alto_pts / 2) / radio,
        "diametro": diametro,
        "letra_nodo": limitar(diametro * 0.42, 7.5, 12),
        "letra_peso": limitar(diametro * 0.28, 6.5, 9),
        "letra_etiqueta": limitar(diametro * 0.3, 7, 9.5),
        "ancho_arista": limitar(diametro * 0.04, 0.8, 1.4),
    }


def tamanos_de_nodos(grafo, nodos_grandes, medidas):
    tamanos = []
    for nodo in grafo.nodes():
        if nodo in nodos_grandes:
            tamanos.append((medidas["diametro"] * 1.25) ** 2)
        else:
            tamanos.append(medidas["diametro"] ** 2)
    return tamanos


def aristas_base(eje, grafo, posiciones, aristas, pesos, opacidad, tamanos, medidas):
    nx.draw_networkx_edges(
        grafo, posiciones, edgelist=aristas, ax=eje, nodelist=list(grafo.nodes()),
        arrows=True, arrowsize=medidas["diametro"] * 0.45, edge_color=COLOR_ARISTA,
        width=medidas["ancho_arista"], alpha=opacidad, node_size=tamanos,
    )
    nx.draw_networkx_edge_labels(
        grafo, posiciones, edge_labels=pesos, ax=eje,
        font_size=medidas["letra_peso"], label_pos=posicion_pesos(grafo),
        font_color=COLOR_TEXTO, alpha=opacidad, rotate=False,
        bbox=dict(boxstyle="round,pad=0.15", facecolor="white",
                  edgecolor=COLOR_ARISTA, alpha=opacidad),
    )


def aristas_resaltadas(eje, grafo, posiciones, aristas, pesos, color, color_brillo,
                               tamanos, medidas):
    if not aristas:
        return
    nx.draw_networkx_edges(
        grafo, posiciones, edgelist=aristas, ax=eje, nodelist=list(grafo.nodes()),
        arrows=True, arrowstyle="-", edge_color=color_brillo,
        width=medidas["diametro"] * 0.28, node_size=tamanos,
    )
    nx.draw_networkx_edges(
        grafo, posiciones, edgelist=aristas, ax=eje, nodelist=list(grafo.nodes()),
        arrows=True, arrowsize=medidas["diametro"] * 0.6, edge_color=color,
        width=medidas["diametro"] * 0.1, node_size=tamanos,
    )
    nx.draw_networkx_edge_labels(
        grafo, posiciones, edge_labels=pesos, ax=eje,
        font_size=medidas["letra_peso"] + 1, font_weight="bold",
        label_pos=posicion_pesos(grafo), font_color="white", rotate=False,
        bbox=dict(boxstyle="round,pad=0.25", facecolor=color, edgecolor="white"),
    )


def dibujar_nodos(eje, grafo, posiciones, colores, bordes, nodos_grandes, tamanos, medidas):
    lista_colores = []
    lista_bordes = []
    grosores = []
    for nodo in grafo.nodes():
        lista_colores.append(colores[nodo])
        lista_bordes.append(bordes[nodo])
        if nodo in nodos_grandes:
            grosores.append(3)
        else:
            grosores.append(2)
    nx.draw_networkx_nodes(
        grafo, posiciones, nodelist=list(grafo.nodes()), ax=eje, node_size=tamanos,
        node_color=lista_colores, edgecolors=lista_bordes, linewidths=grosores,
    )
    nx.draw_networkx_labels(
        grafo, posiciones, ax=eje, font_size=medidas["letra_nodo"],
        font_weight="bold", font_color=COLOR_TEXTO,
    )


def textos_juntonodos(eje, posiciones, textos, colores_de_texto, nodos_grandes, medidas):
    for nodo in textos:
        x, y = posiciones[nodo]
        radio_del_nodo = medidas["diametro"] / 2
        if nodo in nodos_grandes:
            radio_del_nodo = radio_del_nodo * 1.25
        separacion = radio_del_nodo + 3

        if x > 0.35:
            alineacion_horizontal = "left"
        elif x < -0.35:
            alineacion_horizontal = "right"
        else:
            alineacion_horizontal = "center"
        if y > 0.35:
            alineacion_vertical = "bottom"
        elif y < -0.35:
            alineacion_vertical = "top"
        else:
            alineacion_vertical = "center"

        eje.annotate(
            textos[nodo], xy=(x, y), xytext=(x * separacion, y * separacion),
            textcoords="offset points", ha=alineacion_horizontal, va=alineacion_vertical,
            fontsize=medidas["letra_etiqueta"], fontweight="bold",
            color=colores_de_texto[nodo], zorder=5,
        )


def titulo_leyenda(eje, titulo, elementos_de_leyenda, medidas):
    eje.set_title(titulo, fontsize=12, color=COLOR_TEXTO, pad=6)
    if elementos_de_leyenda:
        eje.legend(handles=elementos_de_leyenda, loc="upper right", fontsize=8.5,
                   framealpha=0.95, edgecolor=COLOR_ARISTA, borderaxespad=0.3)
    eje.set_xlim(-medidas["limite_x"], medidas["limite_x"])
    eje.set_ylim(-medidas["limite_y"], medidas["limite_y"])
    eje.axis("off")


def elemen_leyendanodo(color, borde, texto):
    return Line2D([0], [0], marker="o", color="w", markerfacecolor=color,
                  markeredgecolor=borde, markeredgewidth=2, markersize=11, label=texto)


def elemento_leyendarista(color, texto):
    return Line2D([0], [0], color=color, linewidth=4, label=texto)


def dibujar_grafo_sin_resultado(eje, grafo):
    medidas = calcular_medidas(eje, grafo.number_of_nodes())
    posiciones = nx.circular_layout(grafo)
    tamanos = tamanos_de_nodos(grafo, set(), medidas)
    aristas = lista_de_aristas_ordenada(grafo)
    pesos = {}
    for nodo_u, nodo_v in aristas:
        pesos[(nodo_u, nodo_v)] = grafo[nodo_u][nodo_v]["weight"]
    aristas_base(eje, grafo, posiciones, aristas, pesos, 1.0, tamanos, medidas)

    colores = {}
    bordes = {}
    for nodo in grafo.nodes():
        colores[nodo] = COLOR_NODO
        bordes[nodo] = COLOR_BORDE_NODO
    dibujar_nodos(eje, grafo, posiciones, colores, bordes, set(), tamanos, medidas)
    titulo_leyenda(
        eje,
        "Grafo " + tipoGrafo(grafo) + " - " + str(grafo.number_of_nodes())
        + " nodos - " + str(grafo.number_of_edges()) + " aristas",
        [], medidas,
    )


def dibujar_iteracion(eje, grafo, resultado, iteracion):
    medidas = calcular_medidas(eje, grafo.number_of_nodes())
    posiciones = nx.circular_layout(grafo)
    paso = resultado["pasos"][iteracion]
    nodo_actual = paso["nodo"]
    nodo_origen = resultado["origen"]
    nodo_destino = resultado["destino"]
    iteracion_de_visita = resultado["iteracion_de_visita"]

    nodos_grandes = set()
    if nodo_actual is not None:
        nodos_grandes.add(nodo_actual)
    tamanos = tamanos_de_nodos(grafo, nodos_grandes, medidas)

    aristas_normales, aristas_revisadas, pesos_normales, pesos_revisados = separar_aristas(
        grafo, set(paso["aristas_revisadas"])
    )
    aristas_base(eje, grafo, posiciones, aristas_normales, pesos_normales, 0.7,
                         tamanos, medidas)
    aristas_resaltadas(eje, grafo, posiciones, aristas_revisadas, pesos_revisados,
                               COLOR_ARISTAREVISADA, COLOR_BRILLO_REVISADA, tamanos, medidas)

    colores = {}
    bordes = {}
    textos = {}
    colores_de_texto = {}
    for nodo in grafo.nodes():
        es_permanente = nodo in iteracion_de_visita and iteracion_de_visita[nodo] <= iteracion
        if nodo == nodo_actual:
            colores[nodo] = COLOR_NODOACTUAL
        elif nodo == nodo_origen:
            colores[nodo] = COLOR_ORIGEN
        elif es_permanente:
            colores[nodo] = COLOR_VISITADO
        else:
            colores[nodo] = COLOR_NODO
        if nodo == nodo_destino:
            bordes[nodo] = COLOR_CAMINO
        else:
            bordes[nodo] = COLOR_BORDE_NODO

        distancia, lista_predecesores = etiqueta_final(
            resultado["historial"][nodo], iteracion
        )
        if distancia == INFINITO:
            textos[nodo] = "∞"
        else:
            textos[nodo] = "[" + texto_etiqueta(distancia, lista_predecesores) + "]"
        if es_permanente:
            textos[nodo] += "*"
            colores_de_texto[nodo] = COLOR_TEXTO
        else:
            colores_de_texto[nodo] = COLOR_BORDE_NODO

    dibujar_nodos(eje, grafo, posiciones, colores, bordes, nodos_grandes, tamanos, medidas)
    textos_juntonodos(eje, posiciones, textos, colores_de_texto, nodos_grandes, medidas)

    if nodo_actual is None:
        titulo = "Iteración 0 - inicio en el nodo " + str(nodo_origen)
    else:
        titulo = "Iteración " + str(iteracion) + " - nodo elegido: " + str(nodo_actual)
    titulo_leyenda(eje, titulo, [
        elemen_leyendanodo(COLOR_ORIGEN, COLOR_BORDE_NODO, "Origen"),
        elemen_leyendanodo(COLOR_NODO, COLOR_CAMINO, "Destino"),
        elemen_leyendanodo(COLOR_NODOACTUAL, COLOR_BORDE_NODO, "Nodo que se visita"),
        elemen_leyendanodo(COLOR_VISITADO, COLOR_BORDE_NODO, "Ya visitado (*)"),
        elemento_leyendarista(COLOR_ARISTAREVISADA, "Etiqueta actualizada"),
    ], medidas)


def drawresultados(eje, grafo, resultado):
    medidas = calcular_medidas(eje, grafo.number_of_nodes())
    posiciones = nx.circular_layout(grafo)
    caminos = resultado["caminos"]
    distancias = resultado["distancias"]
    nodo_origen = resultado["origen"]
    nodo_destino = resultado["destino"]

    aristas_del_camino = set()
    for camino in caminos:
        for posicion in range(len(camino) - 1):
            aristas_del_camino.add((camino[posicion], camino[posicion + 1]))
    nodos_del_camino = nodos_caminos(caminos)
    tamanos = tamanos_de_nodos(grafo, nodos_del_camino, medidas)

    aristas_normales, aristas_camino, pesos_normales, pesos_resaltados = separar_aristas(
        grafo, aristas_del_camino
    )
    if caminos:
        opacidad = 0.35
    else:
        opacidad = 1.0
    aristas_base(eje, grafo, posiciones, aristas_normales, pesos_normales, opacidad,
                         tamanos, medidas)
    aristas_resaltadas(eje, grafo, posiciones, aristas_camino, pesos_resaltados,
                               COLOR_CAMINO, COLOR_BRILLO_CAMINO, tamanos, medidas)

    colores = {}
    bordes = {}
    textos = {}
    colores_de_texto = {}
    for nodo in grafo.nodes():
        if nodo == nodo_origen:
            colores[nodo] = COLOR_ORIGEN
        elif nodo == nodo_destino:
            colores[nodo] = COLOR_DESTINO
        elif nodo in nodos_del_camino:
            colores[nodo] = COLOR_NODOCAMINO
        else:
            colores[nodo] = COLOR_NODO
        if nodo in nodos_del_camino:
            bordes[nodo] = COLOR_CAMINO
            colores_de_texto[nodo] = COLOR_CAMINO
        else:
            bordes[nodo] = COLOR_BORDE_NODO
            colores_de_texto[nodo] = COLOR_BORDE_NODO
        if distancias[nodo] == INFINITO:
            textos[nodo] = "d=∞"
        else:
            textos[nodo] = "d=" + str(distancias[nodo])

    dibujar_nodos(eje, grafo, posiciones, colores, bordes, nodos_del_camino, tamanos, medidas)
    textos_juntonodos(eje, posiciones, textos, colores_de_texto, nodos_del_camino, medidas)

    if caminos:
        titulo = "Camino mínimo de " + str(nodo_origen) + " a " + str(nodo_destino)
        leyenda = [
            elemen_leyendanodo(COLOR_ORIGEN, COLOR_CAMINO, "Origen"),
            elemen_leyendanodo(COLOR_DESTINO, COLOR_CAMINO, "Destino"),
            elemen_leyendanodo(COLOR_NODOCAMINO, COLOR_CAMINO, "Nodo intermedio"),
            elemento_leyendarista(COLOR_CAMINO, "Camino minimo"),
        ]
    else:
        titulo = "No hay camino de " + str(nodo_origen) + " a " + str(nodo_destino)
        leyenda = []
    titulo_leyenda(eje, titulo, leyenda, medidas)


def franja_pixeles(cantidad_de_caminos):
    return 34 + 58 * cantidad_de_caminos


def franja_caminos(eje, grafo, resultado):
    caminos = resultado["caminos"]
    nodo_destino = resultado["destino"]

    if grafo.is_directed():
        estilo_flecha = "-|>"
    else:
        estilo_flecha = "-"

    diametro = 24
    radio = diametro / 2

    largo_maximo = 0
    for camino in caminos:
        if len(camino) > largo_maximo:
            largo_maximo = len(camino)
    numero_camino = 0

    for camino in caminos:
        y = -numero_camino
        numero_camino += 1

        if len(caminos) > 1:
            eje.text(-0.7, y, "Camino " + str(numero_camino), ha="right", va="center",
                     fontsize=9, fontweight="bold", color=COLOR_TEXTO)

        distancia_acumulada = 0
        for posicion in range(len(camino)):
            nodo = camino[posicion]
            if posicion > 0:
                peso = grafo[camino[posicion - 1]][nodo]["weight"]
                distancia_acumulada += peso
                eje.annotate(
                    "", xy=(posicion, y), xytext=(posicion - 1, y),
                    arrowprops=dict(arrowstyle=estilo_flecha, color=COLOR_CAMINO, lw=2.2,
                                    shrinkA=radio + 2, shrinkB=radio + 2, mutation_scale=16),
                )
                eje.text(posicion - 0.5, y, "+" + str(peso), ha="center", va="center",
                         fontsize=8.5, fontweight="bold", color=COLOR_CAMINO, zorder=4,
                         bbox=dict(boxstyle="round,pad=0.15", facecolor="white",
                                   edgecolor="none"))

            if posicion == 0:
                color = COLOR_ORIGEN
            elif nodo == nodo_destino:
                color = COLOR_DESTINO
            else:
                color = COLOR_NODOCAMINO
            eje.scatter([posicion], [y], s=diametro ** 2, color=color, edgecolors=COLOR_CAMINO,
                        linewidths=2, zorder=3)
            eje.text(posicion, y, str(nodo), ha="center", va="center", fontsize=9.5,
                     fontweight="bold", color=COLOR_TEXTO, zorder=4)
            eje.annotate("d=" + str(distancia_acumulada), xy=(posicion, y),
                         xytext=(0, -(radio + 2)), textcoords="offset points",
                         ha="center", va="top", fontsize=8, color=COLOR_BORDE_NODO,
                         fontweight="bold")

    eje.set_title(
        "Distancia total = " + str(resultado["distancias"][nodo_destino]),
        fontsize=11, fontweight="bold", color=COLOR_CAMINO, pad=3,
    )
    ancho_visible = max(largo_maximo, 7)
    margen = (ancho_visible - (largo_maximo - 1)) / 2
    margen_izquierdo = margen
    if len(caminos) > 1:
        margen_izquierdo += 0.7
    eje.set_xlim(-margen_izquierdo, largo_maximo - 1 + margen)
    eje.set_ylim(-len(caminos) + 0.3, 0.55)
    eje.set_facecolor("white")
    for borde in eje.spines.values():
        borde.set_color(COLOR_CAMINO)
        borde.set_linewidth(1.5)
    eje.set_xticks([])
    eje.set_yticks([])


class AplicacionDijkstra:
    def __init__(self, ventana):
        self.ventana = ventana
        self.grafo = None
        self.resultado = None
        self.paso_actual = 0
        self.aristas_en_lista = []
        self.redibujo_pendiente = None

        self.tipo_de_grafo = tk.StringVar(value="dirigido")
        self.cantidad_nodos = tk.StringVar(value="8")
        self.arista_origen = tk.StringVar(value="1")
        self.arista_destino = tk.StringVar(value="2")
        self.arista_peso = tk.StringVar(value="5")
        self.nodo_origen = tk.StringVar(value="1")
        self.nodo_destino = tk.StringVar(value="2")
        self.texto_paso = tk.StringVar(value="Aun no se ejecuta el algoritmo.")
        self.texto_resultado = tk.StringVar(value="")
        self.texto_mensaje = tk.StringVar(value="")

        self.configurar_ventana()
        self.configurar_estilos()
        self.barra_superior()
        self.construir_cuerpo()
        self.generar_aleatorio()

    def configurar_ventana(self):
        self.ventana.title("Grupo 2 - Camino minimo (Dijkstra)")
        self.ventana.geometry("1280x760")
        self.ventana.minsize(960, 600)
        try:
            self.ventana.state("zoomed")
        except tk.TclError:
            try:
                self.ventana.attributes("-zoomed", True)
            except tk.TclError:
                pass
        self.ventana.configure(bg=COLOR_FONDO)
        self.ventana.protocol("WM_DELETE_WINDOW", self.cerrar)

    def configurar_estilos(self):
        estilo = ttk.Style(self.ventana)
        estilo.theme_use("clam")
        estilo.configure(".", font=(FUENTE, 10), background=COLOR_FONDO, foreground=COLOR_TEXTO)
        estilo.configure("TFrame", background=COLOR_FONDO)
        estilo.configure("Panel.TFrame", background=COLOR_PANEL)
        estilo.configure("TLabelframe", background=COLOR_PANEL, bordercolor=COLOR_LINEA)
        estilo.configure("TLabelframe.Label", background=COLOR_PANEL, foreground=COLOR_ACENTO,
                         font=(FUENTE, 10, "bold"))
        estilo.configure("TLabel", background=COLOR_PANEL)
        estilo.configure("Paso.TLabel", background=COLOR_PANEL, foreground=COLOR_ACENTO,
                         font=(FUENTE, 10, "bold"))
        estilo.configure("Resultado.TLabel", background=COLOR_PANEL, foreground=COLOR_CAMINO,
                         font=(FUENTE, 10, "bold"))
        estilo.configure("TRadiobutton", background=COLOR_PANEL)
        estilo.configure("TButton", padding=(8, 5))
        estilo.configure("Accion.TButton", background=COLOR_MENTA, foreground=COLOR_TEXTO_BARRA,
                         font=(FUENTE, 10, "bold"), padding=(8, 7), bordercolor=COLOR_MENTA_OSCURO)
        estilo.map("Accion.TButton", background=[("active", COLOR_MENTA_OSCURO), ("disabled", COLOR_DESACTIVADO)])
        estilo.map("TButton", background=[("active", COLOR_MENTA_CLARO)])
        estilo.map("TNotebook.Tab", background=[("selected", COLOR_MENTA_CLARO)])
        estilo.configure("Treeview", rowheight=22, font=(FUENTE_CODIGO, 10))
        estilo.map("Treeview", background=[("selected", COLOR_MENTA)], foreground=[("selected", COLOR_TEXTO_BARRA)])
        estilo.configure("Treeview.Heading", font=(FUENTE, 10, "bold"),
                         background=COLOR_ENCABEZADO, foreground=COLOR_TEXTO)
        estilo.configure("TNotebook", background=COLOR_FONDO)
        estilo.configure("TNotebook.Tab", padding=(14, 5), font=(FUENTE, 10, "bold"))

    def barra_superior(self):
        barra = tk.Frame(self.ventana, bg=COLOR_BARRA, height=46)
        barra.pack(side="top", fill="x")
        tk.Label(barra, text="Problema del camino mínimo - Algoritmo de Dijkstra",
                 bg=COLOR_BARRA, fg=COLOR_TEXTO_BARRA, font=(FUENTE, 15, "bold")).pack(side="left", padx=16, pady=6)

    def construir_cuerpo(self):
        cuerpo = ttk.Frame(self.ventana)
        cuerpo.pack(side="top", fill="both", expand=True, padx=8, pady=8)

        panel_controles = ttk.Frame(cuerpo, style="Panel.TFrame", padding=8)
        panel_controles.pack(side="right", fill="y", padx=(12, 0))

        self.constseccion_grafo(panel_controles)
        self.construir_aristas(panel_controles)
        self.construir_dijkstra(panel_controles)

        self.etiqueta_mensaje = tk.Label(
            panel_controles,
            textvariable=self.texto_mensaje,
            bg=COLOR_PANEL,
            fg=COLOR_OK,
            wraplength=280,
            justify="left",
            font=(FUENTE, 9, "bold")
        )
        self.etiqueta_mensaje.pack(fill="x", pady=(6, 0))

        zona_principal = tk.Frame(cuerpo, bg=COLOR_FONDO)
        zona_principal.pack(side="left", fill="both", expand=True)

        tk.Label(
            zona_principal,
            text="VISUALIZACIÓN Y RESULTADOS",
            font=(FUENTE, 14, "bold"),
            bg=COLOR_FONDO,
            fg=COLOR_ACENTO
        ).pack(fill="x", pady=(2, 4))

        self.division_vertical = ttk.PanedWindow(zona_principal, orient="vertical")
        self.division_vertical.pack(fill="both", expand=True, padx=2, pady=2)

        marco_grafo = tk.LabelFrame(
            self.division_vertical,
            text=" Representación del grafo ",
            font=(FUENTE, 11, "bold"),
            bg="white", fg=COLOR_ACENTO, padx=5, pady=5, relief="solid", bd=1, highlightbackground=COLOR_LINEA
        )
        marco_resultados = tk.LabelFrame(
            self.division_vertical,
            text=" Análisis de Dijkstra ",
            font=(FUENTE, 11, "bold"),
            bg="white", fg=COLOR_ACENTO, padx=5, pady=5, relief="solid", bd=1, highlightbackground=COLOR_LINEA
        )

        self.division_vertical.add(marco_grafo, weight=5)
        self.division_vertical.add(marco_resultados, weight=2)

        self.area_grafo(marco_grafo)
        self.construir_tablas(marco_resultados)

        self.ventana.after(300, self.ajustar_division)
        self.ventana.after(1000, self.ajustar_division)

    def ajustar_division(self):
        alto = self.division_vertical.winfo_height()
        if alto > 100:
            posicion = int(alto * 0.64)
            if alto - posicion < 250:
                posicion = alto - 250
            if posicion < 280:
                posicion = 280
            self.division_vertical.sashpos(0, posicion)


    def constseccion_grafo(self, contenedor):
        seccion = ttk.LabelFrame(contenedor, text="1. Grafo", padding=6)
        seccion.pack(fill="x", pady=(0, 6))

        fila_tipo = ttk.Frame(seccion, style="Panel.TFrame")
        fila_tipo.pack(fill="x")
        ttk.Radiobutton(fila_tipo, text="Dirigido", value="dirigido",
                        variable=self.tipo_de_grafo, command=self.cambiar_tipo).pack(side="left")
        ttk.Radiobutton(fila_tipo, text="No dirigido", value="no dirigido",
                        variable=self.tipo_de_grafo, command=self.cambiar_tipo).pack(side="left", padx=12)

        fila_nodos = ttk.Frame(seccion, style="Panel.TFrame")
        fila_nodos.pack(fill="x", pady=4)
        ttk.Label(fila_nodos, text="Cantidad de nodos (" + str(CANTI_MINNODOS)
                  + " a " + str(CANTI_MAXNODOS) + "):").pack(side="left")
        ttk.Spinbox(fila_nodos, from_=CANTI_MINNODOS, to=CANTI_MAXNODOS,
                    textvariable=self.cantidad_nodos, width=5).pack(side="left", padx=6)

        fila_botones = ttk.Frame(seccion, style="Panel.TFrame")
        fila_botones.pack(fill="x")
        ttk.Button(fila_botones, text="Generar aleatorio", style="Accion.TButton",
                   command=self.generar_aleatorio).pack(side="left", fill="x", expand=True)
        ttk.Button(fila_botones, text="Grafo vacío (manual)",
                   command=self.crear_vacio).pack(side="left", fill="x", expand=True, padx=(6, 0))

    def construir_aristas(self, contenedor):
        seccion = ttk.LabelFrame(contenedor, text="2. Aristas", padding=6)
        seccion.pack(fill="x", pady=(0, 6))

        fila_datos = ttk.Frame(seccion, style="Panel.TFrame")
        fila_datos.pack(fill="x")
        ttk.Label(fila_datos, text="Origen").pack(side="left")
        self.spin_arista_origen = ttk.Spinbox(fila_datos, from_=1, to=CANTI_MAXNODOS,
                                              textvariable=self.arista_origen, width=4)
        self.spin_arista_origen.pack(side="left", padx=(3, 8))
        ttk.Label(fila_datos, text="Destino").pack(side="left")
        self.spin_arista_destino = ttk.Spinbox(fila_datos, from_=1, to=CANTI_MAXNODOS,
                                               textvariable=self.arista_destino, width=4)
        self.spin_arista_destino.pack(side="left", padx=(3, 8))
        ttk.Label(fila_datos, text="Peso").pack(side="left")
        ttk.Spinbox(fila_datos, from_=PESO_MIN, to=PESO_MAX_PERMITIDO, textvariable=self.arista_peso,
                    width=4).pack(side="left", padx=(3, 0))

        fila_botones = ttk.Frame(seccion, style="Panel.TFrame")
        fila_botones.pack(fill="x", pady=4)
        ttk.Button(fila_botones, text="Agregar arista",
                   command=self.agregar_arista).pack(side="left", fill="x", expand=True)
        ttk.Button(fila_botones, text="Quitar seleccionada",
                   command=self.quitar_arista).pack(side="left", fill="x", expand=True, padx=(6, 0))

        marco_lista = ttk.Frame(seccion, style="Panel.TFrame")
        marco_lista.pack(fill="x")
        self.lista_aristas = tk.Listbox(marco_lista, height=5, font=(FUENTE_CODIGO, 10),
                                        activestyle="none", selectbackground=COLOR_MENTA, selectforeground=COLOR_TEXTO_BARRA,
                                        relief="flat", highlightthickness=1,
                                        highlightbackground=COLOR_LINEA)
        barra_lista = ttk.Scrollbar(marco_lista, orient="vertical", command=self.lista_aristas.yview)
        self.lista_aristas.configure(yscrollcommand=barra_lista.set)
        self.lista_aristas.pack(side="left", fill="x", expand=True)
        barra_lista.pack(side="left", fill="y")

    def construir_dijkstra(self, contenedor):
        seccion = ttk.LabelFrame(contenedor, text="3. Dijkstra", padding=6)
        seccion.pack(fill="x")

        fila_nodos = ttk.Frame(seccion, style="Panel.TFrame")
        fila_nodos.pack(fill="x")
        ttk.Label(fila_nodos, text="Origen").pack(side="left")
        self.spin_origen = ttk.Spinbox(fila_nodos, from_=1, to=CANTI_MAXNODOS,
                                       textvariable=self.nodo_origen, width=4)
        self.spin_origen.pack(side="left", padx=(3, 12))
        ttk.Label(fila_nodos, text="Destino").pack(side="left")
        self.spin_destino = ttk.Spinbox(fila_nodos, from_=1, to=CANTI_MAXNODOS,
                                        textvariable=self.nodo_destino, width=4)
        self.spin_destino.pack(side="left", padx=3)

        ttk.Button(seccion, text="Ejecutar Dijkstra", style="Accion.TButton",
                   command=self.ejecutar).pack(fill="x", pady=(6, 4))

        fila_pasos = ttk.Frame(seccion, style="Panel.TFrame")
        fila_pasos.pack(fill="x")
        self.boton_anterior = ttk.Button(fila_pasos, text="Anterior", command=self.paso_anterior)
        self.boton_anterior.pack(side="left", fill="x", expand=True)
        self.boton_siguiente = ttk.Button(fila_pasos, text="Siguiente", command=self.paso_siguiente)
        self.boton_siguiente.pack(side="left", fill="x", expand=True, padx=4)
        self.boton_final = ttk.Button(fila_pasos, text="Ver resultado", command=self.paso_final)
        self.boton_final.pack(side="left", fill="x", expand=True)

        ttk.Label(seccion, textvariable=self.texto_paso, style="Paso.TLabel",
                  wraplength=280).pack(fill="x", pady=(6, 2))
        ttk.Label(seccion, textvariable=self.texto_resultado, style="Resultado.TLabel",
                  wraplength=280, justify="left").pack(fill="x")


    def area_grafo(self, contenedor):
        marco = ttk.Frame(contenedor, style="Panel.TFrame")

        if isinstance(contenedor, ttk.PanedWindow):
            contenedor.add(marco, weight=3)
        else:
            marco.pack(fill="both", expand=True)

        self.figura = Figure(
            figsize=(8, 5),
            dpi=80,
            facecolor="white"
        )

        self.lienzo = FigureCanvasTkAgg(
            self.figura,
            master=marco
        )

        self.lienzo.get_tk_widget().pack(
            fill="both",
            expand=True,
            padx=5,
            pady=5
        )

        self.lienzo.get_tk_widget().bind(
            "<Configure>",
            self.cambiar_tamano,
            add="+"
        )


    def cambiar_tamano(self, evento):
        if self.redibujo_pendiente is not None:
            self.ventana.after_cancel(self.redibujo_pendiente)
        self.redibujo_pendiente = self.ventana.after(150, self.dibujar_vista)

    def dibujar_vista(self):
        self.redibujo_pendiente = None
        if self.grafo is None:
            return
        if self.resultado is None:
            self.dibujargrafo()
        else:
            self.dibujar_paso(self.paso_actual == self.indice_final())

    def crear_eje(self, abajo_en_pixeles, arriba_en_pixeles):
        alto_figura = self.figura.get_figheight() * self.figura.dpi
        abajo = abajo_en_pixeles / alto_figura
        alto = 1 - (abajo_en_pixeles + arriba_en_pixeles) / alto_figura
        if alto < 0.2:
            alto = 0.2
        return self.figura.add_axes([0.01, abajo, 0.98, alto])

    def dibujargrafo(self):
        self.figura.clear()
        dibujar_grafo_sin_resultado(self.crear_eje(6, 30), self.grafo)
        self.lienzo.draw()


    def construir_tablas(self, contenedor):
        pestanas = ttk.Notebook(contenedor)

        pestanas.pack(
            fill="both",
            expand=True,
            padx=5,
            pady=5
        )

        marco_tabla = ttk.Frame(
            pestanas,
            style="Panel.TFrame",
            padding=6
        )

        pestanas.add(marco_tabla, text="Tabla de etiquetas")

        marco_arbol = ttk.Frame(
            marco_tabla,
            style="Panel.TFrame"
        )

        marco_arbol.pack(fill="both", expand=True)

        self.tabla = ttk.Treeview(
            marco_arbol,
            show="headings",
            height=5
        )

        barra_vertical = ttk.Scrollbar(
            marco_arbol,
            orient="vertical",
            command=self.tabla.yview
        )

        barra_horizontal = ttk.Scrollbar(
            marco_arbol,
            orient="horizontal",
            command=self.tabla.xview
        )

        self.tabla.configure(
            yscrollcommand=barra_vertical.set,
            xscrollcommand=barra_horizontal.set
        )

        self.tabla.grid(row=0, column=0, sticky="nsew")
        barra_vertical.grid(row=0, column=1, sticky="ns")
        barra_horizontal.grid(row=1, column=0, sticky="ew")

        marco_arbol.rowconfigure(0, weight=1)
        marco_arbol.columnconfigure(0, weight=1)

        self.tabla.tag_configure(
            "actual",
            background=COLOR_FILA_ACTUAL
        )

        self.tabla.tag_configure(
            "camino",
            background=COLOR_FILA_CAMINO,
            foreground=COLOR_CAMINO
        )

        ttk.Label(
            marco_tabla,
            text="* etiqueta permanente    ∞ sin etiqueta todavía    "
                "a/b dos predecesores con la misma distancia    "
                "Si nodo del camino mínimo",
            font=(FUENTE, 9)
        ).pack(fill="x", pady=(6, 0))

        marco_detalle = ttk.Frame(
            pestanas,
            style="Panel.TFrame",
            padding=6
        )

        pestanas.add(
            marco_detalle,
            text="Detalle paso a paso"
        )

        self.texto_detalle = tk.Text(
            marco_detalle,
            wrap="word",
            font=(FUENTE_CODIGO, 10),
            relief="flat",
            bg="white",
            fg=COLOR_TEXTO,
            padx=8,
            pady=6
        )

        barra_detalle = ttk.Scrollbar(
            marco_detalle,
            orient="vertical",
            command=self.texto_detalle.yview
        )

        self.texto_detalle.configure(
            yscrollcommand=barra_detalle.set,
            state="disabled"
        )

        self.texto_detalle.pack(
            side="left",
            fill="both",
            expand=True
        )

        barra_detalle.pack(
            side="left",
            fill="y"
        )

        self.texto_detalle.tag_configure(
            "titulo",
            font=(FUENTE_CODIGO, 10, "bold"),
            foreground=COLOR_ACENTO
        )

        self.texto_detalle.tag_configure(
            "actual",
            background=COLOR_FILA_ACTUAL
        )

        self.texto_detalle.tag_configure(
            "resultado",
            font=(FUENTE_CODIGO, 11, "bold"),
            foreground=COLOR_CAMINO
        )


    def leer_entero(self, variable):
        texto = variable.get().strip()
        if not texto.isdigit():
            return None
        return int(texto)

    def mostrar_mensaje(self, texto, es_error):
        self.texto_mensaje.set(texto)
        if es_error:
            self.etiqueta_mensaje.configure(fg=COLOR_ERROR)
        else:
            self.etiqueta_mensaje.configure(fg=COLOR_OK)

    def dirigidos(self):
        return self.tipo_de_grafo.get() == "dirigido"

    def leer_cantidad_de_nodos(self):
        cantidad = self.leer_entero(self.cantidad_nodos)
        if cantidad is None or cantidad < CANTI_MINNODOS or cantidad > CANTI_MAXNODOS:
            self.mostrar_mensaje(
                "La cantidad de nodos va de " + str(CANTI_MINNODOS)
                + " a " + str(CANTI_MAXNODOS) + ".", True
            )
            return None
        return cantidad

    def leer_nodo(self, variable, nombre):
        nodo = self.leer_entero(variable)
        if nodo is None or nodo < 1 or nodo > self.grafo.number_of_nodes():
            self.mostrar_mensaje(
                "El " + nombre + " tiene que estar entre 1 y "
                + str(self.grafo.number_of_nodes()) + ".", True
            )
            return None
        return nodo

    def escribir_detalle(self, lineas_con_estilo):
        self.texto_detalle.configure(state="normal")
        self.texto_detalle.delete("1.0", "end")
        for texto, estilo in lineas_con_estilo:
            self.texto_detalle.insert("end", texto + "\n", estilo)
        self.texto_detalle.configure(state="disabled")
        self.texto_detalle.see("end")

    def cambiar_tipo(self):
        self.generar_aleatorio()

    def generar_aleatorio(self):
        cantidad = self.leer_cantidad_de_nodos()
        if cantidad is None:
            return
        self.grafo = grafo_aleatorio(cantidad, self.dirigidos())
        self.modificar_grafo(
            "Se generó un grafo " + tipoGrafo(self.grafo) + " de "
            + str(cantidad) + " nodos y " + str(self.grafo.number_of_edges()) + " aristas.", False
        )

    def crear_vacio(self):
        cantidad = self.leer_cantidad_de_nodos()
        if cantidad is None:
            return
        self.grafo = crear_grafo(cantidad, self.dirigidos())
        self.modificar_grafo("Grafo vacío listo. Ahora agrega las aristas.", False)

    def agregar_arista(self):
        nodo_origen = self.leer_nodo(self.arista_origen, "origen de la arista")
        if nodo_origen is None:
            return
        nodo_destino = self.leer_nodo(self.arista_destino, "destino de la arista")
        if nodo_destino is None:
            return
        peso, motivo = Valitexto_peso(self.arista_peso.get())
        if peso is None:
            self.mostrar_mensaje(motivo, True)
            return
        se_agrego, mensaje = arista_manual(self.grafo, nodo_origen, nodo_destino, peso)
        if se_agrego:
            self.modificar_grafo(mensaje, False)
        else:
            self.mostrar_mensaje(mensaje, True)

    def quitar_arista(self):
        seleccion = self.lista_aristas.curselection()
        if not seleccion:
            self.mostrar_mensaje("Selecciona en la lista la arista que quieres quitar.", True)
            return
        nodo_u, nodo_v = self.aristas_en_lista[seleccion[0]]
        self.grafo.remove_edge(nodo_u, nodo_v)
        self.modificar_grafo(
            "Se quitó la arista " + str(nodo_u) + simbolo_arista(self.grafo) + str(nodo_v) + ".", False
        )

    def modificar_grafo(self, mensaje, es_error):
        self.resultado = None
        cantidad = self.grafo.number_of_nodes()
        self.spin_arista_origen.configure(to=cantidad)
        self.spin_arista_destino.configure(to=cantidad)
        self.spin_origen.configure(to=cantidad)
        self.spin_destino.configure(to=cantidad)

        self.aristas_en_lista = lista_de_aristas_ordenada(self.grafo)
        self.lista_aristas.delete(0, "end")
        for nodo_u, nodo_v in self.aristas_en_lista:
            peso = self.grafo[nodo_u][nodo_v]["weight"]
            self.lista_aristas.insert(
                "end", " " + str(nodo_u).rjust(2) + simbolo_arista(self.grafo)
                + str(nodo_v).rjust(2) + "    peso " + str(peso)
            )

        self.limpiar_tabla()
        self.escribir_detalle([("Aquí aparecerá la explicación de cada iteración.", "")])
        self.texto_paso.set("Todavía no se ejecuta el algoritmo.")
        self.texto_resultado.set("")
        self.actualizar_botones()

        self.dibujargrafo()
        self.mostrar_mensaje(mensaje, es_error)

    def ejecutar(self):
        if self.grafo.number_of_edges() == 0:
            self.mostrar_mensaje("Primero agrega aristas al grafo.", True)
            return
        nodo_origen = self.leer_nodo(self.nodo_origen, "origen")
        if nodo_origen is None:
            return
        nodo_destino = self.leer_nodo(self.nodo_destino, "destino")
        if nodo_destino is None:
            return
        if nodo_origen == nodo_destino:
            self.mostrar_mensaje("El origen y el destino tienen que ser diferentes.", True)
            return
        self.resultado = ejecutar_dijkstra(self.grafo, nodo_origen, nodo_destino)
        self.paso_actual = 0
        self.mostrar_mensaje(
            "Listo. Presiona Siguiente para ver cada iteración.", False
        )
        self.mostrar_paso()

    def indice_final(self):
        return len(self.resultado["pasos"])

    def paso_anterior(self):
        if self.resultado is not None and self.paso_actual > 0:
            self.paso_actual -= 1
            self.mostrar_paso()

    def paso_siguiente(self):
        if self.resultado is not None and self.paso_actual < self.indice_final():
            self.paso_actual += 1
            self.mostrar_paso()

    def paso_final(self):
        if self.resultado is not None:
            self.paso_actual = self.indice_final()
            self.mostrar_paso()

    def actualizar_botones(self):
        if self.resultado is None:
            self.boton_anterior.state(["disabled"])
            self.boton_siguiente.state(["disabled"])
            self.boton_final.state(["disabled"])
            return
        if self.paso_actual == 0:
            self.boton_anterior.state(["disabled"])
        else:
            self.boton_anterior.state(["!disabled"])
        if self.paso_actual >= self.indice_final():
            self.boton_siguiente.state(["disabled"])
            self.boton_final.state(["disabled"])
        else:
            self.boton_siguiente.state(["!disabled"])
            self.boton_final.state(["!disabled"])

    def mostrar_paso(self):
        es_final = self.paso_actual == self.indice_final()
        ultima_iteracion = len(self.resultado["pasos"]) - 1
        if es_final:
            iteracion_de_la_tabla = ultima_iteracion
        else:
            iteracion_de_la_tabla = self.paso_actual

        self.actualizar_botones()
        self.dibujar_paso(es_final)
        self.llenar_tabla(iteracion_de_la_tabla, es_final)
        self.llenar_detalle(iteracion_de_la_tabla, es_final)

        if es_final:
            self.texto_paso.set("Resultado final (" + str(ultima_iteracion) + " iteraciones)")
            self.texto_resultado.set(self.texto_resultados())
        else:
            self.texto_paso.set("Iteración " + str(self.paso_actual) + " de " + str(ultima_iteracion))
            self.texto_resultado.set("")

    def texto_resultados(self):
        caminos = self.resultado["caminos"]
        nodo_origen = self.resultado["origen"]
        nodo_destino = self.resultado["destino"]
        if not caminos:
            return "No hay camino de " + str(nodo_origen) + " a " + str(nodo_destino) + "."
        texto = (
            "Distancia mínima de " + str(nodo_origen) + " a " + str(nodo_destino)
            + ": " + str(self.resultado["distancias"][nodo_destino])
            + "\nCaminos mínimos encontrados: " + str(len(caminos))
        )
        numero_camino = 0
        for camino in caminos:
            numero_camino += 1
            texto += "\nCamino " + str(numero_camino) + ": " + texto_camino(self.grafo, camino)
        return texto

    def dibujar_paso(self, es_final):
        self.figura.clear()
        caminos = self.resultado["caminos"]
        if es_final and caminos:
            alto_franja = franja_pixeles(len(caminos))
            alto_figura = self.figura.get_figheight() * self.figura.dpi
            eje_franja = self.figura.add_axes([
                0.03, 6 / alto_figura, 0.94, (alto_franja - 26) / alto_figura
            ])
            eje_grafo = self.crear_eje(alto_franja + 8, 30)
            drawresultados(eje_grafo, self.grafo, self.resultado)
            franja_caminos(eje_franja, self.grafo, self.resultado)
        elif es_final:
            drawresultados(self.crear_eje(6, 30), self.grafo, self.resultado)
        else:
            dibujar_iteracion(self.crear_eje(6, 30), self.grafo, self.resultado, self.paso_actual)
        self.lienzo.draw()

    def limpiar_tabla(self):
        filas_actuales = self.tabla.get_children()
        if filas_actuales:
            self.tabla.delete(*filas_actuales)
        self.tabla["columns"] = ()

    def llenar_tabla(self, hasta_iteracion, mostrar_final):
        self.limpiar_tabla()
        encabezado, filas, etiquetas_de_fila = construir_tabla(self.resultado, hasta_iteracion, mostrar_final)

        identificadores = []
        for posicion in range(len(encabezado)):
            identificadores.append("c" + str(posicion))
        self.tabla["columns"] = identificadores
        for posicion in range(len(encabezado)):
            self.tabla.heading(identificadores[posicion], text=encabezado[posicion])
            self.tabla.column(identificadores[posicion], width=78, minwidth=60,
                              anchor="center", stretch=False)

        for posicion in range(len(filas)):
            if etiquetas_de_fila[posicion] == "":
                etiquetas = ()
            else:
                etiquetas = (etiquetas_de_fila[posicion],)
            self.tabla.insert("", "end", values=filas[posicion], tags=etiquetas)
        self.tabla.xview_moveto(1.0)

    def llenar_detalle(self, hasta_iteracion, es_final):
        lineas = []
        for iteracion in range(0, hasta_iteracion + 1):
            mensajes = self.resultado["pasos"][iteracion]["mensajes"]
            if iteracion == hasta_iteracion and not es_final:
                estilo_resto = "actual"
            else:
                estilo_resto = ""
            lineas.append((mensajes[0], "titulo"))
            for posicion in range(1, len(mensajes)):
                lineas.append((mensajes[posicion], estilo_resto))
            lineas.append(("", ""))
        if es_final:
            lineas.append(("RESULTADO FINAL", "titulo"))
            lineas.append((self.texto_resultados(), "resultado"))
        self.escribir_detalle(lineas)

    def cerrar(self):
        self.ventana.quit()
        self.ventana.destroy()


def main():
    ventana = tk.Tk()
    AplicacionDijkstra(ventana)
    ventana.mainloop()


if __name__ == "__main__":
    main()