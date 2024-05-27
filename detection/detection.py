import cv2
import pandas as pd
import numpy as np
from ultralytics import YOLO
from detection.tracker import Tracker

def run(video_file):

    model = YOLO('yolov8s.pt')  # YOLO 모델 사용

    # 마우스의 현재 위치 좌표를 저장할 전역 변수
    mouse_x, mouse_y = 0, 0

    # 마우스의 현재 위치로 x, y 좌표값 출력 (영역 그릴 때 x, y 좌표값 확인용)
    def RGB(event, x, y, flags, param):
        global mouse_x, mouse_y
        if event == cv2.EVENT_MOUSEMOVE:
            mouse_x, mouse_y = x, y

    # cv2.namedWindow('RGB')
    cv2.setMouseCallback('RGB', RGB)

    # 사용할 비디오 파일
    cap = cv2.VideoCapture(f"./detection/beforeDetection/{video_file}")

    # 학습 클래스 불러오기
    my_file = open("./detection/coco.txt", "r")
    data = my_file.read()
    class_list = data.split("\n")

    count = 0

    tracker = Tracker()
    # 필드박스(밖) 밖 -> 안 = 골 좌상,우상,우하,좌하
    area1 = [(354, 177), (783, 136), (1015, 434), (604, 483)]
    # 골대박스(안) 초록
    area2 = [(153, 201), (340, 181), (485, 435), (205, 459)]

    ball_enter = {}
    frame_dict = {}  # 객체 ID를 키로 하고 해당 객체가 퇴장 또는 입장할 때의 프레임을 값으로 저장

    # 입장 횟수 카운터
    enter_count = 0

    after_change_state = 0

    # 입장프레임 저장 파일
    enter_frame_file = open(f"./detection/frame/{video_file}_frames.txt", "w")

    state = False # 현재 공의 상태
    previous_state = False  # 이전 상태를 추적하기 위한 변수

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        count += 1
        if count % 3 != 0:
            continue
        frame = cv2.resize(frame, (1020, 500))

        results = model.predict(frame)
        boxes = results[0].boxes  # boxes 객체를 바로 참조

        list = []
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0].numpy()
            conf = box.conf[0].numpy()
            cls = int(box.cls[0].numpy())
            c = class_list[cls]
            if 'sports ball' in c:
                list.append([int(x1), int(y1), int(x2), int(y2)])
                # 객체의 테두리 그리기
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 2)  # 파란색 테두리

        bbox_id = tracker.update(list)

        for bbox in bbox_id:
            x3, y3, x4, y4, id = bbox

            results1 = cv2.pointPolygonTest(np.array(area1, np.int32), ((x4, y4)), False)
            results2 = cv2.pointPolygonTest(np.array(area2, np.int32), ((x4, y4)), False)

            if results2 >= 0:
                state = True  # 객체가 area2에 있음
                ball_enter[id] = (x4, y4)
                if id not in frame_dict:
                    frame_dict[id] = count  # 입장한 객체의 프레임 저장
                    if not previous_state:
                        enter_count += 1  # 이전 상태가 False였으면 입장 횟수 증가
                        # 입장 순간의 프레임 값을 파일에 저장
                        enter_frame_file.write(f"{count}\n")
            elif results1 >= 0:
                state = False  # 객체가 area1에 있음

        cv2.polylines(frame, [np.array(area1, np.int32)], True, (0, 0, 255), 1)
        cv2.polylines(frame, [np.array(area2, np.int32)], True, (0, 255, 0), 1)

        # 입장 횟수 출력
        print("입장 횟수:", enter_count)
        print("State:", state, "프레임", after_change_state)

        # 현재 마우스 좌표 출력
        print(f"현재 마우스 좌표: ({mouse_x}, {mouse_y})")
        
        previous_state = state  # 현재 상태를 이전 상태로 업데이트

        # cv2.imshow("RGB", frame)
        # if cv2.waitKey(1) & 0xFF == 27:
        #     break

    # # 입장시 해당 프레임 출력
    # for obj_id, enter_frame in frame_dict.items():
    #     print(f"Object ID: {obj_id}, 입장 프레임: {enter_frame}")

    # 파일 닫기
    enter_frame_file.close()
    cap.release()
    cv2.destroyAllWindows()

    # plus.makeShortFormVideo()
    # plus.makeLongVideo()