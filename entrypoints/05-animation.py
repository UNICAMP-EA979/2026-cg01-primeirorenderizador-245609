import numpy as np
import urenderer
from urenderer.node import Node

# Crie uma cena com animação
#
# Observe o método urenderer.application.runtime.Runtime::iter
# A iteração da aplicação consiste em 2 etapas:
#  - update: executa códigos da aplicação
#  - render: renderiza a cena
#
# O update funciona a partir de callbacks: cada nó pode possuir uma ou mais funções de callback
# que são executadas no update.
#
# Vamos utilizar o update para criar uma animação simples.
# Crie uma cena simples e utilize funções como a "animate_over_time" para animar objetos
#


def animate_over_time(node: Node, deltaTime: float, time_since_start: float) -> None:
    '''
    Anima um nó

    Args:
        node (Node): nó a ser animado
        deltaTime (float): tempo desde o último update
        time_since_start (float): tempo desde o começo da aplicação
    '''
    node.rotation[1] = 360*np.sin(time_since_start)


if __name__ == "__main__":
    urenderer.utils.clear_workdir("05-animation")
    renderer = urenderer.renderer.PyplotRenderer(1920, 1080, show=False)
    runtime = urenderer.application.Runtime(renderer, name="05-animation")

    node = urenderer.node.Node()
    node.callbacks.append(animate_over_time)

    # Crie a cena

    # Pegando a geometria do cubo e garantindo o formato correto (tupla ou dicionário)
    cube_data = urenderer.geometry.polygonal_ifs.get_ifs_cube()
    if isinstance(cube_data, tuple):
        cube_data = {"geometry_vertex": cube_data[0], "geometry_index": cube_data[1]}
        
    # Preenchendo os dados do nó
    node.render_data['vertices'] = cube_data["geometry_vertex"].copy()
    node.render_data['faces'] = cube_data["geometry_index"]
    node.render_data['color'] = 'magenta'
    node.render_data['alpha'] = 0.9
    node.render_data['geometry_vertex'] = cube_data["geometry_vertex"].copy()
    node.render_data['geometry_index'] = cube_data["geometry_index"]
    
    node.translation = np.array([0.0, 0.0, 0.0])
    node.scale = np.array([3.0, 3.0, 3.0])  # Escala boa para visualização
    
    # Adiciona o objeto animado na cena
    runtime.scene.add_child(node)
    
    # Configura a câmera para enxergar o cubo no centro
    runtime.camera.translation = np.array([6.0, 4.0, 8.0])
    runtime.camera.rotation = np.array([-20.0, 35.0, 0.0])
    runtime.camera.near_plane = 0.1
    runtime.camera.far_plane = 50.0
    runtime.camera.vertical_fov = 60.0

    runtime.loop(n=10, capture=True)

    urenderer.utils.image_to_video("05-animation")