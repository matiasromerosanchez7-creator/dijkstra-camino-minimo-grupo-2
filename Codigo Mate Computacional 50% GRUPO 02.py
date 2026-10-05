import random
import networkx as nx
import matplotlib.pyplot as plt

CANTIDAD_MINIMA_NODOS = 7
CANTIDAD_MAXIMA_NODOS = 16
PESO_MINIMO = 1
PESO_MAXIMO = 20
PROBABILIDAD_ARISTA_EXTRA = 0.25
INFINITO = float("inf")


def imprimir_banner(texto):
    linea = "=" * 60
    print("\n" + linea)
    print(texto)
    print(linea)


def pedir_confirmacion(mensaje):
    """Pide una respuesta si/no por consola. Devuelve True para 's', False para 'n'."""
    while True:
        respuesta = input(mensaje).strip().lower()
        if respuesta in ("s", "si", "sí"):
            return True
        if respuesta in ("n", "no"):
            return False
        print("Respuesta invalida. Escriba s (si) o n (no).")


# ----------------------------------------------------------------------
# LOGICA DEL GRAFO
# ----------------------------------------------------------------------
def existe_camino(grafo, nodo_inicio, nodo_fin):
    """Devuelve True si existe un camino dirigido de nodo_inicio a nodo_fin."""
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


def crear_grafo_vacio(cantidad_nodos):
    """Crea un grafo dirigido con los nodos 1..cantidad_nodos y sin aristas."""
    grafo = nx.DiGraph()
    grafo.add_nodes_from(range(1, cantidad_nodos + 1))
    return grafo


def generar_grafo_aleatorio(cantidad_nodos):
    """
    Genera un grafo dirigido aciclico con cantidad_nodos nodos.

    Se sortea un orden oculto de los nodos y las aristas solo pueden ir de
    un nodo a otro que aparezca despues en ese orden, lo que garantiza que
    no se formen ciclos. Cada nodo (salvo el primero del orden) recibe al
    menos una arista entrante, de modo que todo el grafo queda conectado.
    """
    grafo = crear_grafo_vacio(cantidad_nodos)
    orden_de_los_nodos = list(range(1, cantidad_nodos + 1))
    random.shuffle(orden_de_los_nodos)

    for posicion in range(1, cantidad_nodos):
        nodo_destino = orden_de_los_nodos[posicion]
        posicion_origen = random.randint(0, posicion - 1)
        nodo_origen = orden_de_los_nodos[posicion_origen]
        peso = random.randint(PESO_MINIMO, PESO_MAXIMO)
        grafo.add_edge(nodo_origen, nodo_destino, weight=peso)

    for i in range(cantidad_nodos):
        for j in range(i + 1, cantidad_nodos):
            nodo_u = orden_de_los_nodos[i]
            nodo_v = orden_de_los_nodos[j]
            if not grafo.has_edge(nodo_u, nodo_v):
                if random.random() < PROBABILIDAD_ARISTA_EXTRA:
                    peso = random.randint(PESO_MINIMO, PESO_MAXIMO)
                    grafo.add_edge(nodo_u, nodo_v, weight=peso)
    return grafo


def agregar_arista_manual(grafo, nodo_origen, nodo_destino, peso):
    """
    Intenta agregar la arista nodo_origen -> nodo_destino con el peso dado.
    Devuelve (True, mensaje) si se agrego, o (False, motivo) si no se pudo.
    """
    if nodo_origen == nodo_destino:
        return False, "No se permiten lazos (origen igual a destino)."
    if grafo.has_edge(nodo_origen, nodo_destino):
        return False, "Esa arista ya existe."
    if peso < PESO_MINIMO:
        return False, "El peso debe ser un entero positivo."
    if existe_camino(grafo, nodo_destino, nodo_origen):
        return False, "Esa arista formaria un ciclo; el grafo debe ser aciclico."
    grafo.add_edge(nodo_origen, nodo_destino, weight=peso)
    return True, "Arista agregada correctamente."


