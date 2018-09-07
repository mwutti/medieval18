import cv2
import numpy as np
import logging
import util.detection_utils as util


def binarize(roi):
    return cv2.threshold(roi, 0, 255,
                         cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]


# debug = True
debug = False
detection_threshold = 60
norm_threshold = 3000
skull = cv2.imread('images/skull/skull.png', 0)

def get_first_kill_sec(start_pos_in_video_sec, end_pos_in_video_sec, video_path, team='CT'):
    if debug:
        logging.info("Start detecting first kill for " + team + " from: " + str(start_pos_in_video_sec) + " until:" + str(
            end_pos_in_video_sec))

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    nr_of_frames = 0

    frame_pos_start = int(start_pos_in_video_sec * fps)
    frame_pos_end = int(end_pos_in_video_sec * fps)

    current_frame = frame_pos_start
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos_start)

    detection_map = [0, 0, 0, 0, 0]  # norm must be 60x under norm_threshold

    while current_frame <= frame_pos_end:
        ret, image_np = cap.read()
        current_sec = int(cap.get(cv2.CAP_PROP_POS_MSEC) / 1000)

        current_frame += 1
        nr_of_frames += 1

        image_gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)

        if debug:
            cv2.imshow('kill', image_np)

        # roi for skull/kill detection roi[0] - roi[4] are CounterTerrorists
        if team == 'CT':
            roi = [image_gray[239:255, 611:624], image_gray[262:278, 611:624], image_gray[285:301, 611:624],
                   image_gray[307:323, 611:624], image_gray[330:346, 611:624]]
        else:
            roi = [image_gray[239:255, 16:29], image_gray[262:278, 16:29], image_gray[285:301, 16:29],
                   image_gray[307:323, 16:29], image_gray[330:346, 16:29]]

        # binarize roi
        roi_binarized = [binarize(roi) for roi in roi]
        # calculate L1 norm with skul.png
        l1_norms = [np.linalg.norm(skull.ravel() - roi.ravel(), ord=1) for roi in roi_binarized]

        i = 0
        for norm in l1_norms:
            if norm <= norm_threshold:
                detection_map[i] += 1
            if detection_map[i] >= detection_threshold:
                if debug:
                    cv2.destroyAllWindows()
                logging.info("Detected first kill at: " + util.sec_to_timestamp(current_sec))
                return current_sec
            i += 1

        if debug:
            i = 0
            for roi in roi_binarized:
                cv2.imshow('roi_' + str(i), roi)
                i += 1

            if cv2.waitKey(25) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break
