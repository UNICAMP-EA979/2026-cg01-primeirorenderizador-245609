import numpy as np
def get_ifs_tetrahedron(size: float = 0.5):
    """Create a tetrahedron geometry"""
    # Altura de um tetraedro regular: sqrt(2/3) * size
    height = np.sqrt(2/3) * size
    # Altura do centro da base ao vértice: size * sqrt(3)/6
    center_height = size * np.sqrt(3) / 6
    
    vertices = np.array([
        [0, 0, 0],
        [size, 0, 0],
        [size/2, np.sqrt(3)/2 * size, 0],
        [size/2, center_height, height]
    ])
    
    faces = [
        [0, 1, 2],  # Base
        [0, 1, 3],  # Face 1
        [1, 2, 3],  # Face 2
        [2, 0, 3]   # Face 3
    ]
    
    return{"geometry_vertex": vertices, "geometry_index": faces} 