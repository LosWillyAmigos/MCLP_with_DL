from .utils.base import *
from .utils import create_instances,etl
from keras._tf_keras.keras.preprocessing.sequence import pad_sequences
import random
import numpy as np


def get_location_block(block, space):
    """
    Calcula la posición inicial de un bloque dentro de un espacio tridimensional.
    
    Args:
        block: Objeto que representa el bloque, debe tener atributos `l` (largo), `w` (ancho) y `h` (alto).
        space: Objeto que representa el espacio, debe tener atributos `corner_point` (tupla con las coordenadas iniciales),
               `xmax`, `ymax`, y `zmax` (dimensiones máximas).
               
    Returns:
        tuple: Coordenadas ajustadas (x, y, z) del bloque dentro del espacio.
    """
    # Coordenadas iniciales
    x, y, z = space.corner_point

    # Ajustar las coordenadas según el tamaño del bloque y los límites del espacio
    if x == space.xmax:
        x -= block.l
    if y == space.ymax:
        y -= block.w
    if z == space.zmax:
        z -= block.h

    return x, y, z

def genSpace(L, W, H):
    """
    Genera un espacio disponible dentro de un contenedor tridimensional y el bloque asociado.

    Args:
        L (float): Largo del bloque.
        W (float): Ancho del bloque.
        H (float): Altura del bloque.

    Returns:
        tuple: Una tupla que contiene:
            - space: El espacio libre más cercano donde se puede colocar el bloque.
            - cont: El bloque creado con las dimensiones especificadas.
    
    Raises:
        ValueError: Si las dimensiones (L, W, H) son inválidas (menores o iguales a 0).
        AttributeError: Si el método `closest_space` o el atributo `free_space` no están presentes en `Block`.
    """
    # Validar dimensiones del bloque
    if L <= 0 or W <= 0 or H <= 0:
        raise ValueError("Las dimensiones del bloque (L, W, H) deben ser mayores que cero.")

    # Configurar atributos estáticos de la clase Space
    if not hasattr(Space, "filling") or not hasattr(Space, "vertical_stability"):
        Space.filling = "free"
        Space.vertical_stability = False

    # Crear un bloque con las dimensiones especificadas
    cont = Block(l=L, w=W, h=H)

    # Intentar obtener el espacio libre más cercano
    try:
        space = cont.free_space.closest_space()
    except AttributeError as e:
        raise AttributeError(
            "El objeto 'Block' debe tener un atributo 'free_space' y un método 'closest_space'."
        ) from e

    return space, cont

def remove_unconstructable(blocks, items):
    """
    Filtra y elimina bloques que no son construibles con la lista de ítems disponibles.

    Args:
        blocks (list): Lista de bloques a verificar.
        items (dict): Diccionario de ítems disponibles para construir los bloques.

    Returns:
        list: Una lista de bloques que son construibles con los ítems disponibles.
    """
    # Validar entradas
    if not isinstance(blocks, list) or not isinstance(items, dict):
        raise TypeError("El argumento 'blocks' debe ser una lista y 'items' debe ser un diccionario.")

    # Filtrar bloques no construibles
    blocks = [block for block in blocks if block.is_constructible(items)]

    return blocks


def obtenerAcciones(acciones):
    """
    Procesa una lista de acciones y extrae la información de cada acción.

    Args:
        acciones (list): Lista de cadenas de texto que representan acciones.
                         Ejemplo: "action: block:70734 space:(0,0,0)"

    Returns:
        list: Una lista de listas, donde cada sublista contiene:
              - El ID del bloque (int).
              - Las coordenadas X, Y, Z (int).

    Raises:
        ValueError: Si alguna cadena en la lista no tiene el formato esperado.
    """
    Y = []
    for accion in acciones:
        try:
            # Extraer la posición (x, y, z)
            x, y, z = map(int, accion.split()[2].split(":")[1].strip("()").split(","))
            # Extraer el ID del bloque
            block_id = int(accion.split()[1].split(":")[1])
            # Añadir la acción procesada a la lista
            Y.append([block_id, x, y, z])
        except (IndexError, ValueError) as e:
            raise ValueError(f"La acción '{accion}' no tiene el formato esperado.") from e

    return Y

def funcionActualizadora(space, block, cont, items, blocks, bloquesDict, accion):
    """
    Actualiza el estado del espacio, bloques y contenedor basado en la acción proporcionada.

    Args:
        space: Espacio actual donde se colocará el bloque.
        block: Bloque que se está procesando.
        cont: Contenedor que maneja los bloques y espacios.
        items (dict): Diccionario de ítems disponibles.
        blocks (list): Lista de bloques pendientes por colocar.
        bloquesDict: Diccionario de bloques (no se usa directamente en esta función, pero puede ser útil).
        accion (list): Acción a realizar en el formato [block_id, x, y, z].

    Returns:
        tuple: Contiene los siguientes valores actualizados:
            - space: Espacio libre más cercano para el siguiente bloque.
            - block: Bloque procesado.
            - cont: Contenedor actualizado con el bloque añadido.
            - items (dict): Ítems restantes después de colocar el bloque.
            - blocks (list): Lista de bloques actualizada después de eliminar los no válidos.
            - block_loc (tuple): Ubicación del bloque en el espacio.

    Raises:
        ValueError: Si la acción no tiene el formato esperado.
    """
    try:
        # Obtener la ubicación del bloque en el espacio
        block_loc = get_location_block(block, space)

        # Añadir el bloque al contenedor en las coordenadas indicadas
        cont.add_block(block, accion[1], accion[2], accion[3])

        # Actualizar los ítems disponibles
        items -= block.items

        # Eliminar bloques que ya no son válidos
        blocks = remove_unconstructable(blocks, items)

        # Filtrar el espacio libre según los ítems restantes
        cont.free_space.filter(items)

        # Encontrar el siguiente espacio libre más cercano
        space = cont.free_space.closest_space()
    except Exception as e:
        raise ValueError("Error al actualizar el estado: verifica los argumentos y el flujo de ejecución.") from e

    return space, block, cont, items, blocks, block_loc


