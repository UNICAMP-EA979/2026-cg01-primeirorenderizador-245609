import numpy as np
import urenderer

# Crie uma cena contendo uma pirâmide e renderize ela
#
# Implemente urenderer.geometry.polygonal_ifs.get_ifs_pyramid para obter a geometria de uma pirâmide

if __name__ == "__main__":
    urenderer.utils.clear_workdir("02-pyramid")
    renderer = urenderer.renderer.PyplotRenderer(1920, 1080)
    runtime = urenderer.application.Runtime(renderer, name="02-pyramid")

    # Crie a pirâmide
    pyramid_node = urenderer.node.Node("pyramid")
    
    # Obter a geometria da pirâmide
    vertices, faces = urenderer.geometry.polygonal_ifs.get_ifs_pyramid()
    
    # Adicionar dados de renderização
    pyramid_node.render_data['vertices'] = vertices
    pyramid_node.render_data['faces'] = faces
    pyramid_node.render_data['color'] = 'orange'
    pyramid_node.render_data['alpha'] = 0.8
    
    # Posicionar a pirâmide na cena
    pyramid_node.translation = np.array([0, 0, 0])
    pyramid_node.rotation = np.array([0, 0, 0])  # Sem rotação inicial
    pyramid_node.scale = np.array([1, 1, 1])
    
    # Adicionar a pirâmide à cena
    runtime.scene.add_child(pyramid_node)
    
    # Configurar a câmera para uma boa visualização
    runtime.camera.translation = np.array([200, 200, 300])  # Posicionar câmera na diagonal
    runtime.camera.rotation = np.array([-30, 45, 0])  # Rotacionar para olhar para a pirâmide
    runtime.camera.near_plane = 1.0
    runtime.camera.far_plane = 500.0
    runtime.camera.vertical_fov = 60.0
    
    # Opcional: Adicionar um chão ou grade para referência
    ground_node = urenderer.node.Node("ground")
    grid_size = 5
    grid_points = []
    for i in range(-grid_size, grid_size + 1):
        grid_points.append([i, -grid_size, -0.01])
        grid_points.append([i, grid_size, -0.01])
        grid_points.append([-grid_size, i, -0.01])
        grid_points.append([grid_size, i, -0.01])
    
    axes_vertices = np.array([[0, 0, 0], [200, 0, 0],  # X axis
        [0, 0, 0], [0, 200, 0],  # Y axis
        [0, 0, 0], [0, 0, 200]   # Z axis
    ])
    axes_faces = [[0, 1], [2, 3], [4, 5]]  # Linhas
    axes_node = urenderer.node.Node("axes")
    axes_node.render_data['vertices'] = axes_vertices
    axes_node.render_data['faces'] = axes_faces
    axes_node.render_data['color'] = 'white'
    ground_node.render_data['alpha'] = 0.3
    runtime.scene.add_child(axes_node)
    print(f"Vértices da pirâmide: {vertices}")
    print(f"Faces: {faces}")
    
    runtime.iter(capture=True)
    print("Renderização concluída")
