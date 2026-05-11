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
        '''
        PyplotRenderer initializer.

        Args:
            screen_width (float): screen width
            screen_height (float): screen height
            show (bool, optional): if should show the rendered frame. Defaults to True.
        '''
        super().__init__(screen_width, screen_height)
        self.show = show

    def start(self, camera: Camera, view_matrix: np.ndarray, name: str = ""):
        '''
        Start the frame rendering

        Args:
            camera (Camera): current camera.
            view_matrix (np.ndarray): camera view matrix.
            name (str): name of the application
        '''
        self._fig = plt.figure()
        plt.title(name)
        self._name = name

        self._camera = camera
        self._view_matrix = view_matrix
        self._projection_matrix = camera.projection_matrix

        self._triangles = []
        self._depth = []

    def validate(self, node: Node) -> bool:
        '''
        Validate a node for rendering.

        Check if the node is compatible to be rendered with this renderer.

        Args:
            node (Node): node to validate.

        Returns:
            bool: True if the node is valid
        '''
        return "geometry_index" in node.render_data and "geometry_vertex" in node.render_data

    def _stage_vertex_shading(self, triangle: np.ndarray,
                              model_transformation: np.ndarray) -> np.ndarray:
        '''
        Geometry vertex shading stage.

        Projects the triangle to the view volume.

        Args:
            triangle (np.ndarray): triangle to process (3x4)
            model_transformation (np.ndarray): triangle transformation (4x4)

        Returns:
            np.ndarray: the projected triangle
        '''
        ## SEU CÓDIGO AQUI #####################################################
        # Projete o triângulo, combinando a matriz de transformação do modelo,
        #  view matriz (self._view_matrix) e a matriz de projeção (self._projection_matrix)
        # Calcula a Matriz MVP (Model-View-Projection)
        MVP = self._projection_matrix @ self._view_matrix @ model_transformation
        triangle_proj = (MVP @ triangle.T).T

    
        #########################################################################

        return triangle_proj

    def _stage_clipping(self, triangle: np.ndarray) -> tuple[bool, np.ndarray]:
        '''
        Geometry clipping stage.

        It checks if the triangle is visible and normalizes it. If it's not visible, it doesn't process the triangle.

        Although not accurate, it also discards partially visible triangles.

        Args:
            triangle (np.ndarray): triangle to clip (3x4)

        Returns:
            tuple[bool, np.ndarray]: if the triangle was clipped, and the triangle normalized if it was not.
        '''

    ## SEU CÓDIGO AQUI #####################################################
        
        # Separa as coordenadas xyz (3x3) e a coluna w (3x1) para facilitar
        xyz = triangle[:, 0:3]
        w = triangle[:, 3:4] # Mantém o formato de coluna
        
        # Checa se algum x, y ou z é menor que -w ou maior que w
        clip = np.any(xyz < -w) or np.any(xyz > w)

        if not clip:
            # Normalize o triângulo, dividindo cada coordenada pelo seu respectivo v_w
            # Isso transforma as coordenadas para NDC (Normalized Device Coordinates)
            triangle_ndc = triangle / w
            return clip, triangle_ndc

        return clip, triangle
        #########################################################################

    def _stage_screen_mapping(self, triangle: np.ndarray) -> np.ndarray:
        '''
        Geometry screen mapping stage.

        Maps the triangle from the normalized device coordinates [-1, 1]

        Args:
            triangle (np.ndarray): triangle to map

        Returns:
            np.ndarray: mapped triangle
        '''
## SEU CÓDIGO AQUI #####################################################
        
        # Mapeia o eixo X de [-1, 1] para [0, screen_width]
        triangle[:, 0] = (triangle[:, 0] + 1.0) * (self.screen_width / 2.0)
        
        # Mapeia o eixo Y de [-1, 1] para [0, screen_height]
        triangle[:, 1] = (triangle[:, 1] + 1.0) * (self.screen_height / 2.0)

        #########################################################################

        return triangle

    def render_valid_node(self, node: Node, model_transformation: np.ndarray):
        '''
        Renders a validated node

        Args:
            node (Node): node to render
            model_transformation (np.ndarray): node model transformation in the scene
        '''

        # Get the node geometry data
        geometry_index = node.render_data["geometry_index"]
        geometry_vertex = node.render_data["geometry_vertex"]

        # Processes each triangle of the node
        for triangle_index in geometry_index:
            # Convert to homogeneous coordinates.
            triangle = geometry_vertex[triangle_index]
            triangle = np.hstack([triangle, np.ones((3, 1))])

            # Vertex shading
            triangle_proj = self._stage_vertex_shading(
                triangle, model_transformation)

            # Clipping
            clip, triangle_ndc = self._stage_clipping(triangle_proj)
            if clip:
                continue

            # Screen Mapping
            triangle_screen = self._stage_screen_mapping(triangle_ndc)

            # Buffer the triangle
            self._triangles.append(triangle_screen[:, :2])
            self._depth.append(np.mean(triangle_ndc[:, 2]))

    def end(self, capture: bool = False):
        '''
        Ends the frame rendering

        Args:
            capture (bool, optional): if should save the current frame. Defaults to False.
        '''

        # Draw the triangles using painter's algorithm
        indexes = np.argsort(np.array(self._depth))
        indexes = np.flip(indexes)
        for z, index in enumerate(indexes):
            triangle = self._triangles[index]

            # The 'zorder' sorts the triangles in the screen
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
