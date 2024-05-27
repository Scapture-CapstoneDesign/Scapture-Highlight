from threading import Thread, Event
import cv2
import time


class VideoStreamWidget(object):
    def __init__(self, src=0, output_file=None, window_name="Video Stream"):
        self.capture = cv2.VideoCapture(src)
        self.output_file = output_file
        self.window_name = window_name
        self.start_event = Event()  # 각 인스턴스의 시작 이벤트
        self.stop_event = Event()  # 각 인스턴스의 중지 이벤트

        self.start_event.clear()  # 추가된 코드
        self.stop_event.clear()  # 추가된 코드

        if output_file:
            fourcc = cv2.VideoWriter_fourcc(*'avc1')
            fps = self.capture.get(cv2.CAP_PROP_FPS)
            # self.delay = max(1, int(1000 / fps))
            # self.delay = 1
            width, height = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)), int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.video_writer = cv2.VideoWriter(output_file, fourcc, fps, (width, height))

        print("생성")

    def update(self):
        
        print("녹화를 시작합니다.")
        while not self.stop_event.is_set():
        # while True:
            # if self.stop_event.is_set():
            #     break

            if self.capture.isOpened():
                ret, frame = self.capture.read()
                print(frame)
                if ret:
                    self.frame = frame
                    print(frame)
                    if self.output_file:
                        self.video_writer.write(self.frame)
                else:
                    print("Frame read failed, trying to reconnect...")
                    self.reconnect()
                    continue
            
            # time.sleep(self.delay / 1000.0)

    def reconnect(self):
        # 여기에 재연결 로직 구현
        pass

    def show_frame(self):
        if hasattr(self, 'frame'):
            cv2.imshow(self.window_name, self.frame)

    def release_resources(self):
        if self.output_file:
            self.video_writer.release()
        self.capture.release()

    def make_thread(self):
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()
        print("start event")
        # self.start_event.set()
        

    def stop(self):
        self.stop_event.set()


# 녹화 상태 관리 딕셔너리
recording_status = {}

def start_recording(video_stream_widgets, id):
    id_str = int(id)
    print(video_stream_widgets)
    # 동일한 요청이 들어올 수 있기 때문에 확인
    # if recording_status[id_str] != "recording":
    # if id_str in video_stream_widgets:
    for video_stream in video_stream_widgets:
        
        video_stream.make_thread() # 각 비디오 스트림의 녹화 시작
        print(f"{video_stream.window_name}: 녹화 시작")
            # recording_status[id_str] = "recording"
    # else:
    #     print(f"{id_str}은 이미 사용중입니다.")

def stop_recording(video_stream_widgets, id):
    id_str = int(id)
    # if id_str in recording_status and recording_status[id_str] == "recording":
    # if id_str in video_stream_widgets:
    for video_stream in video_stream_widgets:
        video_stream.stop() # 각 비디오 스트림의 녹화 중지
        video_stream.release_resources()
        print(f"{video_stream.window_name}: 녹화 중지")
    # cv2.destroyAllWindows()
        # recording_status[id_str] = "stopped"

