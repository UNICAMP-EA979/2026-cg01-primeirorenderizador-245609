import abc
import time
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from urenderer.node import Camera, Node


class Renderer(abc.ABC):
    '''
    Abstract class for renderers.

    It receives the elements of the scene and renders them.
    '''

    def __init__(self, screen_width: float, screen_height: float) -> None:
        '''
        Renderer initializer

        Args:
            screen_width (float): screen width
            screen_height (float): screen height
        '''
        super().__init__()
        self.fig = None
        self.ax = None
        self.camera = None
        self.view_matrix = None

        self.screen_width = screen_width
        self.screen_height = screen_height

    @abc.abstractmethod
    def start(self, camera: Camera, view_matrix: np.ndarray, name: str) -> None:
        '''
        Start the frame rendering

        Args:
            camera (Camera): current camera.
            view_matrix (np.ndarray): camera view matrix.
            name (str): name of the application
        '''
        self.camera = camera
        self.view_matrix = view_matrix
        
        # Create figure and 3D axes
        self.fig = plt.figure(figsize=(self.screen_width/100, self.screen_height/100))
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.ax.set_title(name)
        
        # Set axis labels
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')
        
        # Set initial view based on camera
        self._apply_camera_view()

    @abc.abstractmethod
    def validate(self, node: Node) -> bool:
        '''
        Validate a node for rendering.

        Check if the node is compatible to be rendered with this renderer.

        Args:
            node (Node): node to validate.

        Returns:
            bool: True if the node is valid
        '''
        has_vertices = 'vertices' in node.render_data
        has_faces = 'faces' in node.render_data
        
        return has_vertices and has_faces

    def render(self, node: Node, model_transformation: np.ndarray) -> None:
        '''
        Render a node, if valid

        Args:
            node (Node): node to render
            model_transformation (np.ndarray): node model transformation in the scene
        '''
        if self.validate(node):
            self.render_valid_node(node, model_transformation)

    @abc.abstractmethod
    def render_valid_node(self, node: Node, model_transformation: np.ndarray) -> None:
        '''
        Renders a validated node

        Args:
            node (Node): node to render
            model_transformation (np.ndarray): node model transformation in the scene
        '''
        # 1. Obter os vértices do nó em coordenadas locais (object space)
        vertices_local = node.render_data['vertices']  # Formato: N x 3
        faces = node.render_data.get('faces', [])
        
        if len(vertices_local) == 0:
            return
        
        # Converter para coordenadas homogêneas (adicionar w=1)
        vertices_homogeneous = np.hstack([
            vertices_local, 
            np.ones((len(vertices_local), 1))
        ])
        
        # 2. ESTÁGIO 1: Transformação de Modelo (Object Space -> World Space)
        vertices_world_homogeneous = (model_transformation @ vertices_homogeneous.T).T
        
        # 3. ESTÁGIO 2: Transformação de Vista (World Space -> View Space)
        vertices_view_homogeneous = (self.view_matrix @ vertices_world_homogeneous.T).T
        
        # 4. ESTÁGIO 3: Transformação de Projeção (View Space -> Clip Space)
        projection_matrix = self.camera.projection_matrix
        vertices_clip_homogeneous = (projection_matrix @ vertices_view_homogeneous.T).T
        
        # 5. Divisão Perspectiva (Clip Space -> NDC - Normalized Device Coordinates)
        w_coords = vertices_clip_homogeneous[:, 3:4]
        w_coords = np.where(np.abs(w_coords) < 1e-6, 1e-6, w_coords)  # Evitar divisão por zero
        vertices_ndc = vertices_clip_homogeneous[:, :3] / w_coords
        
        # 6. ESTÁGIO 4: Transformação de Viewport (NDC -> Screen Coordinates)
        screen_vertices = np.zeros_like(vertices_ndc)
        screen_vertices[:, 0] = (vertices_ndc[:, 0] + 1.0) * 0.5 * self.screen_width
        screen_vertices[:, 1] = (vertices_ndc[:, 1] + 1.0) * 0.5 * self.screen_height
        screen_vertices[:, 2] = (vertices_ndc[:, 2] + 1.0) * 0.5  # Profundidade normalizada [0,1]
        
        # 7. Culling: Remover vértices fora do frustum (fora do range NDC [-1, 1])
        valid_mask = (np.abs(vertices_ndc[:, 0]) <= 1.0) & \
                    (np.abs(vertices_ndc[:, 1]) <= 1.0) & \
                    (np.abs(vertices_ndc[:, 2]) <= 1.0)
        
        if not np.any(valid_mask):
            return
        
        # 8. Renderizar as faces usando matplotlib
        node_color = node.render_data.get('color', 'blue')
        alpha = node.render_data.get('alpha', 0.5)
        
        for face in faces:
            # Pegar vértices desta face
            face_vertices = screen_vertices[face]
            
            # Verificar se todos os vértices da face são válidos
            face_valid = np.all([valid_mask[idx] for idx in face if idx < len(valid_mask)])
            
            if not face_valid:
                continue
            
            # Extrair coordenadas x, y, z
            x_coords = face_vertices[:, 0]
            y_coords = face_vertices[:, 1]
            z_coords = face_vertices[:, 2]
            
            # Fechar o polígono (repetir primeiro ponto)
            x_coords_closed = np.append(x_coords, x_coords[0])
            y_coords_closed = np.append(y_coords, y_coords[0])
            z_coords_closed = np.append(z_coords, z_coords[0])
            
            # Desenhar a face como um polígono 3D
            self.ax.plot_trisurf(x_coords_closed, y_coords_closed, z_coords_closed, 
                            color=node_color, alpha=alpha, shade=True)
    def _apply_camera_view(self) -> None:
        '''
        Apply camera view settings to matplotlib 3D axes
        '''
        if self.ax is None or self.camera is None:
            return
        
        # Extract camera position from view matrix
        # View matrix transforms world to camera space
        # The inverse gives camera position in world space
        camera_position = self._extract_camera_position()
        
        # Set view limits based on camera frustum
        far_plane = self.camera.far_plane
        self.ax.set_xlim3d([-far_plane, far_plane])
        self.ax.set_ylim3d([-far_plane, far_plane])
        self.ax.set_zlim3d([-far_plane, far_plane])
        
        # Set view angles based on camera orientation
        # For a perspective camera, we can approximate by setting elevation and azimuth
        # This is a simplification - real camera orientation would need extracting from view matrix
        elevation = 30  # degrees
        azimuth = 45    # degrees
        
        # Try to extract orientation from view matrix if available
        if self.view_matrix is not None:
            # Extract rotation part from view matrix
            R = self.view_matrix[:3, :3]
            # Convert to Euler angles (simplified)
            azimuth = np.degrees(np.arctan2(R[1, 0], R[0, 0]))
            elevation = np.degrees(np.arcsin(-R[2, 0]))
        
        self.ax.view_init(elev=elevation, azim=azimuth)
    
    def _extract_camera_position(self) -> np.ndarray:
        '''
        Extract camera position from view matrix
        
        Returns:
            np.ndarray: Camera position in world coordinates
        '''
        if self.view_matrix is None:
            return np.array([0, 0, 5])
        
        # For a view matrix V = [R|t], the camera position in world coordinates is -R^T * t
        R = self.view_matrix[:3, :3]
        t = self.view_matrix[:3, 3]
        
        camera_position = -R.T @ t
        return camera_position

    @abc.abstractmethod
    def end(self, capture: bool = False) -> None:
        '''
        Ends the frame rendering

        Args:
            capture (bool, optional): if should save the current frame. Defaults to False.
        '''
        if self.ax is not None:
            # Render the plot
            plt.tight_layout()
            
            if capture:
                # Save the current frame
                filename = f"frame_{time.time()}.png"
                plt.savefig(filename, dpi=100)
                print(f"Saved frame to {filename}")
            
            # Display or close
            plt.draw()
            plt.pause(0.001)  # Small pause to update display
            
            # Clear for next frame
            self.ax.clear()
            self._apply_camera_view()