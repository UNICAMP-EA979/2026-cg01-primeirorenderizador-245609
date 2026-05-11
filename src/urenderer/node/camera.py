import numpy as np

from .node import Node


class Camera(Node):
    '''
    Camera node, a perspective camera
    '''

    def __init__(self, name: str = "camera") -> None:
        '''
        Camera initilizer

        Args:
            name (str, optional): node name. Defaults to "camera".
        '''
        super().__init__(name)

        self.near_plane = 1.0
        self.far_plane = 10.0
        self.screen_width = 1920.0
        self.screen_height = 1080.0
        self.vertical_fov = 60.0

    @property
    def projection_matrix(self) -> np.ndarray:
        '''
        Camera projection matrix

        Returns:
            np.ndarray: 4x4 projection matrix
        '''

        ## SEU CÓDIGO AQUI #####################################################
        # Crie a matriz de projeção utilizando a fórmula
        matrix = np.zeros((4, 4))

        f = self.far_plane
        n = self.near_plane
        a = self.screen_width / self.screen_height
        fov_rad = np.radians(self.vertical_fov)
        c = 1.0 / np.tan(fov_rad / 2.0)

        # Preenchendo a matriz de projeção perspectiva
        matrix[0, 0] = c / a
        matrix[1, 1] = c
        matrix[2, 2] = -(f + n) / (f - n)
        matrix[2, 3] = -(2 * f * n) / (f - n)
        matrix[3, 2] = -1.0

        #########################################################################
        #########################################################################

        return matrix