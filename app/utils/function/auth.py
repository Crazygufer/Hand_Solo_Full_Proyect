import csv
import os

# Función para validar el usuario en el login
def validar_usuario(username, password):
    with open('users.csv', mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            if row['username'] == username and row['password'] == password:
                return True
    return False

# Función para verificar si un usuario ya existe
def usuario_existe(username):
    if not os.path.exists('users.csv'):
        return False
    with open('users.csv', mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            if row['username'] == username:
                return True
    return False

# Función para registrar un nuevo usuario
def registrar_usuario(username, password):
    file_exists = os.path.exists('users.csv')
    with open('users.csv', mode='a', newline='') as file:
        fieldnames = ['username', 'password']
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()  # Escribir la cabecera si el archivo no existe

        writer.writerow({'username': username, 'password': password})
