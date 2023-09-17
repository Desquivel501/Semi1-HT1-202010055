import boto3
import os
from dotenv import load_dotenv
import base64
from flask import Flask, jsonify, request
from flask_cors import CORS
from PIL import Image, ImageDraw, ImageFont

load_dotenv()

app = Flask(__name__)
CORS(app)

REKOGNITION_KEY_ID = os.getenv('REKOGNITION_KEY_ID')
REKOGNITION_SECRET_KEY = os.getenv('REKOGNITION_SECRET_KEY')

rekognition = boto3.client('rekognition', region_name='us-east-1',
                           aws_access_key_id=REKOGNITION_KEY_ID,
                           aws_secret_access_key=REKOGNITION_SECRET_KEY)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/hoja1-202010055", methods=['POST'])
def detect():

    data = request.get_json()
    image = base64.b64decode(data['image'])

    with open('images/image.png', 'wb') as f:
        f.write(image)

    rekognition_response = rekognition.detect_labels(
        Image={'Bytes': image}, MinConfidence=70)

    image = Image.open('images/image.png')
    image_width, image_height = image.size
    draw = ImageDraw.Draw(image)

    line_width = 3
    for item in rekognition_response['Labels']:
        if 'Instances' in item:
            for instance in item['Instances']:
                bounding_box = instance['BoundingBox']
                width = image_width * bounding_box['Width']
                height = image_height * bounding_box['Height']
                left = image_width * bounding_box['Left']
                top = image_height * bounding_box['Top']

                left = int(left)
                top = int(top)
                width = int(width) + left
                height = int(height) + top

                draw.rectangle(((left, top), (width, height)),
                               outline='red', width=line_width)

                draw.text((left, top), item['Name'],
                          font=ImageFont.truetype('arial.ttf', 30), fill=(0, 0, 0, 255))

    image.save('images/image_labels.png')

    return jsonify(rekognition_response)


if __name__ == "__main__":
    app.run(threaded=True, debug=True)
