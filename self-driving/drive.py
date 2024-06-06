import socketio 
from  socketio import Server
import eventlet
import numpy as np
from flask import Flask 
from keras.models import load_model 
import base64
from io import BytesIO 
from PIL import Image 
import cv2

sio = Server()
app = Flask(__name__)
speed_limit = 10

def img_processing(img):
    img = img[60:135,:,:]
    img = cv2.cvtColor(img, cv2.COLOR_RGB2YUV)
    img = cv2.GaussianBlur(img, (3,3), 0)
    img = cv2.resize(img, (200, 66))
    img = img / 255
    return img

@sio.on('connect')
def connect(sid, environ):
    print('connected')
    send_control(0, 0)

def send_control(steering_angle, throttle):
    sio.emit('steer', data={
        'steering_angle': steering_angle.__str__(),
        'throttle': throttle.__str__()
    })

@sio.on('telemetry')
def telemetry(sid, data):
    speed = float(data['speed'])  # Fix: Access 'speed' key from data dictionary
    image = Image.open(BytesIO(base64.b64decode(data['image'])))
    image = np.asarray(image)
    image = img_processing(image)
    image = np.array([image])
    steering_angle = float(model.predict(image))  # Fix: Call predict method correctly
    throttle = 1.0 - speed / speed_limit
    print('{},{},{}'.format(steering_angle, throttle, speed))
    send_control(steering_angle, throttle)

if __name__ =='__main__':
    model = load_model('model/model.h5')
    app = socketio.Middleware(sio, app)  # Fix: Correct usage of Middleware
    eventlet.wsgi.server(eventlet.listen(('', 4567)), app)  # Fix: Correct typo in 'server'
