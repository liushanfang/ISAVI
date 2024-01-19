
class InputData:
    def __init__(self, color_data,
                 depth_data,
                 width: int,
                 height: int, 
                 unit_dim: int):
        self.color_data = color_data
        self.depth_data = depth_data
        self.width = width
        self.height = height
        self.unit_dim = unit_dim