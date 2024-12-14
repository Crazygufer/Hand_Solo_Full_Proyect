import cv2
import numpy as np

# Cargar el modelo MobileNet-SSD preentrenado
net = cv2.dnn.readNetFromCaffe('C:/Users/enfparedes/Contacts/Hand_Solo_Full_Proyect/app/utils/vision_artificial/deploy.prototxt', 'C:/Users/enfparedes/Contacts/Hand_Solo_Full_Proyect/app/utils/vision_artificial/mobilenet_iter_73000.caffemodel')

# Lista de las clases de objetos que el modelo puede detectar (en inglés)
CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat", "bottle", "bus",
           "car", "cat", "chair", "cow", "diningtable", "dog", "horse", "motorbike",
           "person", "pottedplant", "sheep", "sofa", "train", "tvmonitor"]

# Diccionario para traducir las clases al español
CLASSES_ES = {
    "background": "fondo", "aeroplane": "avión", "bicycle": "bicicleta", "bird": "pájaro", "boat": "barco", 
    "bottle": "botella", "bus": "autobús", "car": "coche", "cat": "gato", "chair": "silla", 
    "cow": "vaca", "diningtable": "mesa", "dog": "perro", "horse": "caballo", "motorbike": "motocicleta", 
    "person": "persona", "pottedplant": "planta", "sheep": "oveja", "sofa": "sofá", "train": "tren", 
    "tvmonitor": "televisor"
}

# URL del streaming de video del ESP32
#url = 'http://192.168.136.169/stream' #

# Conectar al stream de video
#cap = cv2.VideoCapture(url)

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: No se pudo conectar al stream de video.")
    exit()

print("Conexión establecida. Procesando video...")

while True:
    # Leer el frame del stream
    ret, frame = cap.read()

    if not ret:
        print("Error al capturar el frame.")
        break

    # Redimensionar el frame al tamaño requerido por el modelo
    blob = cv2.dnn.blobFromImage(frame, 0.007843, (300, 300), 127.5)
    net.setInput(blob)
    detections = net.forward()

    # Dimensiones de la imagen
    (h, w) = frame.shape[:2]

    # Dividir la imagen en cuadrantes
    centerX = w // 2
    centerY = h // 2

    # Recorrer las detecciones y dibujar cuadros alrededor de los objetos detectados
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > 0.5:  # Solo mostrar objetos con una confianza mayor al 50%
            idx = int(detections[0, 0, i, 1])
            label = CLASSES[idx]  # Nombre del objeto en inglés
            label_es = CLASSES_ES.get(label, label)  # Traducción al español

            # Calcular las coordenadas del cuadro
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")

            # Determinar el centro del objeto
            obj_centerX = (startX + endX) // 2
            obj_centerY = (startY + endY) // 2

            # Determinar el cuadrante
            if obj_centerX < centerX and obj_centerY < centerY:
                cuadrante = "Arriba-Izquierda"
            elif obj_centerX >= centerX and obj_centerY < centerY:
                cuadrante = "Arriba-Derecha"
            elif obj_centerX < centerX and obj_centerY >= centerY:
                cuadrante = "Abajo-Izquierda"
            else:
                cuadrante = "Abajo-Derecha"

            # Imprimir el objeto y el cuadrante en el terminal
            print(f"Objeto detectado: {label_es}, Cuadrante: {cuadrante}")

            # Dibujar el cuadro y la etiqueta en español
            cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 255, 0), 2)
            label_text = f"{label_es}: {confidence * 100:.2f}%"
            cv2.putText(frame, label_text, (startX, startY - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Mostrar el video con los objetos detectados y etiquetados en español
    cv2.imshow('Detección de objetos', frame)

    # Presionar 'q' para salir
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar la conexión y cerrar ventanas
cap.release()
cv2.destroyAllWindows()
