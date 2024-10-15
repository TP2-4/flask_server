import os
from flask import Flask, request, jsonify
from deepface import DeepFace
from PIL import Image
import numpy as np
import cv2
import sqlite3
import io
from datetime import datetime

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('face_recognition.db') # db 서버 주소 
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        return jsonify({"message": "No image uploaded"}), 400

    file = request.files['image'].read()
    img = Image.open(io.BytesIO(file)).convert('RGB')
    frame = np.array(img)
    
    # 현재는 임베딩 벡터 따로 생성하지 않고 바로 비교하는 형식으로 동작함
    dfs = DeepFace.find(
        img_path="temp_image.jpg",
        db_path="./face_db/", # db 서버에 저장된 얼굴 폴더 경로
        model_name="VGG-Face", # 사용할 모델 이름
        distance_metric="cosine", # 유사도 알고리즘 종류
        threshold=None,
    )
    
    if len(dfs) > 0:
        image_path = dfs[0]['identity']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM users WHERE image_path = ?", (image_path,))
        user = cursor.fetchone()
        conn.close()
    
        if user:
            person_name = user['name']
            log_access(person_name, success=1)
            return jsonify({"message": f"Access granted for {person_name}"}), 200
        else:
            log_access("Unknown", success=0)
            return jsonify({"message": "No matching user found."}), 404
    else:
        log_access("Unknown", success=0)  # 인식 실패 시 실패 기록
        return jsonify({"message": "No matches found."}), 404

def log_access(name, success):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    access_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO access_logs (name, success) VALUES (?, ?)", (name, success))
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    app.run(port=5000)
    