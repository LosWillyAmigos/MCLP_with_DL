import random
import numpy as np
import os
import platform

def get_uni(filename:str,n_types:int=10, instances:int=1,initial_seed:int=40):
    try:
        os.makedirs("tests/instances", exist_ok=True)
    except Exception as e:
        print(f"Error creating folder: {e}")

    """
    Generates instances of n_types of boxes for the container loading problem (CLP) and saves them in a .txt file.

    Parameters:
        filename (str): The name of the .txt file where the generated instances will be saved.
        n_types (int): The number of different box types for the container loading problem. Default is 10.
        instances (int): The number of instances to generate for the CLP. Default is 1.
        initial_seed (int): The seed value for random number generation, ensuring reproducibility. Default is 40.
    """


    #dimensiones de contenedor
    l=587
    w=233
    h=220

    n = n_types
    #numero de tipos de caja

    #dimesiones de las cajas (normalizada)
    alpha1 =30
    alpha2=25
    alpha3=20
    beta1=120
    beta2=100
    beta3=80

    #constante de estabilidad
    L=2

    #Semilla
    s=initial_seed

    #Volumen de contenedor
    tc = l*h*w

    #limites de cajas
    low_bound= [alpha1, alpha2, alpha3]
    upper_bound= [beta1, beta2, beta3]

    file = "tests/instances/" + filename + ".txt"

    #abre el archivo para guardarlo
    with open(file, 'w') as file:
        file.write(str(instances)+"\n")
        for instance in range(instances):
            #arreglo con dimensiones, cantidad y volumen de los tipos de cajas
            dimension_box = []
            cantidad_box_type= []
            volumen_box_type=[]

            orientacion_box=[]

            #Inicializa el volumen de carga de cajas
            volumen_cargo = 0

            #guarda parametros base
            file.write(str(instance + 1)+" "+str(s)+"\n")
            file.write(str(l)+" "+str(w)+" "+str(h)+"\n")
            file.write(str(n)+"\n")

            i=0

            random.seed(s)

            for i in range(n):
                #inicializa las dimensiones de las cajas aleatoreamente dentro de los rangos
                r_j= [random.randint(alpha1,beta1),random.randint(alpha2,beta2),random.randint(alpha3,beta3)]

                aux_dim=[]

                #Define las dimensiones de las cajas asegurando que este en los rangos limites
                for j in range(3):
                    aux_dim.append(low_bound[j]+(r_j[j]%(upper_bound[j]-low_bound[j]+1)))

                #Guarda el arreglo dentro de otro arreglo
                dimension_box.append(aux_dim)

                #print(dimension_box)
                #inicializa el tipo de caja
                cantidad_box_type.append(1)
                #guarda el volumen de la caja creada
                volumen_box_type.append(dimension_box[i][0]*dimension_box[i][1]*dimension_box[i][2])
                min_dim=99999
                #busca la dimension mas baja de la caja
                for j in range(3):
                    if dimension_box[i][j] < min_dim:
                            min_dim=dimension_box[i][j]

                aux_orient=[]
                #verifica si la orientacion es viable
                for j in range(3):
                    if dimension_box[i][j]/min_dim < L:
                        aux_orient.append(1)
                    else:
                        aux_orient.append(0)

                orientacion_box.append(aux_orient)



            v_k = 0
            flag = True

            #[1,1,1,1,1]*[30,20,25,4,5]
            while flag:
                volumen_cargo = 0
                #calcula el volumen de de carga
                for i in range(n):
                    volumen_cargo +=cantidad_box_type[i]*volumen_box_type[i];

                aux=random.randint(0,n-1)
                v_k= volumen_box_type[aux]

                if tc > volumen_cargo + v_k:
                    cantidad_box_type[aux]+=1
                else:
                    break


            #Guarda la instancia creada
            for i in range(n):
                file.write(str(i+1))

                for j in range(3):
                    file.write(" "+str(dimension_box[i][j])+" "+str(orientacion_box[i][j]))
                file.write(" "+str(cantidad_box_type[i])+"\n")


            s+=100

    file.close()


def generarSolucionesSolver(instances=1):
    try:
        os.makedirs("tests/resultados_solver", exist_ok=True)
    except Exception as e:
        print(f"Error creating folder: {e}")

    for i in range(instances):  # Adjust the range as needed
        # Skip chmod on Windows
        if platform.system() != "Windows":
            os.system("chmod +x src/solvers/BSG_CLP")
        
        # Adjust the command for cross-platform compatibility
        solver_path = os.path.join("src/", "solvers/", "BSG_CLP")
        instances_file = os.path.join("tests/","instances/", "instances.txt")
        output_file = os.path.join("tests/", "resultados_solver/", f"output{i+1}.txt")

        if platform.system() == "Windows":
            solver_command = f"wsl ./{solver_path} {instances_file} -i {i} -t 5 --verbose > {output_file}"
        else:
            solver_command = f"./{solver_path} {instances_file} -i {i} -t 5 --verbose > {output_file}"

        # Execute the solver command
        try:
            os.system(solver_command)
        except Exception as e:
            print(f"Error executing solver command: {e}")