import cv2
import requests
import time

cap = cv2.VideoCapture(0)  # 웹캠 연결

server_url = "http://127.0.0.1:5000/upload"  # Flask 서버 주소

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture image")
        break

    _, img_encoded = cv2.imencode('.jpg', frame)

    # Flask 서버로 프레임 전송
    try:
        response = requests.post(server_url, files={"image": img_encoded.tobytes()})
        print(f"Server response: {response.json()}")
    except Exception as e:
        print(f"Error sending frame: {str(e)}")

    # 1초마다 전송
    time.sleep(1)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
