# MCLP_with_DL

Este proyecto busca enseñar a un modelo transformer resolver el Container Loading Problem (CLP) utilizando python y tensorflow.

---

Para ejecutar el proyecto
```python

# Crear ambiente 
python -m venv venv
# Activa el entorno:
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate


#Instalar dependencias
pip install -r requirements.txt
```

Si se esta ejecutando el proyecto en windows
```python

#Si se ejecuta en windows instalar ubuntu con wsl
wsl --install -d Ubuntu
wsl --set-default Ubuntu
```
> **Nota:** Se recomienda reiniciar el interprete una vez instalado ubuntu.

---

Estructura del Proyecto

```
MCLP_WITH_DL/
├── src/                    # Código fuente del proyecto
│   ├── models/             # Modelos y clases para el almacenamiento de los datos
│   ├── solvers/            # Solvers para el clp
│   ├── utils/              # Utilidades para el manejo de los datos
│   ├── __init__.py         # Inicialización del paquete
│   └── main.py             # Archivo principal del proyecto
├── tests/                  # Pruebas unitarias
│   ├── instances/          # Carpeta para guardan las instancias
│   └── resultados_solver/  # Carpeta para guardar los archivos resultantes del solver
├── .gitignore              # Archivos ignorados por Git
├── requirements.txt        # Dependencias del proyecto
└── README.md               # Documentación
```

---

Estructura de Git

```
MCLP_WITH_DL/
├── Main/                       # Rama prrincipal
│   ├── README.md               # Documentación
│   └── develop/                # Rama de desarrollo
│       ├── develop_TioPanxo/   # Rama de desarrollo usuario TioPanxo
```