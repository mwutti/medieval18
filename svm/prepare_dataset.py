import cv2
import os
import numpy as np
import logging


def timestamp_to_sec(timestamp):
    split_timestamp = timestamp.split(':')
    stream_timestamp_sec = int(split_timestamp[0]) * 3600 + int(split_timestamp[1]) * 60 + int(
        split_timestamp[2].split('.')[0])
    return stream_timestamp_sec

def sec_to_timestamp(sec):
    seconds = sec % 60
    minutes = sec // 60
    hours = 0
    if minutes > 60:
        hours = minutes // 60
        minutes = minutes % 60
    return str(hours) + ':' + str(minutes) + ':' + str(seconds)

video_path = 'D:/gamestory18-data/train_set/2018-03-02_P11.mp4'
dest_path = 'images'


pos_y1 = 10
pos_y2 = 26

pos_single_left_x1 = 274
pos_single_left_x2 = 290

pos_single_right_x1 = 347
pos_single_right_x2 = 363

pos_double_left_1_x1 = 275
pos_double_left_1_x2 = 283

pos_double_left_2_x1 = 281
pos_double_left_2_x2 = 289

pos_double_right_1_x1 = 347
pos_double_right_1_x2 = 355

pos_double_right_2_x1 = 356
pos_double_right_2_x2 = 364

search_duration = 20
nr_of_frames_to_extract = 500
begin_timestamps = ['1:05:55', '1:06:41', '1:08:52', '1:09:37', '1:11:25', '1:12:26', '1:16:50', '1:18:24', '1:20:57', '1:22:56']

cap = cv2.VideoCapture(video_path)
fps = cap.get(cv2.CAP_PROP_FPS)


def preprocess_and_extract_roi(image):
    """Preprocesses and extracts the left roi

    Args:
        image: Input image

    Returns:
        the preprocessed roi where the left round number is shown

    """
    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    roi = image_gray[pos_y1:pos_y2, pos_single_left_x1:pos_single_left_x2]
    roi = cv2.resize(roi, dsize=(28, 28), interpolation=cv2.INTER_CUBIC)
    roi = cv2.threshold(roi, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    return roi


# extract images from video for 0-9
for i in range(3, 10):
    if not os.path.exists(dest_path + '/' + str(i)):
        os.makedirs(dest_path + '/' + str(i))

    begin_sec = timestamp_to_sec(begin_timestamps[i])
    frame_pos_start = int(begin_sec * fps)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos_start)

    for j in range(0, nr_of_frames_to_extract):
        ret, image_np = cap.read()

        # cv2.imshow('object detection', image_np)
        roi_left = preprocess_and_extract_roi(image_np)

        # cv2.imshow('object detection_left', roi_left)

        cv2.imwrite('images/' + str(i) + '/' + str(j) + '.png', roi_left)
        # if cv2.waitKey(25) & 0xFF == ord('q'):
        #     cv2.destroyAllWindows()
        #     break

