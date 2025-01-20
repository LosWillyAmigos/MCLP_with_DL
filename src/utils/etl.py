import os, platform
from .create_instances import get_uni
from .base import *
import numpy as np
import math

def transformar_a_bloques(bloques, cajas_por_bloques, lwh2item):
    """
    Transforma información de bloques y cajas en objetos `Block` y un diccionario asociado.

    Args:
        bloques (list): Lista de bloques en formato de cadena.
        cajas_por_bloques (list): Lista de cajas asociadas a cada bloque.
        lwh2item (dict): Diccionario que mapea dimensiones (l, w, h) a ítems.

    Returns:
        tuple:
            - listaGeneral (list): Lista de objetos `Block` representando bloques válidos.
            - bloquesDict (dict): Diccionario que asocia IDs de bloques a sus objetos `Block`.
    """
    listaGeneral = []
    bloquesDict = {}

    for i, bloque_str in enumerate(bloques):
        bloque = bloque_str.split()
        lwhBloque = [int(valor) for valor in bloque[2].strip('()').split(',')]

        # Crear el diccionario de ítems para el bloque actual
        bl_items = Itemdict()
        for caja_str in cajas_por_bloques[i]:
            caja = caja_str.split()
            lwhCaja = [int(valor) for valor in caja[2].strip('()').split(',')]
            n = int(caja[4])  # Cantidad de ítems
            item_key = lwh2item.get(tuple(lwhCaja), None)
            if item_key is not None:
                bl_items[item_key] = n
            else:
                raise KeyError(f"Dimensiones de caja {lwhCaja} no encontradas en `lwh2item`.")

        # Crear el objeto `Block`
        newBlock = Block(l=lwhBloque[0], w=lwhBloque[1], h=lwhBloque[2], items=bl_items)

        # Añadir a la lista general y al diccionario
        listaGeneral.append(newBlock)
        blockId = int(bloque[1])  # ID del bloque
        bloquesDict[blockId] = newBlock

    return listaGeneral, bloquesDict



def obtener_registros_de_tipo_block(archivo):
    """
    Extrae información de bloques, cajas y acciones desde un archivo de texto.

    Args:
        archivo (str): Ruta del archivo de texto que contiene los datos.

    Returns:
        tuple:
            - bloques (list): Lista de bloques en formato de cadena.
            - cajas (list): Lista de listas, donde cada sublista contiene las cajas asociadas a un bloque.
            - acciones (list): Lista de acciones en formato de cadena.
    """
    try:
        bloques = []  # Lista de bloques
        cajas = []    # Lista de listas de cajas asociadas a cada bloque

        # Abrir el archivo y leer línea por línea
        with open(archivo, 'r') as f:
            for line in f:
                line = line.strip()
                if 'n_blocks:' in line:
                    # Obtener el número total de bloques
                    n_blocks = int(line.split(':')[1])
                elif '-- box:' in line:
                    # Asociar la caja al último bloque
                    if cajas:
                        cajas[-1].append(line)
                elif 'block:' in line:
                    # Registrar el bloque y preparar su lista de cajas asociadas
                    bloques.append(line)
                    cajas.append([])

        # Separar bloques y acciones
        bloques_validos = bloques[:n_blocks]
        acciones = bloques[n_blocks:]

        return bloques_validos, cajas, acciones

    except FileNotFoundError:
        return f"Error: El archivo '{archivo}' no se encontró."
    except ValueError as e:
        return f"Error de formato en el archivo: {e}"
    except Exception as e:
        return f"Error inesperado: {e}"




def load_instance(filename="instancia.txt", type="BF", id_instance=0):
    """
    Carga los datos de una instancia desde un archivo y devuelve los ítems, dimensiones y mapeo de ítems.

    Args:
        filename (str): Nombre del archivo que contiene los datos de la instancia.
        type (str): Tipo de instancia (no se utiliza actualmente, pero puede extenderse en el futuro).
        id_instance (int): Índice de la instancia que se desea cargar.

    Returns:
        tuple: Una tupla que contiene:
            - items (dict): Diccionario de ítems y su cantidad.
            - L (int): Dimensión L del contenedor.
            - W (int): Dimensión W del contenedor.
            - H (int): Dimensión H del contenedor.
            - lwh2item (dict): Mapeo de dimensiones (l, w, h) a un ítem.
    """
    route = f"tests/instances/{filename}"

    try:
        with open(route, "r") as file:
            # Saltar la primera línea del archivo
            file.readline()

            for j in range(100):  # Limitar a 100 instancias (puede ajustarse)
                file.readline()  # Línea de separación
                L, W, H = [int(x) for x in file.readline().split()]  # Dimensiones del contenedor

                # Leer número de ítems
                n = int(file.readline())
                items = Itemdict()
                lwh2item = {}

                # Leer los ítems y sus cantidades
                for i in range(n):
                    id, l, rotx, w, roty, h, rotz, n = [int(x) for x in file.readline().split()]
                    item = Boxtype(id, l, w, h, rotx, roty, rot_h=True, weight=1)
                    items[item] = n
                    lwh2item[(l, w, h)] = item

                # Retornar los datos cuando se encuentre la instancia deseada
                if j == id_instance:
                    return items, L, W, H, lwh2item

    except FileNotFoundError:
        raise FileNotFoundError(f"El archivo '{filename}' no se encontró en la ruta '{route}'.")
    except Exception as e:
        raise RuntimeError(f"Error al cargar la instancia: {e}")



