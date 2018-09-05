import cv2
import numpy as np
import logging
import util.detection_utils as util
from tensorflow import keras

video_path = 'D:/gamestory18-data/train_set'
model_path = "training/mnist/cnn.h5"
model = keras.models.load_model(model_path)

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

debug = True
# debug = False
detection_threshold = 100

def resize_for_mnist(roi):
    return cv2.resize(roi, dsize=(28, 28), interpolation=cv2.INTER_CUBIC)


def binarize(roi):
    return cv2.threshold(roi, 0, 255,
                         cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]


def reshape_for_mnist(roi):
    roi = roi.reshape(1, 28, 28, 1)
    roi = roi.astype('float32')
    roi /= 255
    return roi


def prepare_for_mnist(roi):
    roi = resize_for_mnist(roi)
    roi = binarize(roi)
    roi = reshape_for_mnist(roi)
    return roi


def get_single_number_left(image):
    roi_left = image[pos_y1:pos_y2, pos_single_left_x1:pos_single_left_x2]
    roi_left_prepared = prepare_for_mnist(roi_left)
    if debug:
        cv2.imshow('object detection_left', roi_left)
    return str(np.argmax(model.predict(roi_left_prepared)))


def get_single_number_right(image):
    roi_right = image[pos_y1:pos_y2, pos_single_right_x1:pos_single_right_x2]
    roi_right_prepared = prepare_for_mnist(roi_right)
    if debug:
        cv2.imshow('object detection_right', roi_right)
    return str(np.argmax(model.predict(roi_right_prepared)))


def get_double_number_left(image):
    roi_left_1 = image[pos_y1:pos_y2, pos_double_left_1_x1:pos_double_left_1_x2]
    roi_left_2 = image[pos_y1:pos_y2, pos_double_left_2_x1:pos_double_left_2_x2]

    roi_left_prepared_1 = prepare_for_mnist(roi_left_1)
    roi_left_prepared_2 = prepare_for_mnist(roi_left_2)

    out_left_1 = model.predict(roi_left_prepared_1)
    out_left_2 = model.predict(roi_left_prepared_2)

    number_string_1 = str(np.argmax(out_left_1))
    # first number could not be 7
    if number_string_1 == '7':
        number_string_1 = '1'

    number_string_2 = str(np.argmax(out_left_2))
    if debug:
        cv2.imshow('object detection_left_1', roi_left_1)
        cv2.imshow('object detection_left_2', roi_left_2)
    return number_string_1 + number_string_2


def get_double_number_right(image):
    roi_right_1 = image[pos_y1:pos_y2, pos_double_right_1_x1:pos_double_right_1_x2]
    roi_right_2 = image[pos_y1:pos_y2, pos_double_right_2_x1:pos_double_right_2_x2]
    roi_left_prepared_1 = prepare_for_mnist(roi_right_1)
    roi_left_prepared_2 = prepare_for_mnist(roi_right_2)

    out_right_1 = model.predict(roi_left_prepared_1)
    out_right_2 = model.predict(roi_left_prepared_2)

    number_string_1 = str(np.argmax(out_right_1))
    # first number could not be 7
    if number_string_1 == '7':
        number_string_1 = '1'

    number_string_2 = str(np.argmax(out_right_2))
    if debug:
        cv2.imshow('object detection_left_1', roi_right_1)
        cv2.imshow('object detection_left_2', roi_right_2)
    return number_string_1 + number_string_2


def get_round_begin(start_pos_in_video_sec, end_pos_in_video_sec, video_full_name, target_round_left,
                    target_round_right):
    logging.info('Looking for ' + str(target_round_left) + ':' + str(target_round_right) + ' in video ' + video_full_name + ' from ' + util.sec_to_timestamp(start_pos_in_video_sec) + ' to ' + util.sec_to_timestamp(end_pos_in_video_sec))
    cap = cv2.VideoCapture(video_full_name)
    fps = cap.get(cv2.CAP_PROP_FPS)
    nr_of_frames = 0

    frame_pos_start = int(start_pos_in_video_sec * fps)
    frame_pos_end = int(end_pos_in_video_sec * fps)

    current_frame = frame_pos_start
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos_start)

    nr_left_detected = 0
    nr_right_detected = 0
    left_detected = False
    right_detected = False

    while not (left_detected and right_detected) and current_frame <= frame_pos_end:
        ret, image_np = cap.read()
        current_frame += 1
        nr_of_frames += 1

        current_sec = int(cap.get(cv2.CAP_PROP_POS_MSEC) / 1000)
        current_timestamp = util.sec_to_timestamp(current_sec)

        # convert Image to grayscale
        image_gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)

        if not left_detected:
            # process left round
            if target_round_left > 9:
                out_left = get_double_number_left(image_gray)
                if debug:
                    print("Left: " + out_left)
            else:
                out_left = get_single_number_left(image_gray)
                if debug:
                    print("Left: " + out_left)

            if out_left == str(target_round_left):
                nr_left_detected += 1
                if nr_left_detected >= detection_threshold:
                    if debug:
                        print("left round detected")
                    left_detected = True

        if not right_detected:
            # process right round
            if target_round_right > 9:
                out_right = get_double_number_right(image_gray)
                if debug:
                    print("right: " + out_right)
            else:
                out_right = get_single_number_right(image_gray)
                if debug:
                    print("Right: " + out_right)

            if out_right == str(target_round_right):
                nr_right_detected += 1
                if nr_right_detected >= detection_threshold:
                    if debug:
                        print("right round detected")
                    right_detected = True

        if left_detected and right_detected:
            logging.info("Detected round start at " + current_timestamp)
            return current_sec

        if debug:
            cv2.imshow('object detection', image_np)
            if cv2.waitKey(25) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break
