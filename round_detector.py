import cv2
import numpy as np
import logging
import svm.number_classifier as classifier
import util.detection_utils as util

# debug = True
debug = False

video_path = 'D:/gamestory18-data/train_set'

image_width = 28
nr_of_samples = image_width * image_width

pos_y1 = 10
pos_y2 = 26

pos_left_x1 = 274
pos_left_x2 = 290

pos_right_x1 = 349
pos_right_x2 = 365

detection_threshold = 100


def prepare_for_classifier(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # convert Image to grayscale
    image = cv2.resize(image, dsize=(image_width, image_width), interpolation=cv2.INTER_CUBIC)  # Resize and interpolate
    image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]  # binarize it
    image = np.divide(image, 255)
    image = image.reshape(1, nr_of_samples)  # reshape
    return image


class RoundDetector:

    def __init__(self):
        self.classifier = classifier.NumberClassifier()
        self.classifier.train_classifier()

    def get_round_begin(self, start_pos_in_video_sec, end_pos_in_video_sec, video_full_name, target_round_left,
                        target_round_right):
        logging.info('Looking for ' + str(target_round_left) + ':' + str(
            target_round_right) + ' in video ' + video_full_name + ' from ' + util.sec_to_timestamp(
            start_pos_in_video_sec) + ' to ' + util.sec_to_timestamp(end_pos_in_video_sec))
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
        right_detected = True

        while not (left_detected and right_detected) and current_frame <= frame_pos_end:
            ret, image_np = cap.read()

            current_frame += 1
            nr_of_frames += 1

            current_sec = int(cap.get(cv2.CAP_PROP_POS_MSEC) / 1000)
            current_timestamp = util.sec_to_timestamp(current_sec)

            if not left_detected:
                # process left round
                out_left = self.get_number_left(image_np)
                if debug:
                    print("Left: " + out_left)

                if out_left == target_round_left:
                    nr_left_detected += 1
                    if nr_left_detected >= detection_threshold:
                        if debug:
                            print("left round detected")
                        left_detected = True

            if not right_detected:
                # process right round
                out_right = self.get_number_right(image_np)
                if debug:
                    print("Right: " + out_right)

                if out_right == target_round_right:
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

    def get_number_left(self, image):
        roi_left = image[pos_y1:pos_y2, pos_left_x1:pos_left_x2]
        roi_left_prepared = prepare_for_classifier(roi_left)

        if debug:
            cv2.imshow('object detection_left', roi_left)
        return self.classifier.predict(roi_left_prepared)

    def get_number_right(self, image):
        roi_right = image[pos_y1:pos_y2, pos_right_x1:pos_right_x2]
        roi_right_prepared = prepare_for_classifier(roi_right)

        if debug:
            cv2.imshow('object detection_right', roi_right)
        return self.classifier.predict(roi_right_prepared)
