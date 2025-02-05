from fastapi import FastAPI, UploadFile, File
from http import HTTPStatus
from enum import Enum
import re
from pydantic import BaseModel
from typing import Optional
import cv2
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from transformers import VisionEncoderDecoderModel, ViTFeatureExtractor, AutoTokenizer
import torch
from PIL import Image

# Create a FastAPI app
app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}

@app.get("/")
def root():
    """ Health check."""
    response = {
        "message": HTTPStatus.OK.phrase,
        "status-code": HTTPStatus.OK,
    }
    return response

class ItemEnum(Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

@app.get("/restric_items/{item_id}")
def read_item(item_id: ItemEnum):
    return {"item_id": item_id}

@app.get("/query_items")
def read_item(item_id: int):
    return {"item_id": item_id}

# reload and figure out how to pass in a query parameter
#  You can pass this query parameter in the URL like this: 
# /query_items?item_id=1&q=example

# Use POST requests for uploading data to the server
database = {'username': [ ], 'password': [ ]}

@app.post("/login/")
def login(username: str, password: str):
    username_db = database['username']
    password_db = database['password']
    if username not in username_db and password not in password_db:
        with open('database.csv', "a") as file:
            file.write(f"{username}, {password} \n")
        username_db.append(username)
        password_db.append(password)

    # Print the database state after updating
    print("Database after update:", database)

    return "login saved"


class EmailData(BaseModel):
    email: str
    domain: str

@app.get("/text_model/")
def contains_email(data: EmailData):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    response = {
        "input": data,
        "message": HTTPStatus.OK.phrase,
        "status-code": HTTPStatus.OK,
        "is_email": re.fullmatch(regex, data) is not None,
        "email": "mlops@gmail.com",
        "domain_match": "gmail"
    }
    
    return response

@app.post("/cv_model/")
async def cv_model(data: UploadFile = File("images/img.png")):
    with open('images/image.jpg', 'wb') as image:
        content = await data.read()
        image.write(content)
        image.close()

    response = {
        "input": data,
        "message": HTTPStatus.OK.phrase,
        "status-code": HTTPStatus.OK,
    }
    return response

h = 28
w = 28

img = cv2.imread("images/img.png")
res = cv2.resize(img, (h, w))

cv2.imwrite('images/image_resize.jpg', res)
FileResponse('images/image_resize.jpg')

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Hello")
    yield
    print("Goodbye")

app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return {"Hello": "World"}

model = VisionEncoderDecoderModel.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
feature_extractor = ViTFeatureExtractor.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
tokenizer = AutoTokenizer.from_pretrained("nlpconnect/vit-gpt2-image-captioning")

device = torch.device("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")
model.to(device)

gen_kwargs = {"max_length": 16, "num_beams": 8, "num_return_sequences": 1}
def predict_step(image_paths):
    images = []
    for image_path in image_paths:
        i_image = Image.open(image_path)
        if i_image.mode != "RGB":
            i_image = i_image.convert(mode="RGB")

        images.append(i_image)
    pixel_values = feature_extractor(images=images, return_tensors="pt").pixel_values
    pixel_values = pixel_values.to(device)
    output_ids = model.generate(pixel_values, **gen_kwargs)
    preds = tokenizer.batch_decode(output_ids, skip_special_tokens=True)
    preds = [pred.strip() for pred in preds]
    return preds

if __name__ == "__main__":
    print(predict_step(['images/my_cat.jpg']))