# ----------------------------------------------------------------------
# ALGORITMO DE DIJKSTRA, PASO A PASO
# ----------------------------------------------------------------------
def ejecutar_dijkstra_paso_a_paso(grafo, nodo_origen, nodo_destino, mostrar_detalle=True):
    """
    Ejecuta Dijkstra desde nodo_origen, imprimiendo en consola el detalle
    de cada iteracion. Devuelve (distancias, predecesores, historial):
      - distancias: diccionario nodo -> distancia minima desde el origen.
      - predecesores: diccionario nodo -> conjunto de nodos predecesores
        que logran esa distancia minima (puede haber mas de uno, lo que
        permite reconstruir todos los caminos minimos, no solo uno).
      - historial: diccionario nodo -> lista de tuplas
        (iteracion, distancia, predecesor) con cada etiqueta [d, V] que
        recibio ese nodo, en el mismo formato que usa la lectura del
        curso, para poder armar la tabla de resultados al final.
    """
    distancias = {}
    predecesores = {}
    historial = {}
    for nodo in grafo.nodes():
        distancias[nodo] = INFINITO
        predecesores[nodo] = set()
        historial[nodo] = []
    distancias[nodo_origen] = 0
    historial[nodo_origen].append((0, 0, None))

    nodos_sin_visitar = set(grafo.nodes())
    nodos_visitados_en_orden = []

    numero_de_iteracion = 0
    mostrar_cada_paso = mostrar_detalle
    while nodos_sin_visitar:
        numero_de_iteracion += 1

        nodo_actual = None
        menor_distancia = INFINITO
        for nodo in nodos_sin_visitar:
            if distancias[nodo] < menor_distancia:
                menor_distancia = distancias[nodo]
                nodo_actual = nodo

        if nodo_actual is None:
            print(
                "\nIteracion " + str(numero_de_iteracion)
                + ": los nodos restantes son inalcanzables desde el origen. "
                "Se detiene el algoritmo."
            )
            break

        nodos_sin_visitar.remove(nodo_actual)
        nodos_visitados_en_orden.append(nodo_actual)

        if mostrar_cada_paso:
            print(
                "\nIteracion " + str(numero_de_iteracion)
                + " -> se visita el nodo " + str(nodo_actual)
                + " (distancia acumulada: " + str(distancias[nodo_actual]) + ")"
            )

        for nodo_vecino in grafo.successors(nodo_actual):
            if nodo_vecino not in nodos_sin_visitar:
                continue
            peso_arista = grafo[nodo_actual][nodo_vecino]["weight"]
            distancia_candidata = distancias[nodo_actual] + peso_arista

            if distancia_candidata < distancias[nodo_vecino]:
                distancias[nodo_vecino] = distancia_candidata
                predecesores[nodo_vecino] = {nodo_actual}
                historial[nodo_vecino].append(
                    (numero_de_iteracion, distancia_candidata, nodo_actual)
                )
                if mostrar_cada_paso:
                    print(
                        "   Se actualiza el nodo " + str(nodo_vecino)
                        + ": nueva distancia minima = " + str(distancia_candidata)
                        + " (a traves de " + str(nodo_actual) + ")"
                    )
            elif distancia_candidata == distancias[nodo_vecino]:
                predecesores[nodo_vecino].add(nodo_actual)
                historial[nodo_vecino].append(
                    (numero_de_iteracion, distancia_candidata, nodo_actual)
                )
                if mostrar_cada_paso:
                    print(
                        "   Se encuentra otro camino igual de corto hacia "
                        + str(nodo_vecino) + " (distancia = "
                        + str(distancia_candidata) + "), tambien a traves de "
                        + str(nodo_actual)
                    )

        if nodo_actual == nodo_destino:
            if mostrar_cada_paso:
                print(
                    "\nSe alcanzo el nodo destino (" + str(nodo_destino)
                    + "). Se detiene el algoritmo."
                )
            break

        if mostrar_cada_paso and nodos_sin_visitar:
            desea_continuar_paso_a_paso = pedir_confirmacion(
                "\n¿Desea ver la siguiente iteracion paso a paso? (s/n): "
            )
            if not desea_continuar_paso_a_paso:
                mostrar_cada_paso = False
                print(
                    "Se completaran las iteraciones restantes sin mostrar "
                    "el detalle. Solo se mostrara la tabla y el resultado final."
                )

    print("\nOrden en que se visitaron los nodos: " + str(nodos_visitados_en_orden))
    return distancias, predecesores, historial


