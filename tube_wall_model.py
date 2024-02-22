import numpy as np
from stl import mesh


def add_hollow_square_tube(vertices, faces, start_pos, length, outer_width, thickness):
    """
    Add a hollow square tube to the vertices and faces lists.

    Parameters:
    - vertices: list of vertices
    - faces: list of faces
    - start_pos: start position of the tube (end of the previous tube)
    - length: length of the tube
    - outer_width: outer width of the tube's square cross-section
    - thickness: thickness of the tube walls
    """
    inner_width = outer_width - 2 * thickness  # Calculate inner width
    w_half = outer_width / 2.0
    w_inner_half = inner_width / 2.0

    # Initial vertex indices
    start_idx = len(vertices)

    # Outer square vertices
    outer_vert = np.array([
        [start_pos, -w_half, -w_half],
        [start_pos, w_half, -w_half],
        [start_pos, w_half, w_half],
        [start_pos, -w_half, w_half],
        [start_pos + length, -w_half, -w_half],
        [start_pos + length, w_half, -w_half],
        [start_pos + length, w_half, w_half],
        [start_pos + length, -w_half, w_half],
    ])

    # Inner square vertices (inverted to face inwards)
    inner_vert = np.array([
        [start_pos + thickness, -w_inner_half, -w_inner_half],
        [start_pos + thickness, w_inner_half, -w_inner_half],
        [start_pos + thickness, w_inner_half, w_inner_half],
        [start_pos + thickness, -w_inner_half, w_inner_half],
        [start_pos + length - thickness, -w_inner_half, -w_inner_half],
        [start_pos + length - thickness, w_inner_half, -w_inner_half],
        [start_pos + length - thickness, w_inner_half, w_inner_half],
        [start_pos + length - thickness, -w_inner_half, w_inner_half],
    ])

    # Add vertices
    vertices.extend(outer_vert)
    vertices.extend(inner_vert)

    # Define faces using the vertices (two triangles per face, 12 faces total for a hollow tube)
    tube_faces = [
        # Outer square faces
        [start_idx, start_idx + 1, start_idx + 5, start_idx + 4],
        [start_idx + 1, start_idx + 2, start_idx + 6, start_idx + 5],
        [start_idx + 2, start_idx + 3, start_idx + 7, start_idx + 6],
        [start_idx, start_idx + 3, start_idx + 7, start_idx + 4],
        # Inner square faces (inverted)
        [start_idx + 8, start_idx + 9, start_idx + 13, start_idx + 12],
        [start_idx + 9, start_idx + 10, start_idx + 14, start_idx + 13],
        [start_idx + 10, start_idx + 11, start_idx + 15, start_idx + 14],
        [start_idx + 8, start_idx + 11, start_idx + 15, start_idx + 12],
        # Connecting faces
        [start_idx, start_idx + 4, start_idx + 12, start_idx + 8],
        [start_idx + 2, start_idx + 6, start_idx + 14, start_idx + 10],
        [start_idx + 1, start_idx + 5, start_idx + 13, start_idx + 9],
        [start_idx + 3, start_idx + 7, start_idx + 15, start_idx + 11],
    ]

    # Convert quads to triangles
    for quad in tube_faces:
        faces.append([quad[0], quad[1], quad[2]])
        faces.append([quad[0], quad[2], quad[3]])


def create_hollow_connected_tubes(lengths, outer_width, thickness):
    """
    Create a model of hollow square tubes of different lengths connected in a line.

    Parameters:
    - lengths: list of lengths for each tube
    - outer_width: outer width of the tube's square cross-section
    - thickness: thickness of the tube walls
    """
    vertices = []
    faces = []

    # Starting position for the first tube
    start_pos = 0

    # Add tubes one after the other
    for length in lengths:
        add_hollow_square_tube(vertices, faces, start_pos, length, outer_width, thickness)
        start_pos += length  # Update start position for the next tube

    # Create the mesh
    connected_tubes_mesh = mesh.Mesh(np.zeros(len(faces), dtype=mesh.Mesh.dtype))
    for i, f in enumerate(faces):
        for j in range(3):
            connected_tubes_mesh.vectors[i][j] = vertices[f[j]]

    return connected_tubes_mesh

if __name__ =='__main__':
# Tube lengths, outer width, and wall thickness
    lengths = [10, 15, 20, 25]  # Different lengths for each tube
    outer_width = 2  # Outer width for all tubes
    thickness = 0.5  # Wall thickness

# Create hollow connected tubes and save to STL
    hollow_connected_tubes = create_hollow_connected_tubes(lengths, outer_width, thickness)
    hollow_connected_tubes.save('hollow_linear_connected_tubes.stl')

    print("Hollow linearly connected tubes STL file has been created.")
