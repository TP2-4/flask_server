### Server

현재 로컬에 저장된 DB와 로컬 웹 캠으로 동작하는 간단한 flask 서버 코드로 구성되어 있음

#### 함수 구성

- get_db_connection() -> DB 연결
- upload() -> 라즈베리파이로부터 받은 POST를 처리하는 부분
  현재는 이미지를 전달받은 뒤 해당 이미지를 그대로 DeepFace 모듈에 전달하여 결과값을 파일 이름으로 받는 형식으로 동작 (추후 임베딩 벡터를 생성하여 비교하는 형식으로 변경할 예정)
  동일한 얼굴의 이미지파일이 존재한다면 DB에서 이미지 파일 이름을 통해 사용자의 이름을 가져오고, log_access() 함수에 사용자 이름을 전달하여 출입기록 저장
- log_access(name, success) -> conn에 db 가져온 다음 출입시간과 사용자 이름을 저장하는 방식



### Client

cap에 웹캠을 연결해서 frame을 받아와서 1초마다 flask 서버로 프레임을 전송하는 기능을 수행함