import sympy as sym

def calculate_transformation_matrix(q1, q2, q3, q4, q5):
    try:
        # Convertir los ángulos de grados a radianes
        q1, q2, q3, q4, q5 = [sym.rad(angle) for angle in [q1, q2, q3, q4, q5]]

        # Definir los elementos de la matriz de transformación
        R11 = -sym.sin(q1)*sym.sin(q5) + sym.cos(q1)*sym.cos(q5)*sym.cos(q2 + q3 + q4)
        R21 = -sym.sin(q1)*sym.cos(q5)*sym.cos(q2 + q3 + q4) + sym.sin(q5)*sym.cos(q1)
        R31 = sym.sin(q2 + q3 + q4)*sym.cos(q5)
        
        R12 = sym.sin(q1)*sym.cos(q5) - sym.sin(q5)*sym.cos(q1)*sym.cos(q2 + q3 + q4)
        R22 = -sym.sin(q1)*sym.sin(q5)*sym.cos(q2 + q3 + q4) + sym.cos(q1)*sym.cos(q5)
        R32 = -sym.sin(q5)*sym.sin(q2 + q3 + q4)
        
        R13 = -sym.sin(q2 + q3 + q4)*sym.cos(q1)
        R23 = -sym.sin(q1)*sym.sin(q2 + q3 + q4)
        R33 = sym.cos(q2 + q3 + q4)
        
        Px = -(0.177*sym.sin(q2) + 0.136*sym.sin(q2 + q3) + 0.195*sym.sin(q2 + q3 + q4))*sym.cos(q1)
        Py = -(0.177*sym.sin(q2) + 0.136*sym.sin(q2 + q3) + 0.195*sym.sin(q2 + q3 + q4))*sym.sin(q1)
        Pz = 0.177*sym.cos(q2) + 0.136*sym.cos(q2 + q3) + 0.195*sym.cos(q2 + q3 + q4) + 0.112

        # Crear la matriz de transformación
        transformation_matrix = sym.Matrix([
            [R11, R12, R13, Px],
            [R21, R22, R23, Py],
            [R31, R32, R33, Pz],
            [0,   0,   0,   1]
        ])

        # Calcular los ángulos de Euler a, b, g
        b = sym.atan2(-R31, sym.sqrt(R32**2 + R33**2))
        a = sym.atan2(R21/sym.cos(b), R11 / sym.cos(b))
        g = sym.atan2(R32 / sym.cos(b), R33 / sym.cos(b))

        # Convertir a, b, g a grados
        a_degree = sym.deg(a).evalf(4)
        b_degree = sym.deg(b).evalf(4)
        g_degree = sym.deg(g).evalf(4)

        # Retornar la matriz de transformación y los valores adicionales
        return {
            "matrix": transformation_matrix.evalf(4),
            "Px": Px.evalf(4),
            "Py": Py.evalf(4),
            "Pz": Pz.evalf(4),
            "a": a_degree,
            "b": b_degree,
            "g": g_degree
        }, None

    except Exception as e:
        # En caso de error, devolver None y el mensaje de error
        return None, f"Error en el cálculo de la matriz: {str(e)}"
