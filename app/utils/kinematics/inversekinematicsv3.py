import numpy as np
import sympy as sym
from sympy import pi

class RobotKinematics:
    def __init__(self, L1, L2, L3, L4):
        # Longitudes de los segmentos del brazo
        self.L1 = L1
        self.L2 = L2
        self.L3 = L3
        self.L4 = L4

    def set_euler_angles(self, alpha, beta, gamma):
        """Establece los ángulos de Euler en radianes"""
        # Asignación corregida de los ángulos
        self.alpha = sym.rad(alpha)
        self.beta = sym.rad(beta)
        self.gamma = sym.rad(gamma)

    def euler_to_rotation_matrix(self):
        """Calcula la matriz de rotación a partir de los ángulos de Euler (ZYX) y evalúa numéricamente"""
        # Definir matrices de rotación individuales
        Rz = sym.Matrix([
            [sym.cos(self.alpha), -sym.sin(self.alpha), 0],
            [sym.sin(self.alpha),  sym.cos(self.alpha), 0],
            [0,              0,              1]
        ])
        Ry = sym.Matrix([
            [sym.cos(self.beta), 0, sym.sin(self.beta)],
            [0,             1, 0],
            [-sym.sin(self.beta), 0, sym.cos(self.beta)]
        ])
        Rx = sym.Matrix([
            [1, 0,              0],
            [0, sym.cos(self.gamma), -sym.sin(self.gamma)],
            [0, sym.sin(self.gamma),  sym.cos(self.gamma)]
        ])
        # Usar el orden de rotación ZYX (Yaw-Pitch-Roll)
        self.rotation_matrix = (Rz * Ry * Rx).evalf()  # Evaluar la matriz numéricamente
        return self.rotation_matrix

    def calculate_wrist_position(self, Xf, Yf, Zf):
        """Calcula la posición de la muñeca a partir de la posición del efector final"""
        # Obtener la matriz de rotación en formato numérico
        Rf_np = np.array(self.rotation_matrix, dtype=float)
        
        # Extraer el vector de dirección del eje Z de la matriz de rotación
        nz = Rf_np[:, 2]
        
        # Calcular la posición de la muñeca
        Xm = Xf - self.L4 * nz[0]
        Ym = Yf - self.L4 * nz[1]
        Zm = Zf - self.L4 * nz[2]
        
        return Xm, Ym, Zm

    def inverse_kinematics(self, Xm, Ym, Zm):
        """Calcula los ángulos de las articulaciones para alcanzar la posición de la muñeca"""
        # Cálculo de theta1
        theta1 = np.arctan2(-Ym, -Xm)
        
        # Cálculo intermedio para r y D
        r = np.sqrt(Xm**2 + Ym**2)
        print(r)
        D = ((r**2 + (Zm - self.L1)**2 - self.L2**2 - self.L3**2) / (2 * self.L2 * self.L3))
        print(D)
        # Configuración del codo
        elbow_config = 'down'
        
        # Calcular theta3
        if elbow_config == 'down':
            theta3 = np.arctan2(np.sqrt(1 - D**2), D)
        else:
            theta3 = np.arctan2(np.sqrt(1 + D**2), D)
        
        # Calcular theta2
        s = Zm - self.L1
        theta2 = np.arctan2(r, s) - np.arctan2(self.L3 * np.sin(theta3), self.L2 + self.L3 * np.cos(theta3))
        
        # Calcular theta4 y theta5 usando la matriz de rotación Rf
        Rf = np.array(self.rotation_matrix.evalf(), dtype=float)
        
        K = Rf[0, 1] * np.sin(theta1) - Rf[1, 1] * np.cos(theta1)
        KK = (Rf[0, 2] * np.sin(theta2 + theta3) * np.cos(theta1) +
              -Rf[1, 2] * np.sin(theta1) * np.sin(theta2 + theta3) -
              Rf[2, 2] * np.cos(theta2 + theta3))
        

        KK2 = (Rf[0,2] * np.cos(theta1) * np.cos(theta2 + theta3) + Rf[1,2] * np.sin(theta1)*np.cos(theta2 + theta3) + Rf[2,2]*np.sin(theta2 + theta3))


        #theta4 = np.arctan2(np.sqrt(1 - KK**2), KK)
        #parece que también se condiciona a codo arriba y codo abajo
        theta4 = -(np.arctan2(KK2, np.sqrt(1 - KK2**2),))
        print(theta4)
        theta5 = np.arctan2(np.sqrt(1 - K**2), -K)
        print(theta1)
        print(theta5)
        # Convertir ángulos a grados y normalizarlos
        angles_degrees = [self.normalize_angle(angle) for angle in np.degrees([theta1, theta2, theta3, theta4, theta5])]
        
        return angles_degrees

    @staticmethod
    def normalize_angle(angle):
        """ Normaliza el ángulo a un rango de [-180, 180) grados """
        normalized_angle = angle % 360  # Convierte a [0, 360)
        if normalized_angle > 180:
            normalized_angle -= 360  # Ajusta a [-180, 180)
        return normalized_angle

# Distancias
L1, L2, L3, L4 = 0.112, 0.177, 0.136, 0.195
kinematics = RobotKinematics(L1, L2, L3, L4)

# Definir ángulos de Euler y posición del efector
alpha, beta, gamma = 0, -55, 0
Xf, Yf, Zf = -0.41635, 0 , 0.40307

# Configurar ángulos en el objeto
kinematics.set_euler_angles(alpha, beta, gamma)

# Obtener la matriz de rotación
rotation_matrix = kinematics.euler_to_rotation_matrix()
print("Matriz de Rotación Numérica:")
sym.pprint(rotation_matrix)

# Calcular la posición de la muñeca con respecto a una posición final del efector
Xm, Ym, Zm = kinematics.calculate_wrist_position(Xf, Yf, Zf)
print(f"Posición de la muñeca: Xm={Xm}, Ym={Ym}, Zm={Zm}")

"""# Calcular ángulos de las articulaciones para alcanzar la posición de la muñeca
joint_angles = kinematics.inverse_kinematics(Xm, Ym, Zm)
print(f"Ángulos de las articulaciones en grados: {joint_angles}")
"""
# Imprimir los ángulos en formato vertical
joint_angles = kinematics.inverse_kinematics(Xm, Ym, Zm)
for i, angle in enumerate(joint_angles, start=1):
    print(f"Theta{i} = {angle:.2f} grados")