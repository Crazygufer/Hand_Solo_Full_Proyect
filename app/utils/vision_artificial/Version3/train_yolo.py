from ultralytics import YOLO

# Ruta estática para el archivo del modelo YOLO
model_path = r"C:\Users\enfparedes\Contacts\Hand_Solo_Full_Proyect\app\utils\vision_artificial\Version3\yolo11n.pt"

# Ruta estática para el archivo YAML
yaml_path = r"C:\Users\enfparedes\Contacts\Hand_Solo_Full_Proyect\app\utils\vision_artificial\Version3\DataSet\data.yaml"

# Cargar el modelo YOLO
model = YOLO(model_path)

# Entrenar el modelo
results = model.train(
    data=yaml_path,
    epochs=10,   # Número de iteraciones
    imgsz=640,   # Tamaño de las imágenes
    plots=True   # Guardar gráficos del entrenamiento
)

print("Entrenamiento completado.")
