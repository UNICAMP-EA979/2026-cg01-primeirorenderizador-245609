import matplotlib.pyplot as plt
import numpy as np
from urenderer.node import Camera, Node
from urenderer.renderer.renderer import Renderer


class PyplotRenderer(Renderer):
    def __init__(self, screen_width: float, screen_height: float, show_plot: bool = True) -> None:
        super().__init__(screen_width, screen_height)
        self.fig = None
        self.ax = None
        self.camera = None
        self.view_matrix = None
        self.show_plot = show_plot
        
    def start(self, camera: Camera, view_matrix: np.ndarray, name: str) -> None:
        """Start the frame rendering"""
        self.camera = camera
        self.view_matrix = view_matrix
        
        if self.show_plot:
            self.fig = plt.figure(figsize=(self.screen_width/100, self.screen_height/100))
            self.ax = self.fig.add_subplot(111, projection='3d')
            self.ax.set_title(name)
            self.ax.set_xlabel('X')
            self.ax.set_ylabel('Y')
            self.ax.set_zlabel('Z')
    
    def validate(self, node: Node) -> bool:
        """Validate a node for rendering"""
        return 'vertices' in node.render_data and 'faces' in node.render_data
    
    def _stage_vertex_shading(self, triangle: np.ndarray, model_transformation: np.ndarray) -> np.ndarray:
        """
        Stage 1-3: Model, View, and Projection transformations
        Input: triangle in object space (4x3 or 3x4 matrix)
        Output: triangle in clip space (homogeneous coordinates)
        """
        # Ensure triangle is 3x4 (3 vertices, 4 coordinates)
        if triangle.shape == (4, 3):
            triangle = triangle.T
        
        # Add homogeneous coordinate if needed
        if triangle.shape[1] == 3:
            triangle = np.hstack([triangle, np.ones((3, 1))])
        
        # Model Transformation (object space -> world space)
        world_space = (model_transformation @ triangle.T).T
        
        # View Transformation (world space -> view space)
        view_space = (self.view_matrix @ world_space.T).T
        
        # Projection Transformation (view space -> clip space)
        projection_matrix = self.camera.projection_matrix
        clip_space = (projection_matrix @ view_space.T).T
        
        return clip_space
    
    def _stage_clipping(self, triangle: np.ndarray) -> tuple:
        """
        Stage 4: Clipping against view frustum
        Returns: (is_visible, clipped_triangle)
        """
        # Check if triangle is completely outside the clip space (-w <= x,y,z <= w)
        # For homogeneous coordinates, we check all vertices
        w = triangle[:, 3:4]
        valid = np.all(np.abs(triangle[:, :3]) <= w, axis=1)
        
        if np.all(valid):
            # Triangle fully inside
            return True, triangle
        elif np.any(valid):
            # Triangle partially inside - in a full implementation, we would clip
            # For this test, we'll return the triangle as-is
            return True, triangle
        else:
            # Triangle fully outside
            return False, triangle
    
    def _stage_screen_mapping(self, triangle: np.ndarray) -> np.ndarray:
        """
        Stage 5: Perspective division and viewport mapping
        Input: triangle in clip space (homogeneous coordinates)
        Output: triangle in screen space with depth
        """
        # Perspective division (clip space -> NDC)
        w = triangle[:, 3:4]
        w = np.where(np.abs(w) < 1e-6, 1e-6, w)
        ndc = triangle[:, :3] / w
        
        # Viewport mapping (NDC -> screen space)
        screen = np.zeros_like(triangle)
        screen[:, 0] = (ndc[:, 0] + 1.0) * 0.5 * self.screen_width
        screen[:, 1] = (ndc[:, 1] + 1.0) * 0.5 * self.screen_height
        screen[:, 2] = (ndc[:, 2] + 1.0) * 0.5  # depth
        screen[:, 3] = triangle[:, 3]  # keep w for potential use
        
        return screen
    
    def render_valid_node(self, node: Node, model_transformation: np.ndarray) -> None:
        """Renders a validated node using the pipeline stages"""
        vertices = node.render_data['vertices']
        faces = node.render_data.get('faces', [])
        
        if len(vertices) == 0:
            return
        
        # Convert vertices to homogeneous coordinates
        vertices_homogeneous = np.hstack([
            vertices,
            np.ones((len(vertices), 1))
        ])
        
        # Process each face through the pipeline
        node_color = node.render_data.get('color', 'blue')
        alpha = node.render_data.get('alpha', 0.5)
        
        for face in faces:
            # Get triangle vertices
            triangle = vertices_homogeneous[face]
            
            # Stage 1-3: Vertex shading (Model, View, Projection)
            triangle_clip = self._stage_vertex_shading(triangle, model_transformation)
            
            # Stage 4: Clipping
            is_visible, triangle_clipped = self._stage_clipping(triangle_clip)
            
            if not is_visible:
                continue
            
            # Stage 5: Screen mapping
            triangle_screen = self._stage_screen_mapping(triangle_clipped)
            
            # Render triangle
            if self.ax is not None and self.show_plot:
                # Extract screen coordinates
                x = triangle_screen[:, 0]
                y = triangle_screen[:, 1]
                z = triangle_screen[:, 2]
                
                # Close the polygon
                x = np.append(x, x[0])
                y = np.append(y, y[0])
                z = np.append(z, z[0])
                
                try:
                    self.ax.plot_trisurf(x, y, z, color=node_color, alpha=alpha, shade=True)
                except Exception as e:
                    print(f"Error rendering face: {e}")
    
    def end(self, capture: bool = False) -> None:
        """Ends the frame rendering"""
        if self.ax is not None and self.show_plot:
            plt.tight_layout()
            
            if capture:
                filename = f"frame.png"
                plt.savefig(filename, dpi=100)
                print(f"Saved frame to {filename}")
            
            plt.draw()
            plt.pause(0.001)
            
            # Clear for next frame
            self.ax.clear()