def getSample(x_accion, y_accion, posicion, cantidad_bloques_colocados, tamanioMuestra=100):
    """
    Genera una muestra basada en una lista de acciones, excluyendo un elemento fijo y seleccionando
    elementos aleatorios para completar el tamaño de la muestra.

    Args:
        x_accion (list): Lista de acciones disponibles.
        y_accion (list): Lista de etiquetas correspondientes.
        posicion (int): Índice de la posición base.
        cantidad_bloques_colocados (int): Número de bloques colocados.
        tamanioMuestra (int, opcional): Tamaño de la muestra a generar. Por defecto es 100.

    Returns:
        tuple: Una tupla (x_sample, y_sample) donde:
               - x_sample: Arreglo NumPy con las acciones seleccionadas.
               - y_sample: Arreglo NumPy con las etiquetas correspondientes.
    """
    try:
        # Calcular la posición del elemento fijo
        posicion_elemento = posicion + 1 + cantidad_bloques_colocados
        block = x_accion[posicion_elemento]

        # Crear una lista auxiliar excluyendo el elemento fijo
        x_aux = x_accion[:posicion_elemento] + x_accion[posicion_elemento + 1:]

        # Excluir el espacio inicial y los bloques colocados
        x_aux = x_aux[1 + cantidad_bloques_colocados:]

        # Asegurarse de que haya suficientes elementos para la muestra
        num_samples = min(tamanioMuestra - 1, len(x_aux))
        muestra = random.sample(x_aux, num_samples)

        # Construir la muestra final
        x_sample = x_accion[:1 + cantidad_bloques_colocados] + muestra
        x_sample.append(block)

        # Crear las etiquetas correspondientes
        y_sample = np.zeros(len(x_sample))
        y_sample[-1] = 1

        return np.array(x_sample), y_sample
    except IndexError as e:
        raise IndexError(
            "Error de índice: Verifica que la posición base y los bloques colocados no excedan el tamaño de 'x_accion'."
        ) from e
    except ValueError as e:
        raise ValueError(
            "Error al tomar la muestra: Asegúrate de que 'x_aux' tenga suficientes elementos para completar la muestra."
        ) from e


def generarX_y(id):
    #abrimos el archivo que contiene el resultado del problema
    #tests\resultados_solver\output1.txt
    archivo = r"tests\resultados_solver\output"+str(id+1)+".txt"

    #obtenemos los datos importantes del archivo
    bloques,cajas,acciones = etl.obtener_registros_de_tipo_block(archivo)  ##(acciones)

    #cargamos la instancia original
    items, L, W, H, lwh2item = etl.load_instance(filename = "instances.txt", type="BF", id_instance=id)

    acciones = obtenerAcciones(acciones)

    #obtenemos la cantidad de cajas
    cant_cajas = sum(items.values())

    #definimos las variables a utilizar
    valid_blocks, bloquesDict = etl.transformar_a_bloques(bloques,cajas,lwh2item)
    space,cont = genSpace(L,W,H)
    bloques_colocados = []
    X = []
    Y = []

    for accion in acciones:
        #print(space)
        if(space == None): break
        x_accion = etl.funNormalizar(space, valid_blocks, bloques_colocados, cont, cant_cajas)
        y_accion, posicion = etl.genVectorBinario(accion, bloquesDict, valid_blocks, len(x_accion), len(bloques_colocados))

        x_sample,y_sample = getSample(x_accion, y_accion, posicion, len(bloques_colocados), 20)
        space, bloque_actual, cont, items, valid_blocks, block_loc = funcionActualizadora (space, valid_blocks[posicion], cont, items, valid_blocks, bloquesDict,accion)


        id = accion[0]
        bloques_colocados.append([id, bloque_actual, block_loc])

        X.append(x_sample)
        Y.append(y_sample)



    #mostrar la solucion
    #box_dims = []
    #for aabb in cont.aabbs:
        #box_dims.append([aabb.xmin,aabb.ymin,aabb.zmin,aabb.xmax,aabb.ymax,aabb.zmax])

    #box_plotter.plot_container([L,W,H], box_dims)
    return X,Y


def generate_data(runs = 100):
    X = []
    Y = []

    #generar los datos
    for i in range(runs):
        print(i)
        x,y = generarX_y(i)

        X += x
        Y += y


    X_padded = pad_sequences(X, padding='post',dtype=np.float64)
    Y_padded = pad_sequences(Y, padding='post',dtype=np.float64)


    np.set_printoptions(threshold=np.inf)


    return np.array(X_padded),np.array(Y_padded)


create_instances.get_uni("instances", n_types=10, instances=100, initial_seed=2502505)
create_instances.generarSolucionesSolver(100)

X,Y = generate_data(100)
print(X.shape,Y.shape)