def imprimir_tabla_de_resultados(historial, nodo_origen):
    """
    Imprime una tabla con las etiquetas [distancia, predecesor] que
    recibio cada vertice en cada iteracion, en el mismo formato que
    presenta la lectura del curso (una columna por iteracion).
    """
    mayor_iteracion = 0
    for nodo in historial:
        for iteracion, distancia, predecesor in historial[nodo]:
            if iteracion > mayor_iteracion:
                mayor_iteracion = iteracion

    nodos_ordenados = sorted(historial.keys())

    ancho_columna_nodo = 8
    ancho_columna_iteracion = 12

    encabezado = "Vertice".ljust(ancho_columna_nodo)
    for iteracion in range(0, mayor_iteracion + 1):
        encabezado += ("Iter. " + str(iteracion)).ljust(ancho_columna_iteracion)
    print(encabezado)
    print("-" * (ancho_columna_nodo + ancho_columna_iteracion * (mayor_iteracion + 1)))

    for nodo in nodos_ordenados:
        fila = str(nodo).ljust(ancho_columna_nodo)
        etiquetas_por_iteracion = {}
        for iteracion, distancia, predecesor in historial[nodo]:
            texto_predecesor = "-" if predecesor is None else str(predecesor)
            etiquetas_por_iteracion[iteracion] = str(distancia) + "," + texto_predecesor

        for iteracion in range(0, mayor_iteracion + 1):
            texto_celda = etiquetas_por_iteracion.get(iteracion, "")
            fila += texto_celda.ljust(ancho_columna_iteracion)
        print(fila)


def reconstruir_todos_los_caminos_minimos(predecesores, nodo_origen, nodo_destino):
    """
    A partir del diccionario de predecesores (uno o varios por nodo),
    reconstruye por backtracking TODAS las secuencias de vertices que
    logran la distancia minima entre nodo_origen y nodo_destino.
    """
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


# ----------------------------------------------------------------------
# DIBUJO
# ----------------------------------------------------------------------
def dibujar_grafo(grafo, aristas_resaltadas=None):
    """
    Muestra el grafo en una ventana de Matplotlib, con nodos y pesos.
    Si se pasa aristas_resaltadas (conjunto de tuplas (u, v)), esas
    aristas se dibujan en otro color para marcar el camino minimo.
    """
    if aristas_resaltadas is None:
        aristas_resaltadas = set()

    posiciones_de_nodos = nx.circular_layout(grafo)

    plt.figure(figsize=(7, 6))
    nx.draw_networkx_nodes(
        grafo, posiciones_de_nodos,
        node_size=750, node_color="#DCEBFF", edgecolors="#2F5FA8",
    )
    nx.draw_networkx_labels(
        grafo, posiciones_de_nodos, font_size=11, font_weight="bold",
    )

    aristas_normales = []
    aristas_del_camino = []
    for arista in grafo.edges():
        if arista in aristas_resaltadas:
            aristas_del_camino.append(arista)
        else:
            aristas_normales.append(arista)

    nx.draw_networkx_edges(
        grafo, posiciones_de_nodos, edgelist=aristas_normales,
        arrows=True, arrowsize=18, edge_color="#555555", node_size=750,
    )
    if aristas_del_camino:
        nx.draw_networkx_edges(
            grafo, posiciones_de_nodos, edgelist=aristas_del_camino,
            arrows=True, arrowsize=20, edge_color="#D62828", width=2.5,
            node_size=750,
        )

    etiquetas_de_pesos = nx.get_edge_attributes(grafo, "weight")
    nx.draw_networkx_edge_labels(
        grafo, posiciones_de_nodos, edge_labels=etiquetas_de_pesos,
        font_size=9, label_pos=0.3,
    )
    plt.title(
        "Grafo dirigido (" + str(grafo.number_of_nodes()) + " nodos, "
        + str(grafo.number_of_edges()) + " aristas)"
    )
    plt.axis("off")
    plt.show()


