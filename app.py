from flask import Flask
import threading
import paho.mqtt.client as mqtt
# import record  # 사용자 정의 record 모듈
import os
import requests
from detection import detection
from detection import cutVideo
from record import *
from s3Connect import s3_connection
from config import BUCKET_NAME, SERVER_URL

app = Flask(__name__)

# mqtt_broker = "192.168.0.15"
# mqtt_broker = "192.168.1.100"
mqtt_broker = "localhost"

# MQTT 클라이언트 설정
client = mqtt.Client()

# ============== 여기는 사용 X, 테스트용 ================== #
# video_stream_widgets = {
#             "1": [
                # VideoStreamWidget(src=0, output_file='./detection/beforeDetection/test.mp4', window_name='Camera 1'),
                # VPN 테스트용
                # VideoStreamWidget(src="rtsp://admin:asdf1346@@172.27.232.16:9001/stream1/out.h265", output_file='./detection/beforeDetection/goalline.mp4', window_name='Camera 1'),
                # VideoStreamWidget(src="rtsp://admin:asdf1346@@172.27.232.16:9002/stream1/out.h265", output_file='./detection/beforeDetection/goalline2.mp4', window_name='Camera 2'),
                # VideoStreamWidget(src="rtsp://admin:asdf1346@@172.27.232.16:9003/stream1/out.h265", output_file='./detection/beforeDetection/goalline3.mp4', window_name='Camera 3'),
                # VideoStreamWidget(src="rtsp://admin:asdf1346@@172.27.232.45:9004/stream1/out.h265", output_file='./detection/beforeDetection/goalline3.mp4', window_name='Camera 4'),

                # 로컬 테스트용
                # VideoStreamWidget(src="rtsp://admin:asdf1346@@192.168.0.11:554/stream1/out.h265", output_file='./detection/beforeDetection/goalline.mp4', window_name='Camera 1'),
                # VideoStreamWidget(src="rtsp://admin:asdf1346@@192.168.0.12:554/stream1/out.h265", output_file='./detection/beforeDetection/left.mp4', window_name='Camera 2'),
                # VideoStreamWidget(src="rtsp://admin:asdf1346@@192.168.0.13:554/stream1/out.h265", output_file='./detection/beforeDetection/right.mp4', window_name='Camera 3'),
                # VideoStreamWidget(src="rtsp://admin:asdf1346@@192.168.0.14:554/stream1/out.h265", output_file='./detection/beforeDetection/goalline2.mp4', window_name='Camera 4'),
                # VideoStreamWidget(src="rtsp://admin:asdf1346@@192.168.0.15:554/stream1/out.h265", output_file='./detection/beforeDetection/left2.mp4', window_name='Camera 5'),
                # VideoStreamWidget(src="rtsp://admin:asdf1346@@192.168.0.16:554/stream1/out.h265", output_file='./detection/beforeDetection/right2.mp4', window_name='Camera 6')
        #     ]
        # }

video_stream_widgets = {}

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

        
    
def on_message(client, userdata, msg):
    id = msg.topic
    message = msg.payload.decode()
    print(f"{id}: arrived message: ", message)
    
    # 메시지에 따라 적절한 동작 수행
    if message == "start":
        # 녹화 시작 처리
        # 비디오 스트림 위젯 관리 딕셔너리
        # 여기를 변경
        video_stream_widgets[id] = [ 
                # VideoStreamWidget(src=0, output_file='./detection/beforeDetection/test.mp4', window_name='Camera 1'),
                # VPN 테스트용
                # VideoStreamWidget(src="rtsp://admin:asdf1346@@172.27.232.16:9001/stream1/out.h265", output_file='./detection/beforeDetection/goalline.mp4', window_name='Camera 1'),
                # VideoStreamWidget(src="rtsp://admin:asdf1346@@172.27.232.16:9002/stream1/out.h265", output_file='./detection/beforeDetection/goalline2.mp4', window_name='Camera 2'),
                # VideoStreamWidget(src="rtsp://admin:asdf1346@@172.27.232.16:9003/stream1/out.h265", output_file='./detection/beforeDetection/goalline3.mp4', window_name='Camera 3'),
                # VideoStreamWidget(src="rtsp://admin:asdf1346@@172.27.232.45:9004/stream1/out.h265", output_file='./detection/beforeDetection/goalline3.mp4', window_name='Camera 4'),

                # 로컬 테스트용
                # VideoStreamWidget(src="rtsp://admin:asdf1346@@192.168.0.11:554/stream1/out.h265", output_file='./detection/beforeDetection/goalline.mp4', window_name='Camera 1'),
                # VideoStreamWidget(src="rtsp://admin:asdf1346@@192.168.0.12:554/stream1/out.h265", output_file='./detection/beforeDetection/left.mp4', window_name='Camera 2'),
                # VideoStreamWidget(src="rtsp://admin:asdf1346@@192.168.0.13:554/stream1/out.h265", output_file='./detection/beforeDetection/right.mp4', window_name='Camera 3'),
                # VideoStreamWidget(src="rtsp://admin:asdf1346@@192.168.0.14:554/stream1/out.h265", output_file='./detection/beforeDetection/goalline2.mp4', window_name='Camera 4'),
                # VideoStreamWidget(src="rtsp://admin:asdf1346@@192.168.0.15:554/stream1/out.h265", output_file='./detection/beforeDetection/left2.mp4', window_name='Camera 5'),
                # VideoStreamWidget(src="rtsp://admin:asdf1346@@192.168.0.16:554/stream1/out.h265", output_file='./detection/beforeDetection/right2.mp4', window_name='Camera 6')
            ] 
        start_recording(video_stream_widgets[id], id)
        print(f"Start recording for {id}")
    elif message == "end":
        # 녹화 종료 처리
        stop_recording(video_stream_widgets[id], id)
        client.unsubscribe(id)
        del video_stream_widgets[id]
        print(f"Stop recording for {id}")

