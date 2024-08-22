import numpy as np
import trimesh


def create_detachable_section_mesh(square_length, height, inner_radius, filename='tao',segments=256):
    outer_mesh = trimesh.creation.box((square_length, square_length, height))
    inner_mesh = trimesh.creation.cylinder(radius=inner_radius, height=height, sections=segments)
    tube_mesh = outer_mesh.difference(inner_mesh)
    stl_file_path = filename+'.stl'
    tube_mesh.export(stl_file_path)

    print(f"STL file created: {stl_file_path}")
    return tube_mesh


def create_detachable_section_mesh_lego(square_length, height, inner_radius, hole_depth, filename='a', segments=256):
    # Convert hole_depth to float if it's passed as a string
    hole_depth = float(hole_depth)

    # Create the main cuboid
    outer_mesh = trimesh.creation.box((square_length, square_length, height))

    # Define the offset for hole and cylinder placement
    offset = square_length / 2.5
    # Define the depth/height for the cylinders to ensure they are connected to the cuboid
    cylinder_height = hole_depth - 0.1  # Making cylinders slightly taller than the hole depth for connection

    # Positions for the holes on the bottom side
    hole_positions = [
        (offset, offset, -height/2+hole_depth / 2),  # Adjusted to ensure holes start from the bottom surface
        (-offset, offset, -height/2+hole_depth/2),
        (offset, -offset, -height/2+hole_depth/2),
        (-offset, -offset, -height/2+hole_depth / 2),
    ]

    # Positions for the cylinders on the top side
    cylinder_positions = [
        (offset, offset, height/2 + cylinder_height / 2),  # Adjusted to ensure cylinders are connected to the top surface
        (-offset, offset, height/2 + cylinder_height / 2),
        (offset, -offset, height/2 + cylinder_height / 2),
        (-offset, -offset, height/2 + cylinder_height / 2),
    ]

    # Subtract holes from the cuboid
    for x, y, z in hole_positions:
        hole = trimesh.creation.cylinder(radius=square_length*0.05, height=hole_depth, sections=segments)
        hole.apply_translation((x, y, z))
        outer_mesh = outer_mesh.difference(hole)

    inner_mesh = trimesh.creation.cylinder(radius=inner_radius, height=height, sections=segments)
    outer_mesh = outer_mesh.difference(inner_mesh)

    # Add cylinders to the top side of the cuboid
    for x, y, z in cylinder_positions:
        cylinder = trimesh.creation.cylinder(radius=square_length*0.05*0.8, height=cylinder_height, sections=segments)
        cylinder.apply_translation((x, y, z))
        outer_mesh += cylinder  # Assuming boolean operations work correctly in the environment

    # Export the mesh to an STL file
    stl_file_path = f'{filename}.stl'
    outer_mesh.export(stl_file_path)

    print(f"STL file created: {stl_file_path}")
    return outer_mesh


def detachable_tubemaker_3d(length_list, area_list, filename):
    assert len(length_list) == len(area_list)
    # get radius from area
    radius_list = np.sqrt(np.array(area_list) / np.pi)

    # for 3d printer, may not be univerisal
    radius_list = 10 * radius_list
    length_list = 10 * np.array(length_list)

    square_length = 2.5*max(radius_list)
    for i in range(len(length_list)):
        create_detachable_section_mesh_lego(square_length, length_list[i], radius_list[i], 5, filename+str(i+1))


def create_tube_mesh(inner_radius, height, thickness, segments=256, filename='i'):
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


def get_tube_specs(length_list, area_list, thickness=1):
    assert len(length_list) == len(area_list)
    # get radius from area
    radius_list = np.sqrt(np.array(area_list) / np.pi)

    # for 3d printer, may not be univerisal
    radius_list = 10 * radius_list
    length_list = 10 * np.array(length_list)

    tube_specs = [(radius_list[0], length_list[0], thickness)]
    for i in range(len(length_list) - 1):
        # the
        tube_specs.append((min(radius_list[i], radius_list[i + 1]),
                           thickness,
                           np.abs(radius_list[i] - radius_list[i + 1]) + thickness))
        # the actual tube section
        tube_specs.append((radius_list[i + 1], length_list[i + 1], thickness))
    # print(tube_specs)
    return tube_specs


def tubemaker_3d(length_list, area_list, file_name, thickness=1):
    # Initial position for the first tube
    z_position = 0

    # List to store each tube mesh
    tubes = []

    # Tube specifications (inner radius, height, thickness)
    '''
    tube_specs = [
        (1, 2, 0.1),  # Inner Radius 1, Height 2, Thickness 0.1
        (1,0.1,0.6),
        (1.5, 3, 0.1),  # Inner Radius 1.5, Height 3, Thickness 0.1
        (1.5,0.1,0.6),
        (2, 2, 0.1),  # Inner Radius 2, Height 4, Thickness 0.1
        (2,0.1,0.6),
        (2.5, 5, 0.1)  # Inner Radius 2.5, Height 5, Thickness 0.1
    ]
    '''
    tube_specs = get_tube_specs(length_list, area_list, thickness)
    # Create and position tubes
    for inner_radius, height, thickness in tube_specs:
        tube = create_tube_mesh(inner_radius=inner_radius, height=height, thickness=thickness)
        tube.apply_translation((0, 0, z_position + height / 2))  # Center tube at current z_position
        tubes.append(tube)
        z_position += height  # Update z_position for the next tube

    # Combine all tubes into a single mesh
    combined_mesh = trimesh.util.concatenate(tubes)

    # Export the combined mesh to an STL file
    stl_file_path = file_name + '.stl'
    combined_mesh.export(stl_file_path)

    print(f"STL file created: {stl_file_path}")


if __name__ == '__main__':
    detachable_tubemaker_3d([2, 6, 6, 2], [2,5,0.2,2])
