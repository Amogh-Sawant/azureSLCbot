from time import sleep
import os


image_data = open(os.path.join('static',"a.svg"), "rb").read()
print(type(image_data))