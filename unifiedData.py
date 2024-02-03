
class InputData:
    def __init__(self, color_data,
                 depth_data,
                 width: int,
                 height: int, 
                 unit_dim: int,
                 frame_id: int):
        self.color_data = color_data
        self.depth_data = depth_data
        self.width = width
        self.height = height
        self.unit_dim = unit_dim
        self.frame_id = frame_id

class outputData:
    def __init__(self, data,
                 width: int,
                 height: int, 
                 frame_id: int,
                 ocr_text: str):
        self.data = data
        self.width = width
        self.height = height
        self.frame_id = frame_id
        self.text = ocr_text