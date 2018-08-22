import cv2

video_path = 'D:/gamestory18-data/train_set'

def get_round_begin_offset():
    cap = cv2.VideoCapture(video_path + '/' + '2018-03-02_P11.mp4')
    fps = cap.get(cv2.CAP_PROP_FPS)

    nr_of_frames = 0
    begin_sec = 5000
    end_sec = 5060
    frame_pos_start = int(begin_sec * fps)
    frame_pos_end = int(end_sec * fps)

    current_frame = frame_pos_start

    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos_start)

    while current_frame <= frame_pos_end:
        ret, image_np = cap.read()
        current_frame += 1
        pos_msec = cap.get(cv2.CAP_PROP_POS_MSEC)
        nr_of_frames += 1

        image_gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)

        roi_left = image_gray[10:30, 270:295]
        roi_right = image_gray[10:30, 345:370]
        print(image_gray.shape)
        cv2.imshow('object detection_left', roi_left)
        cv2.imshow('object detection_right', roi_right)
        cv2.imshow('object detection', image_np)

        if cv2.waitKey(25) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break


get_round_begin_offset()
