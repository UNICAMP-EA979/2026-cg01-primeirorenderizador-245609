import numpy as np
import urenderer

def get_ifs_cube(size: float = 1.0):
    """Create a cube geometry"""
    half = size / 2
    vertices = np.array([
        [-half, -half, -half],  # 0
        [ half, -half, -half],  # 1
        [ half, -half,  half],  # 2
        [-half, -half,  half],  # 3
        [-half,  half, -half],  # 4
        [ half,  half, -half],  # 5
        [ half,  half,  half],  # 6
        [-half,  half,  half]   # 7
    ])
    
    faces = [
        [0, 1, 2], [0, 2, 3],  # Bottom
        [4, 6, 5], [4, 7, 6],  # Top
        [0, 4, 5], [0, 5, 1],  # Front
        [1, 5, 6], [1, 6, 2],  # Right
        [2, 6, 7], [2, 7, 3],  # Back
        [3, 7, 4], [3, 4, 0]   # Left
    ]
    
    return vertices, faces

def get_ifs_pyramid(base_size: float = 0.8, height: float = 1.0):
    """Create a pyramid geometry"""
    half = base_size / 2
    
    vertices = np.array([
        [-half, -half, 0],  # 0
        [ half, -half, 0],  # 1
        [ half,  half, 0],  # 2
        [-half,  half, 0],  # 3
        [0, 0, height]      # 4
    ])
    
    faces = [
        [0, 1, 2], [0, 2, 3],  # Base
        [0, 1, 4],  # Front
        [1, 2, 4],  # Right
        [2, 3, 4],  # Back
        [3, 0, 4]   # Left
    ]
    
    return vertices, faces



# Crie uma cena com três objetos, um filho do outro:
# Objeto0 -> Objeto1 -> Objeto2
#
# Configure as transformações para que todos os objetos sejam visíveis e renderize a cena
#
# Altere a transformação do objeto avô dos outros e renderize a cena.
# Observe como que os objetos filhos se movem juntos

if __name__ == "__main__":
    urenderer.utils.clear_workdir("03-grandchild")
    renderer = urenderer.renderer.PyplotRenderer(1920, 1080)
    runtime = urenderer.application.Runtime(renderer, name="03-grandchild")
    
    cube_data = urenderer.geometry.polygonal_ifs.get_ifs_cube()

    _c_vert, _c_faces = get_ifs_cube()
    cube_data = {"geometry_vertex": _c_vert, "geometry_index": _c_faces}

   # Criar os objetos com geometrias diferentes para facilitar a visualização
    # Objeto0 (Avô) - Um cubo grande
    grandparent = urenderer.node.Node("grandparent_cube")
    grandparent.render_data['vertices'] = cube_data["geometry_vertex"]
    grandparent.render_data['faces'] = cube_data["geometry_index"]
    grandparent.render_data['color'] = 'red'
    grandparent.render_data['alpha'] = 0.6
    
    grandparent.render_data['geometry_vertex'] = cube_data["geometry_vertex"]
    grandparent.render_data['geometry_index'] = cube_data["geometry_index"]


    grandparent.translation = np.array([0, 0, 0])
    grandparent.scale = np.array([2.0, 2.0, 2.0])  # Cubo maior

    pyramid_data = urenderer.geometry.polygonal_ifs.get_ifs_pyramid()

    _p_vert, _p_faces = get_ifs_pyramid()
    pyramid_data = {"geometry_vertex": _p_vert, "geometry_index": _p_faces}
    
    # Objeto1 (Pai) - Uma pirâmide
    parent = urenderer.node.Node("parent_pyramid")
    parent.render_data['vertices'] = pyramid_data["geometry_vertex"]
    parent.render_data['faces'] = pyramid_data["geometry_index"]
    parent.render_data['color'] = 'green'
    parent.render_data['alpha'] = 0.7

    parent.render_data['geometry_vertex'] = pyramid_data["geometry_vertex"]
    parent.render_data['geometry_index'] = pyramid_data["geometry_index"]

    parent.translation = np.array([1.5, 0, 0])
    parent.scale = np.array([1.0, 1.0, 1.0])

    child = urenderer.node.Node("child_tetra")

    tetra_vertices = np.array([
        [0, 0, 0],
        [0.5, 0, 0],
        [0.25, 0.433, 0],
        [0.25, 0.144, 0.408]
    ], dtype=np.float64)
    
    tetra_faces = [
        [0, 1, 2],
        [0, 1, 3],
        [1, 2, 3],
        [2, 0, 3]
    ]
    
    child.render_data['vertices'] = tetra_vertices
    child.render_data['faces'] = tetra_faces
    child.render_data['color'] = 'blue'
    child.render_data['alpha'] = 0.8
    child.render_data['geometry_vertex'] = tetra_vertices
    child.render_data['geometry_index'] = tetra_faces
    # --------------------------------------------------------

    child.translation = np.array([1.0, 1.0, 0])
    child.scale = np.array([0.8, 0.8, 0.8])
    
    # Construir a hierarquia: Avô -> Pai -> Filho
    runtime.scene.add_child(grandparent)  # Avô é filho direto da cena
    grandparent.add_child(parent)          # Pai é filho do avô
    parent.add_child(child)               # Filho é filho do pai
    
    # Configurar a câmera para uma boa visualização
    runtime.camera.translation = np.array([5, 5, 8])
    runtime.camera.rotation = np.array([-30, 45, 0])
    runtime.camera.near_plane = 0.1
    runtime.camera.far_plane = 20.0
    runtime.camera.vertical_fov = 60.0
    
    print("=== Cena inicial - Sem rotação ===")
    print(f"Avô: cubo vermelho na origem (escala 2x)")
    print(f"Pai: pirâmide verde à direita do avô")
    print(f"Filho: tetraedro azul acima e à direita do pai")
    
    # Primeira renderização - hierarquia sem rotação
    runtime.iter(capture=True)
    print("Primeira renderização concluída\n")
    
    # Rotacionar o nó avô em torno do eixo Y
    print("=== Aplicando rotação ao Avô ===")
    grandparent.rotation = np.array([0, 60, 0])  # Rotação de 60 graus no eixo Y
    print("Avô rotacionado 60 graus no eixo Y")
    print("Observe que o pai e o filho também rotacionaram junto!\n")
    
    # Segunda renderização - com rotação do avô
    runtime.iter(capture=True)
    print("Segunda renderização concluída")
    
    # Opcional: Demonstrar translação do avô
    print("\n=== Aplicando translação ao Avô ===")
    grandparent.translation = np.array([1, 0.5, 0])
    print("Avô movido para (1, 0.5, 0)")
    print("Toda a família se moveu junto!\n")
    
    runtime.iter(capture=True)
    print("Terceira renderização concluída")
    
    print("\n=== Demonstração finalizada ===")
    print("Conceitos demonstrados:")
    print("- Hierarquia de transformações")
    print("- Transformações acumulativas (rotação e translação)")
    print("- Objetos filhos herdam transformações dos pais")