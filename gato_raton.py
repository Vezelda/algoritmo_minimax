import pygame
import numpy as np
import random

# Dimensiones del tablero
TABLERO_TAMANIO = 5    
TAMANIO_CELDA = 100
ANCHO_VENTANA = TABLERO_TAMANIO * TAMANIO_CELDA
ALTO_VENTANA = TABLERO_TAMANIO * TAMANIO_CELDA

# Colores
COLOR_FONDO = (255, 255, 255)
COLOR_LINEA = (0, 0, 0)

# Inicializamos el tablero
tablero = np.zeros((TABLERO_TAMANIO, TABLERO_TAMANIO))

# Posiciones iniciales
gato_pos = (0, 0)
raton_pos = (4, 4)

# Definir las posiciones iniciales en el tablero
tablero[gato_pos] = 1  # 1 representa al Gato
tablero[raton_pos] = 2  # 2 representa al Ratón

# Para evitar movimientos repetidos
movimientos_previos = set()

# Generar destino para el ratón
def generar_destino(raton_pos, min_distancia):
    while True:
        destino = (random.randint(0, TABLERO_TAMANIO - 1), random.randint(0, TABLERO_TAMANIO - 1))
        distancia = np.sum(np.abs(np.array(destino) - np.array(raton_pos)))
        if distancia >= min_distancia:
            return destino


destino = generar_destino(raton_pos, 4)

def mover_jugador(tablero, posicion_actual, nueva_posicion):
    if (0 <= nueva_posicion[0] < TABLERO_TAMANIO) and (0 <= nueva_posicion[1] < TABLERO_TAMANIO):
        jugador = tablero[posicion_actual]
        tablero[posicion_actual] = 0
        tablero[nueva_posicion] = jugador
        return nueva_posicion
    else:
        return posicion_actual

def evaluar(tablero):
    gato_pos = np.argwhere(tablero == 1)
    raton_pos = np.argwhere(tablero == 2)
    
    if gato_pos.size == 0 or raton_pos.size == 0:
        return 0

    gato_pos = gato_pos[0]
    raton_pos = raton_pos[0]

    # Escalar las coordenadas del ratón y del destino
    escala = TABLERO_TAMANIO / 5  # Escala para ajustar las coordenadas
    distancia_gato_raton = np.sum(np.abs(gato_pos - raton_pos) * escala)
    distancia_raton_destino = np.sum(np.abs(raton_pos - destino) * escala)
    
    # Queremos que el gato minimice la distancia al ratón y el ratón minimice la distancia al destino
    return -distancia_gato_raton - distancia_raton_destino



def generar_movimientos(tablero, jugador, movimientos_previos):
    movimientos = []
    posicion_actual = np.argwhere(tablero == jugador)
    
    if posicion_actual.size == 0:
        return movimientos
    
    posicion_actual = posicion_actual[0]
    posibles_movimientos = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    # Agregar movimientos diagonales para el gato
    if jugador == 1:
        posibles_movimientos.extend([(1, 1), (1, -1), (-1, 1), (-1, -1)])

    for movimiento in posibles_movimientos:
        nueva_posicion = (posicion_actual[0] + movimiento[0], posicion_actual[1] + movimiento[1])
        if (0 <= nueva_posicion[0] < TABLERO_TAMANIO) and (0 <= nueva_posicion[1] < TABLERO_TAMANIO):
            nuevo_tablero = tablero.copy()
            nuevo_tablero[posicion_actual[0], posicion_actual[1]] = 0
            nuevo_tablero[nueva_posicion[0], nueva_posicion[1]] = jugador
            # Verificar si se repitio el movmiento
            if tuple(map(tuple, nuevo_tablero)) not in movimientos_previos:
                movimientos.append(nuevo_tablero)
    
    # Limitar los movimientos diagonales a un máximo de dos
    if jugador == 1:
        diagonales = [(movimiento[0], movimiento[1]) for movimiento in posibles_movimientos[4:]]
        movimientos = movimientos[:len(posibles_movimientos[:4])] + movimientos[len(posibles_movimientos[:4]):][:2]
    
    return movimientos

def minimax(tablero, profundidad, maximizando, movimientos_previos):
    if profundidad == 0 or juego_terminado(tablero):
        return evaluar(tablero)
    
    if maximizando: #que estructura de datos me genera el algoritmo minimax, por eso puedo recorrer en profundidad
        mejor_valor = -np.inf
        movimientos = generar_movimientos(tablero, 1, movimientos_previos)
        for movimiento in movimientos:
            valor = minimax(movimiento, profundidad - 1, False, movimientos_previos)
            mejor_valor = max(mejor_valor, valor)
        return mejor_valor
    else:
        mejor_valor = np.inf
        movimientos = generar_movimientos(tablero, 2, movimientos_previos)
        for movimiento in movimientos:
            valor = minimax(movimiento, profundidad - 1, True, movimientos_previos)
            mejor_valor = min(mejor_valor, valor)
        return mejor_valor

