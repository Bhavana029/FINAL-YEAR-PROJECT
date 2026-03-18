import cv2
import numpy as np
import urllib.request

def preprocess_image(image_path):

    # 🔥 If it's a URL (Cloudinary)
    if image_path.startswith("http"):
        resp = urllib.request.urlopen(image_path)
        image = np.asarray(bytearray(resp.read()), dtype="uint8")
        img = cv2.imdecode(image, cv2.IMREAD_COLOR)
    else:
        img = cv2.imread(image_path)

    # Continue your preprocessing
    img = cv2.resize(img, (224, 224))

    return img