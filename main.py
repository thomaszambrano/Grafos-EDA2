

import sys
import random
import numpy as np
from PyQt5 import QtWidgets, QtGui, QtCore
from grafos_ui import Ui_MainWindow
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsTextItem, QGraphicsItem


class Nodo(QGraphicsEllipseItem):
    def __init__(self, x, y, radius, id, app):
        super().__init__(-radius, -radius, 2 * radius, 2 * radius)  # Dibujar el nodo centrado
        self.setBrush(QtGui.QBrush(QtGui.QColor("lightblue")))
        self.setPen(QtGui.QPen(QtCore.Qt.black))
        self.id = id
        self.setFlag(QGraphicsEllipseItem.ItemIsMovable)
        self.setFlag(QGraphicsEllipseItem.ItemSendsGeometryChanges)
        self.text_item = QGraphicsTextItem(f"Nodo {self.id}", self)
        self.text_item.setPos(-10, -10)  # Ajusta la posición del texto para que no se superponga con el nodo
        self.app = app  # Referencia a la aplicación para actualizar las aristas
        self.aristas = []  # Para guardar las aristas conectadas a este nodo

    def agregar_arista(self, arista):
        self.aristas.append(arista)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            # Cuando se mueva el nodo, actualizar las aristas
            for arista in self.aristas:
                arista.actualizar_posiciones()
        return super().itemChange(change, value)


class Arista(QGraphicsLineItem):
    def __init__(self, nodo1, nodo2, peso, scene):
        super().__init__()
        self.nodo1 = nodo1
        self.nodo2 = nodo2
        self.peso = peso
        self.scene = scene

        # Agregar el peso de la arista como un texto
        self.text_item = QGraphicsTextItem(str(self.peso))
        self.scene.addItem(self.text_item)

        # Agregar la línea y actualizar posiciones
        self.actualizar_posiciones()

        # Establecer el evento de clic para engrosar la arista y los nodos conectados
        self.setFlag(QGraphicsLineItem.ItemIsSelectable)
        self.setPen(QtGui.QPen(QtCore.Qt.black))

    def actualizar_posiciones(self):
        x1, y1 = self.nodo1.scenePos().x(), self.nodo1.scenePos().y()
        x2, y2 = self.nodo2.scenePos().x(), self.nodo2.scenePos().y()

        # Actualizar la línea de la arista
        self.setLine(x1, y1, x2, y2)

        # Colocar el texto en el centro de la línea
        self.text_item.setPos((x1 + x2) / 2, (y1 + y2) / 2)

    def mousePressEvent(self, event):
        # Engrosar la línea y los nodos conectados al hacer clic en la arista
        self.setPen(QtGui.QPen(QtCore.Qt.red, 3))  # Cambia el color y grosor de la arista
        self.nodo1.setPen(QtGui.QPen(QtCore.Qt.red, 3))  # Engrosar el nodo1
        self.nodo2.setPen(QtGui.QPen(QtCore.Qt.red, 3))  # Engrosar el nodo2
        super().mousePressEvent(event)  # Llama al evento de clic original


