import requests

# Dirección IP del ESP32
ESP32_IP = "http://192.168.9.46"  # Reemplaza esta IP con la IP que obtuviste
#ESP32_IP = "http://192.168.9.169"  # Reemplaza esta IP con la IP que obtuviste


def establecer_angulo(motor, angulo):
    try:
        # Definir la URL con el motor y ángulo como parámetros
        url = f"{ESP32_IP}/set_angle?motor={motor}&angle={angulo}"
        response = requests.get(url)
        if response.status_code == 200:
            print(f"Ángulo del motor {motor} establecido a {angulo} grados")
        else:
            print(f"Error al establecer ángulo: {response.status_code}")
    except requests.RequestException as e:
        print(f"Error de conexión: {e}")

# Ejemplo de uso
if __name__ == "__main__":
    # Establecer el ángulo de cada motor
    # Motor 1 (Base) a 90 grados
    establecer_angulo(0, 90)
    
    # Motor 2 (Articulación 2) a 45 grados
    # Motor 3 se moverá automáticamente a 135 grados porque es espejo del motor 2
    establecer_angulo(1, 90)
    
    # Motor 4 (Articulación 4) a 60 grados +90
    establecer_angulo(3, 90)
    
    # Motor 5 (Articulación 5) a 30 grados
    establecer_angulo(4, 90)
    
    # Motor 6 (Articulación 5) """Rotativo"""
    establecer_angulo(5, 90)
    
    # Motor 7 (Efector) a 90 grados
    establecer_angulo(6, 90)
