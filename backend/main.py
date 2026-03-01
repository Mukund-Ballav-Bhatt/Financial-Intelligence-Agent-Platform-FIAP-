from fastapi import FastAPI
import json
from pydantic import BaseModel

app=FastAPI()


class Patient(BaseModel):
    id:int
    name:str
    age:int
    gender:str
    disease:str
    admitted:bool


def load_data():
    with open('patients.json','r') as f:
        data=json.load(f)
    return data    

@app.get("/")
def hello():
    return {'message':'I hate'}

@app.get('/about')
def about():
    return {'message':'I love MBB'}

@app.get('/view')
def view():
    data= load_data()
    return data

@app.get('/patient/id')
def view_patient(id: int):
    data= load_data()

    if id in data:
        return data[id]
    return {'error':'patient not found'}