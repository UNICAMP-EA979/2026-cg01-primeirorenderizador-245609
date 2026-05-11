import matplotlib.pyplot as plt
import numpy as np
from urenderer.node import Camera, Node
from urenderer.utils import get_filename_unique
from urenderer.renderer.renderer import Renderer

class PyplotRenderer(Renderer):
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
        MVP = self._projection_matrix @ self._view_matrix @ model_transformation
        triangle_proj = (MVP @ triangle.T).T
        return triangle_proj

    def _stage_clipping(self, triangle: np.ndarray) -> tuple[bool, np.ndarray]:
        # Verificar se o triângulo está completamente fora do frustum
        xyz = triangle[:, 0:3]
        w = triangle[:, 3:4]
        
        # Verificar se cada vértice está dentro do frustum
        inside = np.all((xyz >= -w) & (xyz <= w), axis=1)
        
        if np.all(~inside):
            # Todos os vértices estão fora
            return True, triangle
        
        if np.all(inside):
            # Todos os vértices estão dentro - normalizar para NDC
            triangle_ndc = np.column_stack([
                triangle[:, 0] / triangle[:, 3],
                triangle[:, 1] / triangle[:, 3],
                triangle[:, 2] / triangle[:, 3],
                np.ones(3)
            ])
            return False, triangle_ndc
        
        # Parcialmente visível - descartar
        return True, triangle

    def _stage_screen_mapping(self, triangle: np.ndarray) -> np.ndarray:
        triangle_mapped = triangle.copy()
        triangle_mapped[:, 0] = (triangle[:, 0] + 1.0) * (self.screen_width / 2.0)
        triangle_mapped[:, 1] = (triangle[:, 1] + 1.0) * (self.screen_height / 2.0)
        return triangle_mapped

    def render_valid_node(self, node: Node, model_transformation: np.ndarray):
        geometry_index = node.render_data["geometry_index"]
        geometry_vertex = node.render_data["geometry_vertex"]

        for triangle_index in geometry_index:
            triangle = geometry_vertex[triangle_index]
            triangle = np.hstack([triangle, np.ones((3, 1))])

            triangle_proj = self._stage_vertex_shading(triangle, model_transformation)
            clip, triangle_ndc = self._stage_clipping(triangle_proj)
            
            if clip:
                continue

            triangle_screen = self._stage_screen_mapping(triangle_ndc)
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
                              transparent=False, bbox_inches="tight")

        if self.show:
            plt.show()
        plt.close(self._fig)