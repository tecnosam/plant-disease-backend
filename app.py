import io

import numpy as np

from fastapi import (
    FastAPI,
    UploadFile
)

from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel, Field

from PIL import Image

from controllers import (
    login,
    signup,
    get_results,
    register_results
)

unit_size = 224


class LoginForm(BaseModel):

    email: str
    password: str


class SignupForm(BaseModel):

    name: str
    email: str
    password: str


class Patient(BaseModel):

    name: str
    gender: str
    email: str
    notes: str

    result: str = Field(default="Pending...")


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)


@app.post("/login")
async def login_route(data: LoginForm) -> bool:

    data = data.model_dump()
    return login(**data)


@app.post("/signup")
async def signup_route(data: SignupForm) -> bool:

    data = data.model_dump()
    return signup(**data)


@app.get("/results")
async def get_results_route():

    return get_results()


@app.post("/results")
async def register_results_route(data: Patient):

    data = data.model_dump()
    return register_results(data)


@app.post("/predict")
async def predict_route(file: UploadFile):

    content = await file.read()

    print(len(content))
    image = Image.open(
        io.BytesIO(content)
    ).resize((unit_size, unit_size))

    image = np.array(image) / 255

    # predictions = model.predict([image])
    # prediction = np.argmax(predictions, axis=-1)[0]
    # return labels[prediction]
    return 'No Tumor'
