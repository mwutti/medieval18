import cv2
import numpy as np
import logging as logger
import util.detection_utils as util
logger.basicConfig(format='%(levelname)s: %(asctime)s %(message)s', level=logger.DEBUG)


def binarize(roi):
    return cv2.threshold(roi, 0, 255,
                         cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]


debug = True
# debug = False
detection_threshold = 20
norm_threshold = 20
skull = cv2.imread('images/skull/skull.png', 0)

video_path = 'D:/gamestory18-data/train_set/2018-03-02_P11.mp4'

cap = cv2.VideoCapture(video_path)
fps = cap.get(cv2.CAP_PROP_FPS)

max_duration = 20000


def get_nth_kill_sec(start_pos_in_video_sec, end_pos_in_video_sec, video_path, nth_kill=1):
    if debug:
        logger.info("Start detecting " + str(nth_kill) + " kill from: " + util.sec_to_timestamp(start_pos_in_video_sec) + " until:" + util.sec_to_timestamp(
            end_pos_in_video_sec))

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    nr_of_frames = 0

    frame_pos_start = int(start_pos_in_video_sec * fps)
    frame_pos_end = int(end_pos_in_video_sec * fps)

    current_frame = frame_pos_start
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos_start)

    detection_map = np.zeros(10)

    while current_frame <= frame_pos_end:
        ret, image_np = cap.read()
        current_sec = int(cap.get(cv2.CAP_PROP_POS_MSEC) / 1000)

        current_frame += 1
        nr_of_frames += 1

        image_gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)

        if debug:
            cv2.imshow('kill', image_np)

        #TODO refactore positions into properties file
        roi = [image_gray[239:255, 611:624], image_gray[262:278, 611:624], image_gray[285:301, 611:624],
               image_gray[307:323, 611:624], image_gray[330:346, 611:624],
               image_gray[239:255, 16:29], image_gray[262:278, 16:29], image_gray[285:301, 16:29],
               image_gray[307:323, 16:29], image_gray[330:346, 16:29]
               ]

        # binarize roi
        roi_binarized = [binarize(roi) for roi in roi]
        # normalize roi
        roi_normalized = [np.divide(roi, 255) for roi in roi_binarized]

        # calculate L1 norm with skul.png
        np.sum(abs(np.divide(skull, 255) - roi_normalized))
        l1_norms = [np.sum(abs(np.divide(skull, 255) - roi_normalized)) for roi_normalized in roi_normalized]

        i = 0
        for norm in l1_norms:
            if norm <= norm_threshold:
                detection_map[i] += 1
            i += 1

        if (detection_map >= norm_threshold).sum() >= nth_kill:
            if debug:
                cv2.destroyAllWindows()
            logger.info("Detected " + str(nth_kill) + " kill at: " + util.sec_to_timestamp(current_sec))
            return current_sec

        if debug:
            i = 0
            for roi in roi_binarized:
                cv2.imshow('roi_' + str(i), roi)
                i += 1

            if cv2.waitKey(25) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break


get_nth_kill_sec(4010, 4500, video_path, 2)

