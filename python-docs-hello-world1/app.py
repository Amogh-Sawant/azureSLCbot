from flask import Flask, render_template, sessions, url_for, Response, session
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from msrest.authentication import ApiKeyCredentials
import pyautogui
import numpy as np
import requests
import json
from camera import VideoCamera
from time import sleep
import cv2
import os

prediction_endpoint = "https://testvision326-prediction.cognitiveservices.azure.com"
prediction_key = "791857180c034b83ad76780d8e22626f"
project_id = "2b0b8510-b87b-4172-b1d6-d079127c2243"
model_name = "Iteration1"
url = "https://asllang.cognitiveservices.azure.com/language/:query-knowledgebases?projectName=AzureASL&api-version=2021-10-01&deploymentName=production"
headers={'Ocp-Apim-Subscription-Key': '4226713283bd4af1bbb06c34d70388dc', "Content-Type":"application/json"}
question = ''
onlyletters = "abcdefghijklmnopqrstuvwxyz"
start_recording = False

credentials = ApiKeyCredentials(in_headers={"Prediction-key": prediction_key})
prediction_client = CustomVisionPredictionClient(endpoint=prediction_endpoint, credentials=credentials)
app = Flask(__name__)

global reply 
reply = 1

def filterstring(string):
    string = string.lower()
    fil_str = ""
    for letter in string:
        if letter in onlyletters:
            fil_str = fil_str + letter

    return fil_str

def chatbot():
    global start_recording
    global reply

    while start_recording:
        if not start_recording:
            return "none"

        question = input("")
        data="{'question': '"+question+"'}"

        if question == "exit": break

        if question != '':
            res = requests.post(url=url, data=data, headers=headers)
            res = json.loads(res.text)

            reply = filterstring(res['answers'][0]['answer'])
            print(reply)
    
    return "Exit"

def testbot():
    global reply
    while True:
        reply = input("")

def generate_frames(camera):
    global reply
    while True:
        data = camera.get_frame()
        frame = data[0]

        yield(b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def generate_answer():
    global reply

    while True:
        n = reply
        image_data = open(os.path.join('static/test-images',f"IMG_TEST_{n}.jpg"), "rb").read()
        sleep(1)

        yield(b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + image_data + b'\r\n\r\n')

    
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chatbotOn")
def chatbotOn():
    global start_recording, reply
    start_recording = True
    pn = 0
    question = ""
    # chatbot()
    testbot()

    # while start_recording:
    #     image = pyautogui.screenshot()
    #     image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    #     cv2.imwrite(f"static/question/classifyimage{pn}.jpg", image)
    #     pn = pn + 1
    #     sleep(1)
    #     print ("im here")

    # if not start_recording:
        # for image in os.listdir('static/question'):
        #     image_data = open(os.path.join('static/question',image), "rb").read()
        #     results = prediction_client.classify_image(project_id, model_name, image_data)

        #     for prediction in results.predictions:
        #         if prediction.probability > 0.5:
        #             question = question + prediction.tag_name

        # if question != '':
        #     data="{'question': '" + question + "'}"
        #     res = requests.post(url=url, data=data, headers=headers)
        #     res = json.loads(res.text)

        #     reply = filterstring(res['answers'][0]['answer'])
        #     print(reply) # send this reply to html file without reloading the damn page
        
        # print("stopped")

        # return "Exit"

    return "Exit"

@app.route("/chatbotOff")
def chatbotOff():
    global start_recording
    start_recording = False

    return "none"

@app.route("/video")
def video():
    return Response(generate_frames(VideoCamera()), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/image")
def image():
    return Response(generate_answer(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(host="0.0.0.0")