import torch
from facenet_pytorch import InceptionResnetV1
from torchvision import transforms
import json
import cv2
from PIL import Image
from yaml import load


def load_faceslist():
    embeds = torch.load('data/facelist.pth')

    with open('data/member.json', 'r') as f:
        names = json.load(f)

    with open('data/history.json', 'r') as f:
        history = json.load(f)

    return embeds, names, history


def extract_face(img, box):
    img = img[box[1]:box[3], box[0]:box[2]]
    face = cv2.resize(img, (160, 160), interpolation=cv2.INTER_AREA)
    face = Image.fromarray(face)
    return face


def trans(img):
    transform = transforms.Compose([
            transforms.Resize(size=(160, 160)),
            transforms.ToTensor()
        ])
    return transform(img)


embeddings, names, history_file = load_faceslist()

model = torch.hub.load('ultralytics/yolov5', 'custom', path='src/model/best.pt')
model.conf = 0.8

fe = InceptionResnetV1(
    classify=False,
    pretrained="vggface2"
).to('cuda:0')
fe.eval()