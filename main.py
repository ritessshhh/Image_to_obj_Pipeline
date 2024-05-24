import os
import math
import numpy as np
from PIL import Image

class ImageToObjPipeline:
    def __init__(self, img, objPath='model.obj', mtlPath='model.mtl', matName='colored', useMaterial=False):
        self.img = img
        self.objPath = objPath
        self.mtlPath = mtlPath
        self.matName = matName
        self.useMaterial = useMaterial
        self.w = img.shape[1]
        self.h = img.shape[0]
        self.FOV = math.pi / 4
        self.D = (self.h / 2) / math.tan(self.FOV / 2)

    def vete(self, v, vt):
        if v == vt:
            return str(v)
        return str(v) + "/" + str(vt)

    def prepare_directories(self):
        if max(self.objPath.find('\\'), self.objPath.find('/')) > -1:
            os.makedirs(os.path.dirname(self.mtlPath), exist_ok=True)

    def write_header(self, f):
        if self.useMaterial:
            f.write("mtllib " + self.mtlPath + "\n")
            f.write("usemtl " + self.matName + "\n")

    def generate_vertices(self, f):
        ids = np.zeros((self.w, self.h), int)
        vid = 1

        for u in range(0, self.w):
            for v in range(self.h - 1, -1, -1):
                d = self.img[v, u]
                ids[u, v] = vid if d != 0.0 else 0
                vid += 1

                x = u - self.w / 2
                y = v - self.h / 2
                z = -self.D

                norm = 1 / math.sqrt(x * x + y * y + z * z)
                t = d / (z * norm)

                x = -t * x * norm
                y = t * y * norm
                z = -t * z * norm

                f.write(f"v {x} {y} {z}\n")
        return ids

    def generate_texture_coordinates(self, f):
        for u in range(0, self.w):
            for v in range(0, self.h):
                f.write(f"vt {u / self.w} {v / self.h}\n")

    def generate_faces(self, f, ids):
        for u in range(0, self.w - 1):
            for v in range(0, self.h - 1):
                v1 = ids[u, v]
                v3 = ids[u + 1, v]
                v2 = ids[u, v + 1]
                v4 = ids[u + 1, v + 1]

                if v1 == 0 or v2 == 0 or v3 == 0 or v4 == 0:
                    continue

                f.write(f"f {self.vete(v1, v1)} {self.vete(v2, v2)} {self.vete(v3, v3)}\n")
                f.write(f"f {self.vete(v3, v3)} {self.vete(v2, v2)} {self.vete(v4, v4)}\n")

    def create_obj(self):
        self.prepare_directories()
        with open(self.objPath, "w") as f:
            self.write_header(f)
            ids = self.generate_vertices(f)
            self.generate_texture_coordinates(f)
            self.generate_faces(f, ids)

# def main():
#     # Load an image using PIL
#     input_image_path = 'image1.png'  # Replace with the path to your image
#     img = Image.open(input_image_path).convert('L')  # Convert image to grayscale

#     # Convert the image to a NumPy array
#     img_array = np.array(img)

#     # Initialize the pipeline with the image data
#     pipeline = ImageToObjPipeline(img_array)

#     # Create the OBJ file
#     pipeline.create_obj()

# if __name__ == "__main__":
#     main()