client.on_connect = on_connect
client.on_message = on_message

def run_mqtt_client():
    client.connect(mqtt_broker, 1883, 60)
    client.loop_start()  # loop_forever() 대신 loop_start()를 사용하여 별도의 스레드에서 MQTT 클라이언트를 실행


# 구독 관리를 위한 id 집합
subscribed_ids = set()

def manage_subscription(id, action):
    global subscribed_ids
    topic = f"recording/control/{id}"
    if action == "subscribe" and id not in subscribed_ids:
        client.subscribe(topic)
        subscribed_ids.add(id)
        print(f"Subscribed to {topic}")
    elif action == "unsubscribe" and id in subscribed_ids:
        client.unsubscribe(topic)
        subscribed_ids.remove(id)
        print(f"Unsubscribed from {topic}")



@app.route('/start/<id>')
def start(id):
    # 영상 녹화 시작
    client.subscribe(id)
    # manage_subscription(id, "subscribe")
    client.publish(id, "start", qos=0)
    return 'Recording started for ' + id

# 영상 녹화가 끝나면 detection/beforeDetection > detection/source 에 하이라이트로 자르고 > final 폴더
@app.route('/end/<id>')
def stop(id):

    # 영상 녹화 종료
    # client.publish(id, "end", qos=0)
    # client.unsubscribe(id)

    # 하이라이트 검출
    video_folder_path = "./detection/beforeDetection"
    video_files = os.listdir(video_folder_path)
    
    if video_files[0]:
        # 하이라이트 기점 찾기 (frame)
        detection.run(video_files[0])

        # 하이라이트 frame 기준으로 자르기
        cutVideo.run(video_files[0])

        # 최종 영상 s3에 저장
        s3 = s3_connection()
        video_folder_path = "./final"
        video_files = os.listdir(video_folder_path)
        video_urls = []

        for video_file in video_files:
            # 파일 이름 알아내기
            file_path = os.path.join(video_folder_path, video_file)
            with open(file_path, 'rb') as data:
                s3.upload_fileobj(data, BUCKET_NAME, video_file)
                video_url = f"https://{BUCKET_NAME}.s3.ap-northeast-2.amazonaws.com/{video_file}"
                # print(video_url)
                video_urls.append(video_url)
                print(f"Uploaded {video_file} to S3 bucket")

        # Spring 서버로 POST 요청 전송
        spring_server_url = f"http://{SERVER_URL}/api/video"
        payload = {
            "title": "영상1",
            "place": "한성대학교",
            "videoUrl": video_urls
        }
        response = requests.post(spring_server_url, json=payload)
        print(response)
        

        

    # source 파일 정리
    filePath = "./detection/source"
    if os.path.exists(filePath):
        for file in os.scandir(filePath):
            os.remove(file.path)
            print('Remove All File')
        else:
            print('Directory Not Found')

    # final 파일 정리
    filePath = "./final"
    if os.path.exists(filePath):
        for file in os.scandir(filePath):
            os.remove(file.path)
            print('Remove All File')
        else:
            print('Directory Not Found')

    return 'Recording stopped for ' + id


@app.route('/test')
def test():
    # 하이라이트 검출
    # video_folder_path = "./detection/beforeDetection"
    # video_files = os.listdir(video_folder_path)
    
    # if video_files[0]:
    #     detection.run(video_files[0])

    #     cutVideo.run(video_files[0])

    # filePath = "./detection/source"
    # if os.path.exists(filePath):
    #     for file in os.scandir(filePath):
    #         os.remove(file.path)
    #         print('Remove All File')
    #     else:
    #         print('Directory Not Found')

     # S3로 보내기
    s3 = s3_connection()

    # 최종 파일 가져오기
    video_folder_path = "./final"
    video_files = os.listdir(video_folder_path)

    # 최종 영상들 보내기
    for video_file in video_files:
        file_path = os.path.join(video_folder_path, video_file)
        with open(file_path, 'rb') as data:
            s3.upload_fileobj(data, BUCKET_NAME, video_file)
            print(f"Uploaded {video_file} to S3 bucket")

            
    return 'test code'

if __name__ == '__main__':
    threading.Thread(target=run_mqtt_client, daemon=True).start()
    app.run(host='0.0.0.0', port=8000, threaded=False, debug=True)
