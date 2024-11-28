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
    try:
        # 데이터베이스 연결 설정
        connection = mysql.connector.connect(
            host="49.247.171.103",       # MySQL 서버 주소
            user="user",   # 사용자 이름
            password="qwer0505",  # 비밀번호
            database="tf2"   # 연결할 데이터베이스 이름
        )
        
        if connection.is_connected():
            return connection
    except Error as e:
        return None

@app.route('/upload', methods=['POST'])
def upload():
    is_front = request.files['is_front'].read()
    camera = ""
    if is_front == 1:
        camera = "front"
        print("Received from front camera")
    elif is_front == 0:
        camera = "rear"
        print("Received from rear camera")
    
    if 'image' not in request.files:
        return jsonify({"message": "No image uploaded"}), 400

    file = request.files['image'].read()
    img = Image.open(io.BytesIO(file)).convert('RGB')
    frame = np.array(img)
    
    # 현재는 임베딩 벡터 따로 생성하지 않고 바로 비교하는 형식으로 동작함
    dfs = DeepFace.find(
        img_path=frame,
        db_path="./face_db/", # db 서버에 저장된 얼굴 폴더 경로
        model_name="Facenet512", # 사용할 모델 이름
        distance_metric="euclidean_l2", # 유사도 알고리즘 종류
        threshold=None,
    )
    
    if len(dfs) > 0:
        image_path = dfs[0]['identity']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        query = f"SELECT name FROM people WHERE face_info = '{image_path}'"
        cursor.execute(query)
        user = cursor.fetchone()
        conn.close()
        
        if user:
            person_id, person_name = user
            log_access(person_id, camera)

            return jsonify({"message": f"Access granted for {person_name} (ID: {person_id})"}), 200
        else:
            unknown_file_name = save_unknown_image(img, camera)
            return jsonify({"message": f"No matching user found. Saved image as {unknown_file_name}"}), 404
        
    else:
        unknown_file_name = save_unknown_image(img, camera)
        return jsonify({"message": f"No matching user found. Saved image as {unknown_file_name}"}), 404

# user 있을 시 유저 id, 시간 기록
def log_access(id, success, cam_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    access_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if cam_id == "front":
        query = f"INSERT INTO Entry_logs (person_id, entry_time) VALUES ('{id}', '{access_time}')"
        cursor.execute(query)
    elif cam_id == "rear":
        query = f"INSERT INTO Entry_logs (person_id, exit_time) VALUES ('{id}', '{access_time}')"
        cursor.execute(query)
    conn.commit()
    conn.close()
    

# 미등록자 일시 프레임 저장하고, -1에 파일이름, 출입시간 기록
def save_unknown_image(image_data, camera):
    conn = get_db_connection()
    save_folder = "/forunknown"
    os.makedirs(save_folder, exist_ok=True)
    
    access_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"unknown_{timestamp}.jpg"
    file_path = os.path.join(save_folder, file_name)

    with open(file_path, "wb") as f:
        f.write(image_data)
        
    cursor = conn.cursor()
    if camera == "front":
        query = f"INSERT INTO Entry_logs (person_id, file_name, entry_time) VALUES (-1,'{file_name}', '{access_time}')"
        cursor.execute(query)
    elif camera == "rear":
        query = f"INSERT INTO Entry_logs (person_id, file_name, exit_time) VALUES (-1,'{file_name}', '{access_time}')"
        cursor.execute(query)

    conn.close()
    return file_name

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9978, threaded=True, debug=False)
    