def generar_movimientos_raton(tablero, raton_pos, movimientos_previos):
    movimientos = []
    posibles_movimientos = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    for movimiento in posibles_movimientos:
        nueva_posicion = (raton_pos[0] + movimiento[0], raton_pos[1] + movimiento[1])
        if (0 <= nueva_posicion[0] < TABLERO_TAMANIO) and (0 <= nueva_posicion[1] < TABLERO_TAMANIO):
            nuevo_tablero = tablero.copy()
            nuevo_tablero[raton_pos[0], raton_pos[1]] = 0
            nuevo_tablero[nueva_posicion[0], nueva_posicion[1]] = 2
            if tuple(map(tuple, nuevo_tablero)) not in movimientos_previos:
                movimientos.append((nuevo_tablero, nueva_posicion))
    # Ordenar movimientos por la distancia al destino
    movimientos.sort(key=lambda x: np.sum(np.abs(np.array(x[1]) - np.array(destino))))
    return movimientos

def juego_terminado(tablero):
    gato_pos = np.argwhere(tablero == 1)
    raton_pos = np.argwhere(tablero == 2)
    if gato_pos.size == 0 or raton_pos.size == 0:
        return True
    gato_pos = gato_pos[0]
    raton_pos = raton_pos[0]
    if np.array_equal(gato_pos, raton_pos):
        return True
    if np.array_equal(raton_pos, destino):
        return True
    return False

def dibujar_destino(pantalla, imagen_destino, destino):
    destino_rect = pygame.Rect(destino[1] * TAMANIO_CELDA, destino[0] * TAMANIO_CELDA, TAMANIO_CELDA, TAMANIO_CELDA)
    pantalla.blit(imagen_destino, destino_rect.topleft)

def jugar():
    global gato_pos, raton_pos
    turno_gato = True
    profundidad = 3

    # Inicializar pygame
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
    pygame.display.set_caption("Juego del Gato y el Ratón")
    reloj = pygame.time.Clock()

    # Cargar imágenes GIF y redimensionarlas
    imagen_gato = pygame.image.load('static/gato.gif')
    imagen_raton = pygame.image.load('static/raton.gif')
    imagen_destino = pygame.image.load('static/destino.png')
    imagen_gato = pygame.transform.scale(imagen_gato, (TAMANIO_CELDA, TAMANIO_CELDA))
    imagen_raton = pygame.transform.scale(imagen_raton, (TAMANIO_CELDA, TAMANIO_CELDA))
    imagen_destino = pygame.transform.scale(imagen_destino, (TAMANIO_CELDA, TAMANIO_CELDA))

    corriendo = True
    while corriendo and not juego_terminado(tablero):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False

        pantalla.fill(COLOR_FONDO)

        # Dibujar el tablero
        for x in range(TABLERO_TAMANIO):
            for y in range(TABLERO_TAMANIO):
                rect = pygame.Rect(y * TAMANIO_CELDA, x * TAMANIO_CELDA, TAMANIO_CELDA, TAMANIO_CELDA)
                pygame.draw.rect(pantalla, COLOR_LINEA, rect, 1)
                if tablero[x, y] == 1:
                    pantalla.blit(imagen_gato, rect.topleft)
                elif tablero[x, y] == 2:
                    pantalla.blit(imagen_raton, rect.topleft)
        
        # Dibujar el destino
        dibujar_destino(pantalla, imagen_destino, destino)

        pygame.display.flip()

        if turno_gato:
            mejor_valor = -np.inf
            mejor_movimiento = None
            movimientos = generar_movimientos(tablero, 1, movimientos_previos)
            for movimiento in movimientos:
                valor = minimax(movimiento, profundidad, False, movimientos_previos)
                if valor > mejor_valor:
                    mejor_valor = valor
                    mejor_movimiento = movimiento
            if mejor_movimiento is not None:
                movimientos_previos.add(tuple(map(tuple, mejor_movimiento)))
                tablero[:] = mejor_movimiento
                gato_pos = np.argwhere(tablero == 1)[0]
        else:
            mejor_valor = np.inf
            mejor_movimiento = None
            movimientos = generar_movimientos_raton(tablero, raton_pos, movimientos_previos)
            for movimiento, nueva_posicion in movimientos:
                valor = minimax(movimiento, profundidad, True, movimientos_previos)
                if valor < mejor_valor:
                    mejor_valor = valor
                    mejor_movimiento = movimiento
            if mejor_movimiento is not None:
                movimientos_previos.add(tuple(map(tuple, mejor_movimiento)))
                tablero[:] = mejor_movimiento
                raton_pos = np.argwhere(tablero == 2)[0]

        turno_gato = not turno_gato
        reloj.tick(2)  # Controla la velocidad del juego

    # Mostrar el resultado final
    pantalla.fill(COLOR_FONDO)
    if gato_pos.size == 0 or raton_pos.size == 0:
        mensaje = "Error en la posición de los jugadores."
    else:
        if np.array_equal(raton_pos, destino):
            mensaje = "El Ratón huyo!"
        else:
            mensaje = "El Gato ceno hoy!"
    
    fuente = pygame.font.Font(None, 74)
    texto = fuente.render(mensaje, True, (0, 128, 0))
    pantalla.blit(texto, (20, ALTO_VENTANA // 2 - 37))
    pygame.display.flip()

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                return

if __name__ == "__main__":
    jugar()
