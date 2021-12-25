from flask import Flask, render_template, sessions, url_for, Response, session
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from msrest.authentication import ApiKeyCredentials
from numpy.core.records import record
import pyautogui
import numpy as np
import requests
import json
from camera import VideoCamera

url = "https://asllang.cognitiveservices.azure.com/language/:query-knowledgebases?projectName=AzureASL&api-version=2021-10-01&deploymentName=production"
headers={'Ocp-Apim-Subscription-Key': '4226713283bd4af1bbb06c34d70388dc', "Content-Type":"application/json"}
question = ''
app = Flask(__name__)
start_recording = False

def chatbot():
    global start_recording

    while start_recording:
        question = input("")
        data="{'question': '"+question+"'}"

        if question == "exit": break

        if question != '':
            res = requests.post(url=url, data=data, headers=headers)
            res = json.loads(res.text)

            print(res['answers'][0]['answer'])
    
    return "Exit"



def generate_frames(camera):
    while True:
        data =camera.get_frame()
        frame = data[0]
        yield(b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def main():
    try:
        # image = pyautogui.screenshot()
        # image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        # cv2.imwrite("static/test-images/image3.jpg", image)
    
        pass

    except Exception as ex:
        print(ex)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chatbotOn")
def chatbotOn():
    global start_recording
    start_recording = True
    chatbot()
    return "Exit"

@app.route("/chatbotOff")
def chatbotOff():
    global start_recording
    start_recording = False
    return "Exit"

@app.route("/video")
def video():
    return Response(generate_frames(VideoCamera()), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(host="0.0.0.0")