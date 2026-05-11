import numpy as np
import urenderer

# Renderize uma cena em que o algoritmo de oclusão falha
#
# Observe o método urenderer.renderer.pyplot_renderer.PyplotRenderer::end
# Ele desenha a cena utilizando o "algoritmo do pintor" (painter's algorithm)
# para determinar a visibilidade dos triângulos (qual deve estar por cima do outro)
#
# Crie uma cena com dois cubos de forma que o algoritmo do pintor falhe de forma
# visualmente perceptível.

if __name__ == "__main__":
    urenderer.utils.clear_workdir("04-intersection")
    renderer = urenderer.renderer.PyplotRenderer(1920, 1080)
    runtime = urenderer.application.Runtime(renderer, name="04-intersection")

    # Crie a cena
    # Criar geometria do cubo
    cube_data = urenderer.geometry.polygonal_ifs.get_ifs_cube()

    if isinstance(cube_data, tuple):
        cube_data = {"geometry_vertex": cube_data[0], "geometry_index": cube_data[1]}

    vertices = cube_data["geometry_vertex"]
    faces = cube_data["geometry_index"]
    
    # CUBO 1: Vermelho, posicionado no centro
    cube1 = urenderer.node.Node("cube_red")
    cube1.render_data['vertices'] = vertices.copy()
    cube1.render_data['faces'] = faces
    cube1.render_data['color'] = 'red'
    cube1.render_data['alpha'] = 0.7
    cube1.render_data['geometry_vertex'] = vertices.copy()
    cube1.render_data['geometry_index'] = faces
    
    cube1.translation = np.array([0, 0, 0])
    cube1.scale = np.array([1.0, 1.0, 1.0])
    
    # CUBO 2: Azul, intersectando o cubo vermelho
    cube2 = urenderer.node.Node("cube_blue")
    cube2.render_data['vertices'] = vertices.copy()
    cube2.render_data['faces'] = faces
    cube2.render_data['color'] = 'blue'
    cube2.render_data['alpha'] = 0.7
    cube2.render_data['geometry_vertex'] = vertices.copy()
    cube2.render_data['geometry_index'] = faces
    
    cube2.translation = np.array([0.6, 0.6, 0.6])  # Deslocado diagonalmente
    cube2.scale = np.array([1.0, 1.0, 1.0])
    
    # Adicionar cubos à cena
    runtime.scene.add_child(cube1)
    runtime.scene.add_child(cube2)
    
    # Adicionar um terceiro cubo para tornar a falha mais perceptível
    cube3 = urenderer.node.Node("cube_green")
    cube3.render_data['vertices'] = vertices.copy()
    cube3.render_data['faces'] = faces
    cube3.render_data['color'] = 'green'
    cube3.render_data['alpha'] = 0.7
    cube3.render_data['geometry_vertex'] = vertices.copy()
    cube3.render_data['geometry_index'] = faces
    
    cube3.translation = np.array([-0.6, -0.4, 0.5])
    cube3.scale = np.array([0.8, 0.8, 0.8])
    
    runtime.scene.add_child(cube3)
    
    # Configurar a câmera para uma boa visualização da intersecção
    runtime.camera.translation = np.array([3, 2, 4])
    runtime.camera.rotation = np.array([-25, 35, 0])
    runtime.camera.near_plane = 0.1
    runtime.camera.far_plane = 10.0
    runtime.camera.vertical_fov = 60.0
    
    print("=== Cena com intersecção de cubos ===")
    print("Cubo vermelho: centro na origem (0,0,0)")
    print("Cubo azul: centro em (0.6, 0.6, 0.6)")
    print("Cubo verde: centro em (-0.6, -0.4, 0.5)")
    print("\nOs cubos se intersectam!")
    print("O algoritmo do pintor não consegue determinar a ordem correta")
    print("Resultado: partes que deveriam estar atrás aparecem na frente\n")
    
    # Renderizar a cena
    runtime.iter(capture=True)
    
    print("Renderização concluída!")
    print("Observe na imagem como a sobreposição dos cubos está incorreta.")
    print("Partes do cubo azul que deveriam estar atrás do cubo vermelho")
    print("podem aparecer na frente, ou vice-versa.")