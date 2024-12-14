import tensorflow as tf
import numpy as np
import cv2

# Cargar el modelo entrenado
model = tf.keras.models.load_model('C:/Users/enfparedes/Contacts/Hand_Solo_Full_Proyect/app/utils/vision_artificial/Version2/modelo_mobilenet(8cosas)_transfer_learning.keras')

# Diccionario con las clases correspondientes a las categorías entrenadas
CLASSES_ES = {
    0: 'Bolígrafo', 
    1: 'Cargador', 
    2: 'Celular', 
    3: 'Cuchara', 
    4: 'Cuchillo', 
    5: 'Tenedor',
    6: 'Persona', 
    7: 'Botella'
}

# URL del streaming de video del ESP32
#url = 'http://192.168.177.169/stream'

# Conectar al stream de video
#print(f"Intentando conectar a {url}...")

#cap = cv2.VideoCapture(url)
cap = cv2.VideoCapture(0)

# Aumentar el timeout del stream y ajustes adicionales
cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)
cap.set(cv2.CAP_PROP_FPS, 10)
cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 60000)  # Aumentar tiempo de espera

# Verificar si la conexión se abre correctamente
if not cap.isOpened():
    print("Error: No se pudo conectar al stream de video.")
    exit()

print("Conexión establecida. Procesando video...")

IMG_SIZE = 224  # Tamaño de imagen que espera el modelo

while True:
    # Leer el frame del stream
    ret, frame = cap.read()

    if not ret:
        print("Error al capturar el frame. Verifica la conexión con el ESP32.")
        break

    print("Frame capturado con éxito.")

    # Redimensionar el frame al tamaño requerido por el modelo
    resized_frame = cv2.resize(frame, (IMG_SIZE, IMG_SIZE))
    normalized_frame = resized_frame / 255.0  # Normalizar los valores de los píxeles

    # Convertir la imagen en un array y expandir dimensiones para que sea compatible con el modelo
    input_image = np.expand_dims(normalized_frame, axis=0)

    # Realizar predicción
    predictions = model.predict(input_image)
    predicted_class = np.argmax(predictions[0])  # Clase con mayor probabilidad
    confidence = predictions[0][predicted_class] * 100  # Confianza en la predicción

    # Obtener el nombre de la clase predicha
    label_es = CLASSES_ES.get(predicted_class, 'Desconocido')

    # Dibujar el cuadro y la etiqueta en español
    # Aquí dibujamos un cuadro alrededor de toda la imagen porque MobileNet no usa bounding boxes
    (h, w) = frame.shape[:2]
    cv2.rectangle(frame, (10, 10), (w - 10, h - 10), (0, 255, 0), 2)  # Cuadro alrededor del objeto
    cv2.putText(frame, f'{label_es}: {confidence:.2f}%', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Mostrar el video con las predicciones
    cv2.imshow('Detección en tiempo real', frame)

    # Presionar 'q' para salir
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar la conexión y cerrar ventanas
cap.release()
cv2.destroyAllWindows()
