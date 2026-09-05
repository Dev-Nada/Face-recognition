import cv2
import numpy as np
from insightface.app import FaceAnalysis
from insightface.utils import face_align

model_path = "face_detection_yunet_2023mar.onnx"

detect_face = cv2.FaceDetectorYN.create(
    model_path, "", (320, 320), 0.7, 0.3, 1000
)

app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])

app.prepare(ctx_id=-1, det_size=(640, 640))

reco_model = app.models["recognition"]


def detect_and_crop_face(image):
    h, w = image.shape[:2]
    detect_face.setInputSize((w, h))

    _, faces = detect_face.detect(image)

    if faces is None:
        raise ValueError("No face detected.")
    if len(faces) > 1:
        raise ValueError(
            "Multiple faces detected. Please provide an image with exactly one face."
        )

    confidence = float(faces[0][-1])
    if confidence < 0.7:
        raise ValueError("Face detection confidence is too low.")

    face_data = faces[0]
    x, y, face_w, face_h = face_data[:4]
    x, y, face_w, face_h = int(x), int(y), int(face_w), int(face_h)

    padding_x = 0.15
    padding_y = 0.15
    x1 = max(0, int(x - face_w * padding_x))
    y1 = max(0, int(y - face_h * padding_y))
    x2 = min(w, int(x + face_w * (1 + padding_x)))
    y2 = min(h, int(y + face_h * (1 + padding_y)))

    face_crop = image[y1:y2, x1:x2]
    box = (x1, y1, x2, y2)
    return face_crop, face_data, box, confidence


def get_face_embedding(image):
    face_crop, face_data, box, confidence = detect_and_crop_face(image)
    landmarks = face_data[4:14].reshape(5, 2)
    aligned_face = face_align.norm_crop(image, landmarks)
    embedding = reco_model.get_feat(aligned_face)

    embedding = embedding.flatten()
    embedding = embedding / np.linalg.norm(embedding)
    return embedding


def compare_faces(embedding1, embedding2, threshold=0.5):

    similarity = float(np.dot(embedding1, embedding2))
    is_match = similarity >= threshold
    return similarity, is_match