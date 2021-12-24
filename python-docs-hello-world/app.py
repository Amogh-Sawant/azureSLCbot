from flask import Flask, render_template, url_for, Response
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from msrest.authentication import ApiKeyCredentials
import cv2

import requests
import json

# url = "https://asllang.cognitiveservices.azure.com/language/:query-knowledgebases?projectName=AzureASL&api-version=2021-10-01&deploymentName=production"

# headers={'Ocp-Apim-Subscription-Key': '4226713283bd4af1bbb06c34d70388dc', "Content-Type":"application/json"}

# question = ''

# while True:
#     question = input("")
#     data="{'question': '"+question+"'}"

#     if question == "exit": break

#     if question != '':
#         res = requests.post(url=url, data=data, headers=headers)
#         res = json.loads(res.text)

#         print(res['answers'][0]['answer'])

recording_flag = True

app = Flask(__name__)

camera = cv2.VideoCapture(0)

def generate_frames():
    while True:

        success, frame = camera.read()

        if not success: 
            break

        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

        yield(b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        if recording_flag != "True":
            break


@app.route("/")
def index():
    return render_template("index.html", flag="Ino")

@app.route("/video")
def video():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


# def main():

#     try:

#         image = pyautogui.screenshot()
#         image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
#         cv2.imwrite("static/test-images/image3.jpg", image)

#         print("exceucted")

#     except Exception as ex:
#         print(ex)


if __name__ == "__main__":
    app.run(host="0.0.0.0")
