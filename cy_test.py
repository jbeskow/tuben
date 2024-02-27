import numpy as np
import trimesh


def create_tube_mesh(inner_radius, height, thickness, segments=32):
    """
    Creates a mesh for a tube (pipe) with the given inner radius, height, and wall thickness.

    Args:
    - inner_radius: Inner radius of the tube.
    - height: Height of the tube.
    - thickness: Wall thickness of the tube.
    - segments: Number of segments for the tube's circular cross-section.

    Returns:
    - A trimesh.Trimesh object representing the tube.
    """
    outer_radius = inner_radius + thickness
    # Create outer cylinder
    outer_mesh = trimesh.creation.cylinder(radius=outer_radius, height=height, sections=segments)
    # Create inner cylinder
    inner_mesh = trimesh.creation.cylinder(radius=inner_radius, height=height, sections=segments)

    # Subtract the inner cylinder from the outer cylinder to create a hollow tube
    tube_mesh = outer_mesh.difference(inner_mesh)

    return tube_mesh


# Initial position for the first tube
z_position = 0

# List to store each tube mesh
tubes = []

# Tube specifications (inner radius, height, thickness)
tube_specs = [
    (1, 2, 0.1),  # Inner Radius 1, Height 2, Thickness 0.1
    (1,0.1,0.6),
    (1.5, 3, 0.1),  # Inner Radius 1.5, Height 3, Thickness 0.1
    (1.5,0.1,0.6),
    (2, 2, 0.1),  # Inner Radius 2, Height 4, Thickness 0.1
    (2,0.1,0.6),
    (2.5, 5, 0.1)  # Inner Radius 2.5, Height 5, Thickness 0.1
]

# Create and position tubes
for inner_radius, height, thickness in tube_specs:
    tube = create_tube_mesh(inner_radius=inner_radius, height=height, thickness=thickness)
    tube.apply_translation((0, 0, z_position + height / 2))  # Center tube at current z_position
    tubes.append(tube)
    z_position += height  # Update z_position for the next tube

# Combine all tubes into a single mesh
combined_mesh = trimesh.util.concatenate(tubes)

# Export the combined mesh to an STL file
stl_file_path = 'combined_tubes_no_space.stl'
combined_mesh.export(stl_file_path)

print(f"STL file created: {stl_file_path}")
