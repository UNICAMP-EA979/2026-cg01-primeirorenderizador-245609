import matplotlib.pyplot as plt
import numpy as np
from urenderer.node import Camera, Node
from urenderer.utils import get_filename_unique
from urenderer.renderer.renderer import Renderer

class PyplotRenderer(Renderer):
    '''
    Simple renderer using PyPlot.
    '''

    def __init__(self, screen_width: float, screen_height: float, show: bool = True) -> None:
        super().__init__(screen_width, screen_height)
        self.show = show

    def start(self, camera: Camera, view_matrix: np.ndarray, name: str = ""):
        self._fig = plt.figure()
        plt.title(name)
        self._name = name

        self._camera = camera
        self._view_matrix = view_matrix
        self._projection_matrix = camera.projection_matrix

        self._triangles = []
        self._depth = []

    def validate(self, node: Node) -> bool:
        return "geometry_index" in node.render_data and "geometry_vertex" in node.render_data

    def _stage_vertex_shading(self, triangle: np.ndarray,
                              model_transformation: np.ndarray) -> np.ndarray:
        # Calcula a Matriz MVP (Model-View-Projection)
        MVP = self._projection_matrix @ self._view_matrix @ model_transformation
        triangle_proj = (MVP @ triangle.T).T
        return triangle_proj

    def _stage_clipping(self, triangle: np.ndarray) -> tuple[bool, np.ndarray]:
        # Separa as coordenadas xyz e w
        xyz = triangle[:, 0:3]
        w = triangle[:, 3:4]
        
        # Verificar se o triângulo está completamente fora do frustum
        outside = np.any(xyz < -w, axis=1) | np.any(xyz > w, axis=1)
        
        if np.all(outside):
            return True, triangle
        
        if not np.any(outside):
            # Normalizar para NDC
            triangle_ndc = np.zeros_like(triangle)
            triangle_ndc[:, 0:3] = xyz / w
            triangle_ndc[:, 3] = 1.0
            return False, triangle_ndc
        
        # Parcialmente visível - descartar
        return True, triangle

    def _stage_screen_mapping(self, triangle: np.ndarray) -> np.ndarray:
        # Criar uma cópia
        triangle_mapped = triangle.copy()
        
        # Mapeia X e Y de [-1, 1] para coordenadas de tela
        triangle_mapped[:, 0] = (triangle[:, 0] + 1.0) * (self.screen_width / 2.0)
        triangle_mapped[:, 1] = (triangle[:, 1] + 1.0) * (self.screen_height / 2.0)
        
        # Z e W permanecem inalterados
        return triangle_mapped

    def render_valid_node(self, node: Node, model_transformation: np.ndarray):
        geometry_index = node.render_data["geometry_index"]
        geometry_vertex = node.render_data["geometry_vertex"]

        for triangle_index in geometry_index:
            # Converter para coordenadas homogêneas
            triangle = geometry_vertex[triangle_index]
            triangle = np.hstack([triangle, np.ones((3, 1))])

            # Vertex shading
            triangle_proj = self._stage_vertex_shading(triangle, model_transformation)

            # Clipping
            clip, triangle_ndc = self._stage_clipping(triangle_proj)
            if clip:
                continue

            # Screen Mapping
            triangle_screen = self._stage_screen_mapping(triangle_ndc)

            # Buffer
            self._triangles.append(triangle_screen[:, :2])
            self._depth.append(np.mean(triangle_ndc[:, 2]))

    def end(self, capture: bool = False):
        indexes = np.argsort(np.array(self._depth))
        indexes = np.flip(indexes)
        for z, index in enumerate(indexes):
            triangle = self._triangles[index]
            plt.fill(triangle[:, 0], triangle[:, 1],
                     color=np.random.rand(3), zorder=z)

        plt.xlim([0, self.screen_width])
        plt.ylim([0, self.screen_height])

        if capture:
            filename = get_filename_unique(self._name)
            self._fig.savefig(filename, facecolor="white",
                              transparent=False,  bbox_inches="tight")

        if self.show:
            plt.show()
        plt.close(self._fig)