# ----------------------------------------------------------------------
# ENTRADA DE DATOS POR CONSOLA
# ----------------------------------------------------------------------
def pedir_cantidad_de_nodos():
    while True:
        texto_ingresado = input(
            "Ingrese la cantidad de nodos n (entre "
            + str(CANTIDAD_MINIMA_NODOS) + " y "
            + str(CANTIDAD_MAXIMA_NODOS) + "): "
        )
        if texto_ingresado.isdigit():
            cantidad_nodos = int(texto_ingresado)
            if CANTIDAD_MINIMA_NODOS <= cantidad_nodos <= CANTIDAD_MAXIMA_NODOS:
                return cantidad_nodos
        print("Dato invalido. Intente de nuevo.")


def pedir_modo_de_generacion():
    while True:
        respuesta = input("¿Generar el grafo (M)anual o (A)leatorio? ")
        respuesta = respuesta.strip().lower()
        if respuesta in ("m", "manual"):
            return "manual"
        if respuesta in ("a", "aleatorio"):
            return "aleatorio"
        print("Opcion invalida. Escriba M o A.")


def obtener_clave_de_orden_de_arista(tupla_arista):
    """Clave de ordenamiento (origen, destino) para una arista con datos."""
    nodo_origen, nodo_destino, _ = tupla_arista
    return (nodo_origen, nodo_destino)


def imprimir_lista_de_aristas_ordenada(grafo):
    """Imprime todas las aristas del grafo, ordenadas por origen y destino."""
    lista_de_aristas = list(grafo.edges(data=True))
    lista_de_aristas.sort(key=obtener_clave_de_orden_de_arista)

    print("\nLista de aristas del grafo (ordenada):")
    if not lista_de_aristas:
        print("  (el grafo todavia no tiene aristas)")
        return
    for nodo_origen, nodo_destino, datos_de_la_arista in lista_de_aristas:
        print(
            "  " + str(nodo_origen) + " -> " + str(nodo_destino)
            + "   (peso " + str(datos_de_la_arista["weight"]) + ")"
        )


def pedir_aristas_manualmente(grafo, cantidad_nodos):
    print(
        "Ingrese las aristas del grafo. Los nodos van del 1 al "
        + str(cantidad_nodos) + "."
    )
    print("Escriba 0 en el nodo origen para terminar de ingresar aristas.\n")

    while True:
        texto_origen = input("Nodo origen (0 para terminar): ").strip()

        if texto_origen == "0":
            break

        if not texto_origen.isdigit():
            print("El origen debe ser un numero. Intente de nuevo.\n")
            continue
        nodo_origen = int(texto_origen)
        if nodo_origen < 1 or nodo_origen > cantidad_nodos:
            print("Ese nodo no existe. Intente de nuevo.\n")
            continue

        texto_destino = input("Nodo destino: ").strip()
        if not texto_destino.isdigit():
            print("El destino debe ser un numero. Intente de nuevo.\n")
            continue
        nodo_destino = int(texto_destino)
        if nodo_destino < 1 or nodo_destino > cantidad_nodos:
            print("Ese nodo no existe. Intente de nuevo.\n")
            continue

        texto_peso = input("Peso de la arista: ").strip()
        if not texto_peso.isdigit():
            print("El peso debe ser un numero entero positivo. Intente de nuevo.\n")
            continue
        peso = int(texto_peso)

        _, mensaje = agregar_arista_manual(
            grafo, nodo_origen, nodo_destino, peso
        )
        print(mensaje)
        imprimir_lista_de_aristas_ordenada(grafo)
        print()


def pedir_origen_y_destino(cantidad_nodos):
    while True:
        texto_origen = input(
            "Nodo ORIGEN (1 a " + str(cantidad_nodos) + "): "
        ).strip()
        texto_destino = input(
            "Nodo DESTINO (1 a " + str(cantidad_nodos) + "): "
        ).strip()

        if not (texto_origen.isdigit() and texto_destino.isdigit()):
            print("Ambos valores deben ser numeros. Intente de nuevo.\n")
            continue

        nodo_origen = int(texto_origen)
        nodo_destino = int(texto_destino)

        if not (1 <= nodo_origen <= cantidad_nodos):
            print("El origen no existe en el grafo. Intente de nuevo.\n")
            continue
        if not (1 <= nodo_destino <= cantidad_nodos):
            print("El destino no existe en el grafo. Intente de nuevo.\n")
            continue
        if nodo_origen == nodo_destino:
            print("El origen y el destino deben ser distintos. Intente de nuevo.\n")
            continue

        return nodo_origen, nodo_destino


