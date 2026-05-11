import numpy as np
import urenderer

def get_ifs_pyramid():
    vertices = np.array([
        [ 0.0,  1.0,  0.0],  # 0: Topo da Pirâmide
        [-1.0, -1.0,  1.0],  # 1: Base Frente-Esquerda
        [ 1.0, -1.0,  1.0],  # 2: Base Frente-Direita
        [ 1.0, -1.0, -1.0],  # 3: Base Trás-Direita
        [-1.0, -1.0, -1.0]   # 4: Base Trás-Esquerda
    ])
    
    # Índices dos triângulos conectando os vértices
    faces = [
        [0, 1, 2],  # Parede da Frente
        [0, 2, 3],  # Parede da Direita
        [0, 3, 4],  # Parede de Trás
        [0, 4, 1],  # Parede da Esquerda
        [1, 3, 2],  # Metade do Chão
        [1, 4, 3]   # Outra Metade do Chão
    ]
    return vertices, faces

if __name__ == "__main__":
    urenderer.utils.clear_workdir("02-pyramid")
    renderer = urenderer.renderer.PyplotRenderer(1920, 1080)
    runtime = urenderer.application.Runtime(renderer, name="02-pyramid")

    # Crie a pirâmide
    pyramid_node = urenderer.node.Node("pyramid")
    

    vertices, faces = get_ifs_pyramid()

    pyramid_node.render_data['vertices'] = vertices
    pyramid_node.render_data['faces'] = faces
    pyramid_node.render_data['color'] = 'orange'
    pyramid_node.render_data['alpha'] = 0.8
    
    pyramid_node.render_data['geometry_vertex'] = vertices
    pyramid_node.render_data['geometry_index'] = faces
    
    # Posicionar a pirâmide na cena
    pyramid_node.translation = np.array([0, 0, 0])
    pyramid_node.rotation = np.array([0, 0, 0])  # Sem rotação inicial
    
    #Aumento da escala de [1,1,1] para [100,100,100] 
    pyramid_node.scale = np.array([100, 100, 100])
    
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
    
    axes_vertices = np.array([[0, 0, 0], [200, 0, 0],  
        [0, 0, 0], [0, 200, 0],  
        [0, 0, 0], [0, 0, 200]   
    ])
    axes_faces = [[0, 1], [2, 3], [4, 5]]  # Linhas
    axes_node = urenderer.node.Node("axes")
    axes_node.render_data['vertices'] = axes_vertices
    axes_node.render_data['faces'] = axes_faces
    axes_node.render_data['color'] = 'white'
    ground_node.render_data['alpha'] = 0.3
    runtime.scene.add_child(axes_node)
    
    print(f"Vértices da pirâmide: \n{vertices}")
    print(f"Faces: \n{faces}")
    
    runtime.iter(capture=True)
    print("Renderização concluída")