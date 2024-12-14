import os
import yaml

# Ruta al directorio base del dataset
# Obtener la ruta base del script actual
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construir la ruta dinámica al dataset
dataset_dir = os.path.join(script_dir)

# Detectar clases automáticamente
classes = [folder for folder in os.listdir(dataset_dir) if os.path.isdir(os.path.join(dataset_dir, folder))]

# Crear el diccionario para el archivo YAML
data = {
    "path": dataset_dir,  # Ruta base del dataset
    "train": "images/train",  # Ruta relativa a las imágenes de entrenamiento
    "val": "images/val",  # Ruta relativa a las imágenes de validación
    "names": classes,  # Lista de clases detectadas
}

# Guardar el archivo YAML
yaml_path = os.path.join(dataset_dir, "data.yaml")
with open(yaml_path, "w") as yaml_file:
    yaml.dump(data, yaml_file, default_flow_style=False)

print(f"Archivo 'data.yaml' creado exitosamente en: {yaml_path}")
