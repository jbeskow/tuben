import numpy as np
from stl import mesh

def create_sphere(radius, resolution):
    # Create a grid of points
    u = np.linspace(0, 2 * np.pi, resolution)
    v = np.linspace(0, np.pi, resolution)
    x = radius * np.outer(np.cos(u), np.sin(v))
    y = radius * np.outer(np.sin(u), np.sin(v))
    z = radius * np.outer(np.ones(np.size(u)), np.cos(v))

    # Flatten the arrays
    x = x.flatten()
    y = y.flatten()
    z = z.flatten()

    # Create the faces
    faces = []
    for i in range(resolution - 1):
        for j in range(resolution - 1):
            # Define the vertices that compose each face
            v0 = i + j * resolution
            v1 = (i + 1) + j * resolution
            v2 = (i + 1) + (j + 1) * resolution
            v3 = i + (j + 1) * resolution
            faces.append([v0, v1, v2])
            faces.append([v0, v2, v3])

    # Create the mesh
    sphere_mesh = mesh.Mesh(np.zeros(len(faces), dtype=mesh.Mesh.dtype))
    for i, f in enumerate(faces):
        for j in range(3):
            sphere_mesh.vectors[i][j] = [x[f[j]], y[f[j]], z[f[j]]]

    return sphere_mesh


if __name__ == '__main__':
# Parameters
    radius = 10  # Radius of the sphere
    resolution = 50  # Number of points in each dimension

# Create sphere and save to STL
    sphere = create_sphere(radius, resolution)
    sphere.save('sphere.stl')

    print("Sphere STL file has been created.")