# ----------------------------------------------------------------------
# PROGRAMA PRINCIPAL
# ----------------------------------------------------------------------
def ejecutar_un_analisis_completo():
    """Ejecuta un ciclo completo: crear grafo, elegir origen/destino y
    correr Dijkstra. Muestra el resultado, exista o no un camino."""
    imprimir_banner("GRUPO 2 - PROBLEMA DEL CAMINO MINIMO (DIJKSTRA)")

    cantidad_nodos = pedir_cantidad_de_nodos()
    modo_de_generacion = pedir_modo_de_generacion()

    if modo_de_generacion == "aleatorio":
        grafo = generar_grafo_aleatorio(cantidad_nodos)
        print("\nGrafo aleatorio generado con " + str(cantidad_nodos) + " nodos.")
        imprimir_lista_de_aristas_ordenada(grafo)
    else:
        grafo = crear_grafo_vacio(cantidad_nodos)
        pedir_aristas_manualmente(grafo, cantidad_nodos)

    print(
        "\nEl grafo tiene " + str(grafo.number_of_nodes()) + " nodos y "
        + str(grafo.number_of_edges()) + " aristas."
    )

    imprimir_banner("VISUALIZACION DEL GRAFO")
    if pedir_confirmacion("¿Desea ver el grafo generado? (s/n): "):
        print("Mostrando el grafo en una ventana aparte...")
        dibujar_grafo(grafo)

    imprimir_banner("SELECCION DE ORIGEN Y DESTINO")
    nodo_origen, nodo_destino = pedir_origen_y_destino(cantidad_nodos)

    imprimir_banner("EJECUCION PASO A PASO DEL ALGORITMO DE DIJKSTRA")
    ejecutar_paso_a_paso = pedir_confirmacion(
        "¿Desea ejecutar el algoritmo mostrando cada iteracion paso a paso? (s/n): "
    )
    distancias, predecesores, historial = ejecutar_dijkstra_paso_a_paso(
        grafo, nodo_origen, nodo_destino, ejecutar_paso_a_paso
    )

    imprimir_banner("TABLA DE RESULTADOS (etiquetas [distancia, predecesor])")
    imprimir_tabla_de_resultados(historial, nodo_origen)

    imprimir_banner("RESULTADO FINAL")
    if distancias[nodo_destino] == INFINITO:
        print(
            "No existe ningun camino entre el nodo " + str(nodo_origen)
            + " y el nodo " + str(nodo_destino) + "."
        )
        return

    print(
        "Distancia minima entre " + str(nodo_origen) + " y "
        + str(nodo_destino) + ": " + str(distancias[nodo_destino])
    )

    todos_los_caminos = reconstruir_todos_los_caminos_minimos(
        predecesores, nodo_origen, nodo_destino
    )
    print("Cantidad de caminos minimos encontrados: " + str(len(todos_los_caminos)))

    aristas_a_resaltar = set()
    for numero_de_camino, camino in enumerate(todos_los_caminos, start=1):
        texto_camino = " -> ".join(str(nodo) for nodo in camino)
        print("  Camino " + str(numero_de_camino) + ": " + texto_camino)
        for posicion in range(len(camino) - 1):
            aristas_a_resaltar.add((camino[posicion], camino[posicion + 1]))

    if pedir_confirmacion("\n¿Desea ver el camino minimo resaltado sobre el grafo? (s/n): "):
        dibujar_grafo(grafo, aristas_a_resaltar)


def main():
    while True:
        ejecutar_un_analisis_completo()

        if not pedir_confirmacion("\n¿Desea hacer un nuevo analisis? (s/n): "):
            print("\nPrograma finalizado.")
            break


if __name__ == "__main__":
    main()