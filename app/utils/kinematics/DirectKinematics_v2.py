# Cargamos la librería, creamos un cliente y obtenemos acceso a sim
import zmqRemoteApi
import sympy as sym
client = zmqRemoteApi.RemoteAPIClient()
sim = client.getObject('sim')

# Obtenemos los manejadores para las articulaciones y el actuador final
j1 = sim.getObject('/Base_01_invisible/q1')
j2 = sim.getObject('/Base_01_invisible/q2')
j3 = sim.getObject('/Base_01_invisible/q3')
j4 = sim.getObject('/Base_01_invisible/q4')
j5 = sim.getObject('/Base_01_invisible/q5')
conn = sim.getObject('/Base_01_invisible/14_Pinza_01')

# y movemos a una posicion deseada
q1 = 90 * 3.1416/180
q2 = 45 * 3.1416/180
q3 = 30 * 3.1416/180
q4 = 30 * 3.1416/180
q5 = 0 * 3.1416/180

sim.setJointTargetPosition(j1, q1)
sim.setJointTargetPosition(j2, q2)
sim.setJointTargetPosition(j4, q4)
sim.setJointTargetPosition(j5, q5)
sim.setJointTargetPosition(j3, q3)


R11 = -sym.sin(q1)*sym.sin(q5)+sym.cos(q1)*sym.cos(q5)*sym.cos(q2+q3+q4)
R21 = -sym.sin(q1)*sym.cos(q5)*sym.cos(q2 + q3 + q4) + sym.sin(q5)*sym.cos(q1)
R31 = sym.sin(q2+q3+q4)*sym.cos(q5)
R12 = sym.sin(q1)*sym.cos(q5)-sym.sin(q5)*sym.cos(q1)*sym.cos(q2+q3+q4)
R22 = -sym.sin(q1)*sym.sin(q5)*sym.cos(q2+q3+q4)+sym.cos(q1)*sym.cos(q5)
R32 = -sym.sin(q5)*sym.sin(q2+q3+q4)
R13 = -sym.sin(q2+q3+q4)*sym.cos(q1)
R23 = -sym.sin(q1)*sym.sin(q2+q3+q4)
R33 = sym.cos(q2+q3+q4)
Px = -(0.177*sym.sin(q2) + 0.136*sym.sin(q2 + q3) + 0.195*sym.sin(q2 + q3 + q4))*sym.cos(q1)
Py = -(0.177*sym.sin(q2) + 0.136*sym.sin(q2 + q3) + 0.195*sym.sin(q2 + q3 + q4))*sym.sin(q1)
Pz = 0.177*sym.cos(q2) + 0.136*sym.cos(q2 + q3) + 0.195*sym.cos(q2 + q3 + q4) + 0.112


transformation_matrix = sym.Matrix([
    [R11, R12, R13, Px],
    [R21, R22, R23, Py],
    [R31, R32, R33, Pz],
    [0,   0,   0,   1]
])

b = sym.atan2(-R31, sym.sqrt(R32**2 + R33**2))
a = sym.atan2(R21/sym.cos(b), R11 / sym.cos(b))
g = sym.atan2(R32 / sym.cos(b), R33 / sym.cos(b))

a_degree = sym.deg(a) 
b_degree = sym.deg(b) 
g_degree = sym.deg(g) 


print(a.evalf(4))
print(b.evalf(4))
print(g.evalf(4))
print('a es igual a:', a_degree.evalf(4))
print('b es igual a:', b_degree.evalf(4))
print('g es igual a:', g_degree.evalf(4))


# Print the transformation matrix
transformation_matrix = transformation_matrix.evalf(4)

# Imprimir la matriz de transformación
sym.pprint(transformation_matrix)

print('X es igual a', Px.evalf(4), "m")
print('Y es igual a', Py.evalf(4), "m")
print('Z es igual a', Pz.evalf(4), "m")

print('X es igual a', Px.evalf(4)*100, "cm")
print('Y es igual a', Py.evalf(4)*100, "cm")
print('Z es igual a', Pz.evalf(4)*100, "cm")