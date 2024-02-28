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

def get_tube_specs(length_list, area_list, thickness=0.1):

    assert len(length_list)==len(area_list)
    #get radius from area
    radius_list = np.sqrt(np.array(area_list)/np.pi)
    tube_specs = [(radius_list[0], length_list[0], thickness)]
    for i in range(len(length_list)-1):
        tube_specs.append((min(radius_list[i], radius_list[i+1]),
                           thickness,
                           np.abs(radius_list[i]-radius_list[i+1])+thickness))
        tube_specs.append((radius_list[i+1], length_list[i+1], thickness))
    #print(tube_specs)
    return tube_specs

def tubemaker_3d(length_list, area_list, thickness=0.1):
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
    tube_specs = get_tube_specs(length_list,area_list,thickness)
    # Create and position tubes
    for inner_radius, height, thickness in tube_specs:
        tube = create_tube_mesh(inner_radius=inner_radius, height=height, thickness=thickness)
        tube.apply_translation((0, 0, z_position + height / 2))  # Center tube at current z_position
        tubes.append(tube)
        z_position += height  # Update z_position for the next tube

    # Combine all tubes into a single mesh
    combined_mesh = trimesh.util.concatenate(tubes)

    # Export the combined mesh to an STL file
    stl_file_path = 'i.stl'
    combined_mesh.export(stl_file_path)

    print(f"STL file created: {stl_file_path}")
if __name__ == '__main__':
    tubemaker_3d([2,6,6,2],[0.1,5,1,2])
