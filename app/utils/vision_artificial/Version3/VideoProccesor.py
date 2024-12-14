import cv2
import os
import time
import tkinter as tk
from tkinter import messagebox
import random
import shutil


class VideoProcessorYOLO:
    def __init__(self, root):
        self.root = root
        self.root.title("Captura y Procesamiento de Imágenes para YOLO")

        # Variables
        self.objeto = tk.StringVar()
        self.tiempo_captura = tk.IntVar(value=10)

        # Configurar la ruta base al directorio del script
        script_dir = os.path.dirname(os.path.abspath(__file__))  # Ruta donde se encuentra el script actual
        self.base_dir = os.path.join(script_dir, "dataset")  # Crear el directorio "dataset" en el mismo lugar que el script

        # Crear el directorio base si no existe
        os.makedirs(self.base_dir, exist_ok=True)

        # Interfaz
        tk.Label(root, text="Nombre del Objeto:").pack(pady=5)
        tk.Entry(root, textvariable=self.objeto).pack(pady=5)

        tk.Label(root, text="Tiempo de Captura (segundos):").pack(pady=5)
        tk.Entry(root, textvariable=self.tiempo_captura).pack(pady=5)

        tk.Button(root, text="Comenzar Captura", command=self.comenzar_captura).pack(pady=10)
        tk.Button(root, text="Salir", command=root.quit).pack(pady=10)

    def comenzar_captura(self):
        objeto = self.objeto.get().strip()
        tiempo_captura = self.tiempo_captura.get()

        if not objeto:
            messagebox.showerror("Error", "Por favor, ingresa el nombre del objeto.")
            return

        if tiempo_captura <= 0:
            messagebox.showerror("Error", "El tiempo de captura debe ser mayor a 0.")
            return

        # Crear carpetas específicas del objeto
        objeto_dir = os.path.join(self.base_dir, objeto)
        images_dir = os.path.join(objeto_dir, "images")
        labels_dir = os.path.join(objeto_dir, "labels")
        for sub_dir in ["train", "val"]:
            os.makedirs(os.path.join(images_dir, sub_dir), exist_ok=True)
            os.makedirs(os.path.join(labels_dir, sub_dir), exist_ok=True)

        # Capturar video
        video_path = os.path.join(images_dir, f"{objeto}_video.mp4")
        self.grabar_video(video_path, tiempo_captura)

        # Descomponer video en frames
        raw_images_dir = os.path.join(images_dir, "raw")
        os.makedirs(raw_images_dir, exist_ok=True)
        self.descomponer_video(video_path, raw_images_dir)

        # Etiquetar manualmente los frames
        self.etiquetar_frames(objeto, raw_images_dir, labels_dir)

        # Dividir las imágenes y etiquetas en train y val
        self.dividir_train_val(raw_images_dir, labels_dir, images_dir)

    def grabar_video(self, video_path, tiempo_captura):
        """
        Graba un video desde la cámara durante un tiempo especificado.
        """
        cap = cv2.VideoCapture(1)
        if not cap.isOpened():
            messagebox.showerror("Error", "No se pudo acceder a la cámara.")
            return

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codificador para MP4
        fps = 30  # Fotogramas por segundo
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        out = cv2.VideoWriter(video_path, fourcc, fps, (frame_width, frame_height))
        start_time = time.time()

        while time.time() - start_time < tiempo_captura:
            ret, frame = cap.read()
            if not ret:
                print("Error al capturar el frame.")
                break

            out.write(frame)
            cv2.imshow("Grabando Video...", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Grabación detenida por el usuario.")
                break

        cap.release()
        out.release()
        cv2.destroyAllWindows()
        messagebox.showinfo("Grabación Completa", f"Video guardado en {video_path}.")

    def descomponer_video(self, video_path, raw_images_dir):
        """
        Divide un video en frames individuales y los guarda como imágenes.
        """
        cap = cv2.VideoCapture(video_path)
        frame_count = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Guardar cada frame como imagen
            frame_path = os.path.join(raw_images_dir, f"frame_{frame_count:04d}.jpg")
            cv2.imwrite(frame_path, frame)
            frame_count += 1

        cap.release()
        print(f"{frame_count} imágenes extraídas del video y guardadas en {raw_images_dir}.")

    def etiquetar_frames(self, objeto, raw_images_dir, labels_dir):
        """
        Permite etiquetar cada X frames y copia la etiqueta para frames intermedios.
        """
        raw_labels_dir = os.path.join(labels_dir, "raw")
        os.makedirs(raw_labels_dir, exist_ok=True)

        images = sorted([img for img in os.listdir(raw_images_dir) if img.endswith(".jpg")])
        previous_label = None

        for idx, img in enumerate(images):
            frame = cv2.imread(os.path.join(raw_images_dir, img))

            # Solo etiquetar cada 100 frames
            if idx % 100 == 0:
                bbox = cv2.selectROI("Etiqueta el Objeto", frame, fromCenter=False, showCrosshair=True)
                cv2.destroyWindow("Etiqueta el Objeto")
                if bbox:
                    x, y, w, h = bbox
                    previous_label = f"0 {(x+w/2)/frame.shape[1]:.6f} {(y+h/2)/frame.shape[0]:.6f} {w/frame.shape[1]:.6f} {h/frame.shape[0]:.6f}\n"

            # Si tenemos una etiqueta previa, copiarla
            if previous_label:
                label_path = os.path.join(raw_labels_dir, img.replace(".jpg", ".txt"))
                with open(label_path, "w") as f:
                    f.write(previous_label)
         # Mostrar mensaje de confirmación al finalizar
        messagebox.showinfo("Etiquetado Completo", f"Se han etiquetado correctamente {len(images)} frames.")

    def dividir_train_val(self, raw_images_dir, labels_dir, images_dir):
        """
        Divide las imágenes y etiquetas en train y val.
        """
        # Lista de imágenes
        images = [img for img in os.listdir(raw_images_dir) if img.endswith(".jpg")]
        random.shuffle(images)

        # Dividir en train y val
        split_index = int(0.8 * len(images))
        train_images = images[:split_index]
        val_images = images[split_index:]

        for subset, subset_images in [("train", train_images), ("val", val_images)]:
            for img in subset_images:
                shutil.move(os.path.join(raw_images_dir, img), os.path.join(images_dir, subset))
                label_file = img.replace(".jpg", ".txt")
                shutil.move(os.path.join(labels_dir, "raw", label_file), os.path.join(labels_dir, subset))


# Ejecutar la aplicación
if __name__ == "__main__":
    root = tk.Tk()
    app = VideoProcessorYOLO(root)
    root.mainloop()
