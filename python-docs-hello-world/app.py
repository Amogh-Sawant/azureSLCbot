from flask import Flask, render_template, url_for
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from msrest.authentication import ApiKeyCredentials
import os
import numpy as np
import cv2
import pyautogui
from threading import Thread
from PIL import Image

app = Flask(__name__)

pyimg = Image.open('static/test-images/image3.jpg')

@app.route("/")
def index():
    return render_template("index.html", pythonimg=pyimg.show())


def main():

    try:

        image = pyautogui.screenshot()
        image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        cv2.imwrite("static/test-images/image3.jpg", image)

        print("exceucted")

    except Exception as ex:
        print(ex)


if __name__ == "__main__":
    app.run(host="0.0.0.0")
    main()
    
    
import requests
import json

url = "https://asllang.cognitiveservices.azure.com/language/:query-knowledgebases?projectName=AzureASL&api-version=2021-10-01&deploymentName=production"

headers={'Ocp-Apim-Subscription-Key': 'keyxxx', "Content-Type":"application/json"}

question = ''

while question != "exit":
    question = input("")
    data="{'question': '"+question+"'}"

    if question != '':
        res = requests.post(url=url, data=data, headers=headers)
        res = json.loads(res.text)

        print(res['answers'][0]['answer'])
