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

---

Estructura del Proyecto

```
MCLP_WITH_DL/
├── src/                # Código fuente del proyecto
│   ├── models/         # Modelos y clases para el almacenamiento de los datos
│   ├── __init__.py     # Inicialización del paquete
│   └── ...
├── tests/              # Pruebas unitarias
│   ├── __init__.py     # Inicialización del paquete
│   └── ...
├── .gitignore          # Archivos ignorados por Git
├── requirements.txt    # Dependencias del proyecto
└── README.md           # Documentación
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