class GrafoApp(QtWidgets.QMainWindow):

    def __init__(self):
        super(GrafoApp, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Configurar la escena del QGraphicsView
        self.scene = QGraphicsScene()
        self.ui.graphicsView.setScene(self.scene)

        # Conectar el botón para dibujar el grafo
        self.ui.btnPintarGrafo.clicked.connect(self.dibujar_grafo)

        # Conectar el botón para generar matriz de adyacencia aleatoria
        self.ui.btnGenerarMatriz.clicked.connect(
            lambda: self.generar_matriz_adyacencia(4, 4, aleatoria=True, conexo=False))

        # Conectar el evento de cambio en la tabla para actualizar trayectorias
        self.ui.tableWidget.itemChanged.connect(self.calcular_y_mostrar_trayectorias)

        # Llenar la matriz de forma aleatoria al inicio
        self.generar_matriz_adyacencia(4, 4, aleatoria=True, conexo=True)

        # Lista para almacenar los nodos y las aristas
        self.nodos = []
        self.aristas = []

    def dibujar_grafo(self):
        try:
            # Limpiar la escena y listas
            self.scene.clear()
            self.nodos.clear()
            self.aristas.clear()

            # Obtener la nueva matriz de la UI y dibujar el grafo
            matriz = self.obtener_matriz()

            # Dibujar nodos y aristas
            self.dibujar_nodos_y_aristas(matriz)
        except Exception as e:
            print(f"Error al dibujar el grafo: {e}")

    def obtener_matriz(self):
        try:
            filas = self.ui.tableWidget.rowCount()
            columnas = self.ui.tableWidget.columnCount()
            matriz = []
            for i in range(filas):
                fila = []
                for j in range(columnas):
                    item = self.ui.tableWidget.item(i, j)
                    valor = int(item.text()) if item and item.text().isdigit() else 0
                    fila.append(valor)
                matriz.append(fila)
            return matriz
        except Exception as e:
            print(f"Error al obtener la matriz: {e}")
            return []

    def dibujar_nodos_y_aristas(self, matriz):
        try:
            num_nodos = len(matriz)
            radius = 20

            # Definir los límites para la posición aleatoria de los nodos
            width = self.ui.graphicsView.width() - 100
            height = self.ui.graphicsView.height() - 100

            # Dibujar nodos
            for i in range(num_nodos):
                x = random.randint(50, width)  # Coordenada x aleatoria
                y = random.randint(50, height)  # Coordenada y aleatoria
                nodo = Nodo(x, y, radius, i + 1, self)
                nodo.setPos(x, y)  # Posicionar el nodo en la escena
                self.scene.addItem(nodo)
                self.nodos.append(nodo)

            # Dibujar aristas
            for i in range(num_nodos):
                for j in range(num_nodos):
                    peso = matriz[i][j]
                    if peso > 0:
                        nodo1 = self.nodos[i]
                        nodo2 = self.nodos[j]

                        # Crear y agregar arista
                        arista = Arista(nodo1, nodo2, peso, self.scene)
                        self.aristas.append(arista)
                        self.scene.addItem(arista)

                        # Agregar aristas a los nodos para que se actualicen al moverlos
                        nodo1.agregar_arista(arista)
                        nodo2.agregar_arista(arista)

        except Exception as e:
            print(f"Error al dibujar nodos y aristas: {e}")

    def generar_matriz_adyacencia(self, filas, columnas, aleatoria=True, conexo=True):
        """
        Genera una matriz de adyacencia y la muestra en la interfaz gráfica.
        :param filas: Número de filas (número de nodos).
        :param columnas: Número de columnas (debe coincidir con filas para ser válida).
        :param aleatoria: Si es True, genera valores aleatorios entre 0 y 1. Si no, inicia con ceros.
        :param conexo: Si es False, generará un grafo potencialmente no conexo.
        """
        try:
            if filas != columnas:
                print("La matriz de adyacencia debe ser cuadrada.")
                return

            matriz = []
            for i in range(filas):
                fila = []
                for j in range(columnas):
                    if i == j:
                        fila.append(0)  # Sin auto-loops
                    else:
                        if aleatoria:
                            valor = random.randint(1, 10) if conexo or random.random() > 0.3 else 0
                            fila.append(valor)
                        else:
                            fila.append(0)  # Inicia con ceros
                matriz.append(fila)

            # Mostrar en la interfaz
            self.ui.tableWidget.setRowCount(filas)
            self.ui.tableWidget.setColumnCount(columnas)
            for i in range(filas):
                for j in range(columnas):
                    self.ui.tableWidget.setItem(i, j, QtWidgets.QTableWidgetItem(str(matriz[i][j])))

            self.calcular_y_mostrar_trayectorias()
        except Exception as e:
            print(f"Error al generar la matriz de adyacencia: {e}")

    def obtener_k_trayectorias(self, matriz, k):
        """
        Calcula la matriz de k-trayectorias usando la matriz de adyacencia.
        """
        try:
            matriz_np = np.array(matriz)
            matriz_k = np.linalg.matrix_power(matriz_np, k)
            return matriz_k.tolist()
        except Exception as e:
            print(f"Error al calcular las {k}-trayectorias: {e}")
            return None

    def calcular_y_mostrar_trayectorias(self):
        """
        Calcula las trayectorias K=2 y K=3 y las muestra en sus respectivas tablas.
        """
        try:
            matriz = self.obtener_matriz()
            if not matriz:
                print("La matriz de adyacencia no es válida.")
                return

            # Calcular trayectorias
            matriz_k2 = self.obtener_k_trayectorias(matriz, 2)
            matriz_k3 = self.obtener_k_trayectorias(matriz, 3)

            # Mostrar en la tabla K=2
            if matriz_k2:
                self.ui.tableWidgetK2.setRowCount(len(matriz_k2))
                self.ui.tableWidgetK2.setColumnCount(len(matriz_k2[0]))
                for i in range(len(matriz_k2)):
                    for j in range(len(matriz_k2[0])):
                        self.ui.tableWidgetK2.setItem(i, j, QtWidgets.QTableWidgetItem(str(matriz_k2[i][j])))

            # Mostrar en la tabla K=3
            if matriz_k3:
                self.ui.tableWidgetK3.setRowCount(len(matriz_k3))
                self.ui.tableWidgetK3.setColumnCount(len(matriz_k3[0]))
                for i in range(len(matriz_k3)):
                    for j in range(len(matriz_k3[0])):
                        self.ui.tableWidgetK3.setItem(i, j, QtWidgets.QTableWidgetItem(str(matriz_k3[i][j])))

            print("Trayectorias K=2 y K=3 calculadas y mostradas.")
        except Exception as e:
            print(f"Error al mostrar trayectorias: {e}")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = GrafoApp()
    window.show()
    sys.exit(app.exec_())
