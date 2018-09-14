import cv2
import numpy as np
import os
import inspect
import logging as logger
import util.detection_utils as util


def binarize(roi):
    return cv2.threshold(roi, 0, 255,
                         cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]


# debug = True
debug = False
detection_threshold = 5
base_dir = os.path.dirname(os.path.abspath(inspect.stack()[0][1]))
skully = cv2.imread(base_dir + '/images/skull/skull.png', 0)


def get_nth_kill_sec(start_pos_in_video_sec, end_pos_in_video_sec, video_path, nth_kill=1, player_stream='P11'):
    # if debug:
    logger.info("Start detecting " + str(nth_kill) + " kill from: " + util.sec_to_timestamp(
        start_pos_in_video_sec) + " until:" + util.sec_to_timestamp(
        end_pos_in_video_sec))

    if player_stream == 'P11':
        skull = cv2.imread(base_dir + '/images/skull/skull.png', 0)
        norm_threshold = 30
    else:
        skull = cv2.imread(base_dir + '/images/skull/skull_Pn.png', 0)
        norm_threshold = 30

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
        current_sec = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000

        current_frame += 1
        nr_of_frames += 1

        image_gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)

        if debug:
            cv2.imshow('kill', image_np)

        # TODO refactor positions into properties file
        if player_stream == 'P11':
            roi = [image_gray[239:255, 611:624],
                   image_gray[262:278, 611:624],
                   image_gray[285:301, 611:624],
                   image_gray[307:323, 611:624],
                   image_gray[330:346, 611:624],
                   image_gray[239:255, 16:29],
                   image_gray[262:278, 16:29],
                   image_gray[285:301, 16:29],
                   image_gray[307:323, 16:29],
                   image_gray[330:346, 16:29]
                   ]
        else:
            roi = [image_gray[170:186, 624:637],
                   image_gray[190:206, 624:637],
                   image_gray[210:226, 624:637],
                   image_gray[230:246, 624:637],
                   image_gray[250:266, 624:637],
                   image_gray[170:186, 3:16],
                   image_gray[190:206, 3:16],
                   image_gray[210:226, 3:16],
                   image_gray[230:246, 3:16],
                   image_gray[250:266, 3:16]
                   ]

        # binarize roi
        roi = [binarize(roi) for roi in roi]

        # normalize roi
        roi_normalized = [np.divide(roi, 255) for roi in roi]

        # calculate L1 norm with skul.png
        np.sum(abs(np.divide(skull, 255) - roi_normalized))
        l1_norms = [np.sum(abs(np.divide(skull, 255) - roi_normalized)) for roi_normalized in roi_normalized]

        # reset detection_map if no kills are visible
        if len([norm for norm in l1_norms if norm <= norm_threshold]) == 0:
            detection_map = np.zeros(10)

        i = 0
        for norm in l1_norms:
            if norm <= norm_threshold:
                detection_map[i] += 1
            i += 1

        # print((detection_map >= detection_threshold).sum())
        if (detection_map >= detection_threshold).sum() == nth_kill:
            if debug:
                cv2.destroyAllWindows()
            logger.info("Detected " + str(nth_kill) + " kill at: " + util.sec_to_timestamp(current_sec))
            return current_sec

        if debug:
            i = 0
            for image in roi:
                cv2.imshow('roi_' + str(i), image)
                i += 1
            # cv2.imshow('roi_' + str(i), roi[9])

            if cv2.waitKey(25) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break
