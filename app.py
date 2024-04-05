from hashlib import md5
import io
import os
from random import randint
from typing import Union
import numpy as np

from fastapi import (
    FastAPI,
    UploadFile,
    Query,
    Path,
    Response
)

from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel, Field

from PIL import Image

import tensorflow as tf

import tensorflow_hub as hub

from controllers import (
    login,
    signup,
    get_results,
    register_results,
    edit_profile
)

from recommendations import (
    cassava_disease_treatments,
    maize_disease_treatments
)

unit_size = 224


class LoginForm(BaseModel):

    email: str
    password: str


class SignupForm(BaseModel):

    name: str
    email: str
    password: str


class EditProfileForm(BaseModel):

    name: str = Field(default=None)
    email: str = Field(default=None)
    password: Union[str, None] = Field(default=None)


class Result(BaseModel):

    crop_type: str
    notes: str
    prediction: str = Field(default="Pending...")
    recommendation: str = Field(default="Pending...")
    ihash: Union[str, None] = Field(default=None)


class Feedback(BaseModel):

    name: str
    email: str
    feedback: str


IMAGE_PATH = './images'
try:
    os.mkdir(IMAGE_PATH)
except:
    print("Image Path created")

try:
    maize_model = tf.keras.models.load_model('maize-model.h5')
except:
    print("Maize Model not loaded... Using randomized function")
    maize_model = lambda x: randint(0, 3)

try:
    cassava_model = hub.KerasLayer('cassava')
except:
    print("Cassava model not loaded... Using randomized function")
    cassava_model = lambda x: randint(0, 5)


accepted_crops = {
    "MAIZE": (
        maize_model,
        150,
        [
            'Cercospora_leaf_spot Gray_leaf_spot',
            'Common_rust',
            'Northern_Leaf_Blight',
            'Healthy'
        ]),

    "CASSAVA": (
        cassava_model,
        224,
        [
            'cbb',
            'cbsd',
            'cgm',
            'cmd',
            'Healthy',
            'unknown'
        ]),
}


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)


@app.post("/login")
async def login_route(data: LoginForm) -> Union[dict, None]:

    data = data.model_dump()
    return login(**data)


@app.post("/signup")
async def signup_route(data: SignupForm) -> bool:

    data = data.model_dump()
    return signup(**data)


@app.put("/edit-profile")
async def edit_profile_route(
    data: EditProfileForm,
    email: str = Query()
) -> bool:

    data = data.model_dump(exclude_none=True)
    print("updates", data)
    return edit_profile(email, data)


@app.get(
    "/image/{ihash}",
    responses = {
        200: {
            "content": {"image/png": {}}
        }
    }
)
def get_image(ihash: str = Path()) -> Union[bytes, None]:

    try:
        path = os.path.join(IMAGE_PATH, ihash)
        with open(path, 'rb') as f:

            image = f.read()
            return Response(image, media_type="image/png")
    except FileNotFoundError:
        return None


@app.get("/get/{collection}")   
async def get_results_route(collection: str):

    return get_results(collection)


@app.post("/add/{collection}")
async def register_results_route(
    data: Union[Result, Feedback],
    collection: str
):

    data = data.model_dump()
    return register_results(data, collection)


@app.post("/predict")
async def predict_route(
    file: UploadFile,
    crop_type: str = Query()
):

    model, unit_size, labels = accepted_crops.get(crop_type.upper())

    content = await file.read()

    print(len(content))
    image = Image.open(
        io.BytesIO(content)
    ).resize((unit_size, unit_size))

    image = np.array(image) / 255

    image = np.expand_dims(image, axis=0)

    predictions = model(image)
    if isinstance(predictions, int):
        prediction = predictions
    else:
        prediction = np.argmax(predictions, axis=-1)[0]
    prediction = labels[prediction]

    if crop_type.upper() == 'MAIZE':
        recommendation = maize_disease_treatments.get(prediction)
    else:
        recommendation = cassava_disease_treatments.get(prediction)

    ihash = md5(content).hexdigest()
    path = os.path.join(IMAGE_PATH, ihash)

    with open(path, "wb") as f:
        f.write(content)

    return {
        'prediction': prediction,
        'recommendation': recommendation,
        'ihash': ihash
    }
