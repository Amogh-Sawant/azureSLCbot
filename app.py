from flask import Flask, render_template, url_for, Response, request
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from msrest.authentication import ApiKeyCredentials
import requests
import json
from camera import VideoCamera
from time import sleep, time
import os
import PIL.Image as Image
import io

prediction_endpoint = "https://aslvision-prediction.cognitiveservices.azure.com"
prediction_key = "76ce50d98d064322bb2fd555ff0f61f5"
project_id = "fb671e7c-3b34-4b0d-b180-f21bf629c550"
model_name = "Iteration1"
url = "https://asllang.cognitiveservices.azure.com/language/:query-knowledgebases?projectName=AzureASL&api-version=2021-10-01&deploymentName=production"
headers={'Ocp-Apim-Subscription-Key': '4226713283bd4af1bbb06c34d70388dc', "Content-Type":"application/json"}
onlyletters = "abcdefghijklmnopqrstuvwxyz"
start_recording = False

credentials = ApiKeyCredentials(in_headers={"Prediction-key": prediction_key})
prediction_client = CustomVisionPredictionClient(endpoint=prediction_endpoint, credentials=credentials)
app = Flask(__name__)

global reply, n, replyChange, question

reply = "welcome"
n = 0
replyChange = False
question = ""

def filterstring(string):
    string = string.lower()
    fil_str = ""
    for letter in string:
        if letter in onlyletters:
            fil_str = fil_str + letter

    return fil_str

def generate_frames(camera):
    global reply, start_recording
    t=0
    start_timer = True
    while True:
        data = camera.get_frame()
        frame = data[0]

        if start_recording:

            if start_timer:
                old_time = time()
                start_timer  = False

            if time() - old_time > 1:
                imj = Image.open(io.BytesIO(frame))
                imj.save(f'static/question/classifyimg{t}.jpg')
                print("ss done")
                start_timer = True
                t += 1
                if t==30:
                    start_recording = False

        yield(b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def generate_answer():
    global reply, n, replyChange
    retry = False

    while True:
        if replyChange:
            n = 0
            replyChange = False
            image_data = open(os.path.join('static/imgdatabase',"loading.jpg"), "rb").read()

        elif not retry and not replyChange:
            image_data = open(os.path.join('static/imgdatabase',f"{reply[n].upper()}.jpg"), "rb").read()
            n += 1

        else:
            image_data = open(os.path.join('static/imgdatabase',"blank.jpg"), "rb").read()
            retry = False

        sleep(0.7)
        
        if n==len(reply):
            n = 0
            retry = True
        
        yield(b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + image_data + b'\r\n\r\n')


@app.route("/", methods=["POST", "GET"])
def index():
    global question, replyChange, reply, start_recording, n
    reply = "welcome"
    n = 0

    if request.method == "POST":
        rply = request.form.get("rply")
        question = rply
        start_recording = False

        if question != '':
            data="{'question': '" + question + "'}"
            res = requests.post(url=url, data=data, headers=headers)
            res = json.loads(res.text)

            reply = filterstring(res['answers'][0]['answer'])
            replyChange = True
            print(reply)

    return render_template("index.html")


@app.route("/chatbotOn")
def chatbotOn():
    global start_recording, reply, replyChange, question

    start_recording = True

    while True:
        if not start_recording:
            question = ""
            for image in os.listdir('static/question'):
                image_data = open(os.path.join('static/question',image), "rb").read()
                results = prediction_client.classify_image(project_id, model_name, image_data)

                for prediction in results.predictions:
                    if prediction.probability > 0.5:
                        if prediction.tag_name == "space":
                            question = question + " "
                        else:
                            question = question + prediction.tag_name
                os.remove(os.path.join('static/question',image))

            print(question)
            if question != '':
                data="{'question': '" + question + "'}"
                res = requests.post(url=url, data=data, headers=headers)
                res = json.loads(res.text)

                reply = filterstring(res['answers'][0]['answer'])
                replyChange = True
                print(reply)

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