def genVectorBinario(accion, bloquesDict, valid_blocks, cantidadElementos, cantidadElementosColocados):
    """
    Genera un vector binario donde se marca la posición del bloque que se está colocando, 
    según la acción proporcionada.

    Args:
        accion (list): Acción que contiene el id del bloque y las coordenadas.
        bloquesDict (dict): Diccionario que mapea un id de bloque a su objeto `Block`.
        valid_blocks (list): Lista de bloques válidos.
        cantidadElementos (int): Cantidad total de bloques válidos.
        cantidadElementosColocados (int): Cantidad de bloques que ya han sido colocados.

    Returns:
        tuple: Un vector binario `Y` y la posición original del bloque en `valid_blocks`.
    """
    # Inicializamos el vector binario con ceros
    Y = np.zeros(cantidadElementos)

    # Obtenemos el id del bloque de la acción
    blockId = accion[0]

    # Recuperamos el bloque correspondiente desde el diccionario de bloques
    block = bloquesDict.get(blockId)
    if block is None:
        raise ValueError(f"El bloque con id {blockId} no se encuentra en el diccionario de bloques.")

    # Posición en la lista de bloques válidos (sin actualizar)
    try:
        posicionSinActualizar = valid_blocks.index(block)
    except ValueError:
        raise ValueError(f"El bloque {block} no se encuentra en la lista de bloques válidos.")

    # Calculamos la posición en el vector de acuerdo con la cantidad de elementos colocados
    posicion = posicionSinActualizar + 1 + cantidadElementosColocados

    # Marcamos la posición correspondiente en el vector binario
    Y[posicion] = 1

    return Y, posicionSinActualizar


def normalizar_bloque(block, block_loc, lwhSpace, cant_cajas, colocado=True):
    """
    Normaliza las dimensiones, ubicación y elementos de un bloque.
    
    Args:
        block: Bloque a normalizar.
        lwhSpace: Dimensiones del espacio (contenedor).
        cant_cajas: Cantidad total de cajas.
        colocado: Si el bloque está colocado o no.
    
    Returns:
        list: Lista normalizada para el bloque.
    """
    # Normalizar dimensiones
    norm_dims = [block.l / lwhSpace[0], block.w / lwhSpace[1], block.h / lwhSpace[2]]
    
    # Normalizar ubicación
    norm_loc = [block_loc[0] / lwhSpace[0], block_loc[1] / lwhSpace[1], block_loc[2] / lwhSpace[2]] if colocado else [0, 0, 0]
    
    # Normalizar el número de elementos en el bloque
    norm_elements = math.log(sum(block.items.values()), cant_cajas) if sum(block.items.values()) > 0 else 0
    
    # Crear el vector normalizado para el bloque
    norm_block = norm_dims + norm_loc + ([1, 0] if colocado else [0, 0]) + [norm_elements]
    
    return norm_block

def funNormalizar(space, valid_blocks, bloques_colocados, cont, cant_cajas):
    """
    Normaliza el espacio y los bloques colocados y no colocados en el contenedor.
    
    Args:
        space: El espacio o contenedor.
        valid_blocks: Lista de bloques válidos.
        bloques_colocados: Lista de bloques ya colocados.
        cont: El contenedor.
        cant_cajas: Cantidad de cajas disponibles para la normalización.
    
    Returns:
        list: Lista de vectores normalizados para el espacio y los bloques.
    """
    # Dimensiones del contenedor
    lwhSpace = [space.xmax, space.ymax, space.zmax]

    # Iniciar la lista X con la normalización del espacio
    norm_space = [1, 1, 1, 0, 0, 0, 0, 1, 0]  # Normalización del espacio (dimensiones y estado)
    X = [norm_space]

    # Normalizar bloques ya colocados
    for element in bloques_colocados:
        block = element[1]
        block_loc = element[2]
        norm_block = normalizar_bloque(block, block_loc,lwhSpace, cant_cajas, colocado=True)
        X.append(norm_block)

    # Normalizar bloques no colocados
    for block in valid_blocks:
        norm_block = normalizar_bloque(block,[0,0,0],lwhSpace, cant_cajas, colocado=False)
        X.append(norm_block)

    return X