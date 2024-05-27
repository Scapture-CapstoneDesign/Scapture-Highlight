import cv2
import time
import os

index = 0

def cut_and_slow_down_video(frame):

    # 사용할 비디오 파일
    video_folder_path = "./detection/beforeDetection"
    video_files = os.listdir(video_folder_path)

    # 편집할 영상들
    paths = []

    # 한 영상에 대해 두가지 버전의 영상을 만들기 때문
    # 변경 => 슬로우모션 제거
    for video_file in video_files:
        input_path = f"{video_folder_path}/{video_file}"
        output_normal_path = f"./detection/source/normal_{video_file}"
        # output_slow_path = f"./detection/source/slow_{video_file}"
        paths.append({
            "input_path": input_path,
            "output_paths": output_normal_path,
            # "output_paths": [output_normal_path, output_slow_path]
        })

    # 최종 파일
    video_path = f"./final/output_{index}.mp4"

    normal_start_frame_number = frame - 100
    normal_end_frame_number = frame + 100
    # slow_start_frame_number = frame - 30
    # slow_end_frame_number = frame + 30

    # 하이라이트 기점으로 자르기
    for path in paths:
        cut(path["input_path"], path["output_paths"], normal_start_frame_number, normal_end_frame_number, 1)
        # cut(path["input_path"], path["output_paths"][1], slow_start_frame_number, slow_end_frame_number, 2)

    # 합치기
    fps_list = []
    output_videos = []

    for path in paths:

        output_set = {
            
        }
        
        cap = cv2.VideoCapture(path["output_paths"])
        fps = cap.get(cv2.CAP_PROP_FPS)
        fps_list.append(fps)
            
            
        output_set["normal_video"] = cap

        # for output_path in path["output_paths"]:
        #     cap = cv2.VideoCapture(output_path)
        #     fps = cap.get(cv2.CAP_PROP_FPS)
        #     fps_list.append(fps)
            
        #     if "normal" in output_path:
        #         output_set["normal_video"] = cap
                
        #     elif "slow" in output_path:
        #         output_set["slow_video"] = cap
                
        
        output_videos.append(output_set)

    # 가장 낮은 FPS를 기준으로 설정
    fps = min(fps_list)
    print(fps)

    width = int(output_videos[0]["normal_video"].get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(output_videos[0]["normal_video"].get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'avc1')

    output = cv2.VideoWriter(video_path, fourcc, fps, (width, height))

    for video in output_videos:
        
        while True:
            ret, frame = video["normal_video"].read()
            if not ret:
                # ret2, frame2 = video["slow_video"].read()
                # if not ret2:
                #     break
                # else:
                #     for _ in range(int(fps * 0.3) - 1):
                #         output.write(frame2)
                break
            # FPS에 따라 프레임 재생 시간 조절
            else:
                output.write(frame)

    # 모든 비디오 파일을 닫습니다.
    for video in output_videos:
        video["normal_video"].release()
        # video["slow_video"].release()
    
    output.release()
    print("END")

def cut(input_path, output_path, start_frame, end_frame, speed):
    vc = cv2.VideoCapture(input_path)
    if not vc.isOpened():
        print("Can't open input video.")
        return

    fps = vc.get(cv2.CAP_PROP_FPS)
    print("fps: ", fps)

    width = int(vc.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(vc.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print("width: ", width, ", height: ", height)

    if start_frame >= end_frame:
        print("Invalid frame range.")
        return

    total_frames = int(vc.get(cv2.CAP_PROP_FRAME_COUNT))

    if end_frame > total_frames:
        print("End frame exceeds the total number of frames. Setting end frame to the last frame.")
        end_frame = total_frames

    vc.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    fourcc = cv2.VideoWriter_fourcc(*'avc1')
    vw = cv2.VideoWriter(output_path, fourcc, fps * speed, (width, height))

    frame_count = start_frame
    while frame_count <= end_frame:
        ret, frame = vc.read()
        if not ret:
            break

        vw.write(frame)
        frame_count += 1

    vc.release()
    vw.release()
    print("Video cut and speed adjusted successfully!")

def run(video_file):
    global index
    index = 0
    
    with open(f'./detection/frame/{video_file}_frames.txt', 'r') as file:
        lines = file.readlines()

    for line in lines:
        cut_and_slow_down_video(int(line.strip()))
        index += 1
