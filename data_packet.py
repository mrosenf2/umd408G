class data_packet:
    def __init__(self, frame_number, num_faces, locations_tl, locations_br, names):
        self.face_count = num_faces
        self.locations_tl = locations_tl
        self.locations_br = locations_br
        self.names = names
        self.frame_number = frame_number
