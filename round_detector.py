import cv2
import numpy as np
import logging
import svm.number_classifier as classifier
import util.detection_utils as util

# debug = True
debug = False

video_path = 'D:/gamestory18-data/train_set'
wins_the_round = cv2.imread('images/win_round/wins_the_round.png', 0)

image_width = 28
nr_of_samples = image_width * image_width

pos_y1_P11 = 10
pos_y2_P11 = 26

pos_left_x1_P11 = 274
pos_left_x2_P11 = 290

pos_right_x1_P11 = 349
pos_right_x2_P11 = 365

pos_y1_Pn = 2
pos_y2_Pn = 18

pos_left_x1_Pn = 275
pos_left_x2_Pn = 291

pos_right_x1_Pn = 345
pos_right_x2_Pn = 361

detection_threshold_for_number = 100
detection_threshold_for_wins_the_round = 200


def prepare_for_classifier(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # convert Image to grayscale
    image = cv2.resize(image, dsize=(image_width, image_width), interpolation=cv2.INTER_CUBIC)  # Resize and interpolate
    image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]  # binarize it
    image = np.divide(image, 255)
    image = image.reshape(1, nr_of_samples)  # reshape
    return image


def check_correct_round_start(image):
    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    roi_left = image_gray[30:45, 170:260]
    roi_right = image_gray[30:45, 375:465]

    roi_right = cv2.threshold(roi_right, 0, 255,
                              cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    roi_left = cv2.threshold(roi_left, 0, 255,
                             cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    win_normalized = np.divide(wins_the_round, 255)
    roi_right_normalized = np.divide(roi_right, 255)
    roi_left_normalized = np.divide(roi_left, 255)

    norm_right = np.sum(abs(win_normalized - roi_right_normalized))
    norm_left = np.sum(abs(win_normalized - roi_left_normalized))

    return not (norm_right <= detection_threshold_for_wins_the_round or norm_left <= detection_threshold_for_wins_the_round)


class RoundDetector:

    def __init__(self):
        self.classifier = classifier.NumberClassifier()
        self.classifier.train_classifier()

    def get_round_begin(self, start_pos_in_video_sec, end_pos_in_video_sec, video_full_name, target_round_left,
                        target_round_right, player_stream='P11', pos_at_one_round_detected=False):
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
        right_detected = False

        while not (left_detected and right_detected) and current_frame <= frame_pos_end:
            ret, image_np = cap.read()

            current_frame += 1
            nr_of_frames += 1

            current_sec = int(cap.get(cv2.CAP_PROP_POS_MSEC) / 1000)
            current_timestamp = util.sec_to_timestamp(current_sec)

            # first check if the string 'wins the round !' is visible... if so... do not detect round begin, it's one round before
            # correct_round_start = check_correct_round_start(image_np)

            if not left_detected:
                # process left round
                out_left = self.get_number_left(image_np, player_stream=player_stream)
                if debug:
                    print("Left: " + str(out_left))

                if out_left == target_round_left:
                    nr_left_detected += 1
                    if nr_left_detected >= detection_threshold_for_number:
                        if debug:
                            print("left round detected")
                        left_detected = True

            if not right_detected:
                # process right round
                out_right = self.get_number_right(image_np, player_stream=player_stream)
                if debug:
                    print("Right: " + str(out_right))

                if out_right == target_round_right:
                    nr_right_detected += 1
                    if nr_right_detected >= detection_threshold_for_number:
                        if debug:
                            print("right round detected")
                        right_detected = True

            if left_detected and right_detected:
                logging.info("Detected round start at " + current_timestamp)
                return current_sec

            if pos_at_one_round_detected and (left_detected or right_detected):
                logging.warning("Just one round detected")
                logging.info("Detected round start at " + current_timestamp)
                return current_sec

            if debug:
                cv2.imshow('object detection', image_np)
                if cv2.waitKey(25) & 0xFF == ord('q'):
                    cv2.destroyAllWindows()
                    break

    def get_number_left(self, image, player_stream='P11'):
        if player_stream == 'P11':
            roi_left = image[pos_y1_P11:pos_y2_P11, pos_left_x1_P11:pos_left_x2_P11]
        else:
            roi_left = image[pos_y1_Pn:pos_y2_Pn, pos_left_x1_Pn:pos_left_x2_Pn]

        roi_left_prepared = prepare_for_classifier(roi_left)

        if debug:
            roi_left = cv2.cvtColor(roi_left, cv2.COLOR_BGR2GRAY)  # convert Image to grayscale
            roi_left = cv2.resize(roi_left, dsize=(image_width, image_width),
                                   interpolation=cv2.INTER_CUBIC)  # Resize and interpolate
            cv2.imshow('object detection_left', roi_left)
        return self.classifier.predict(roi_left_prepared)

    def get_number_right(self, image, player_stream='P11'):
        if player_stream == 'P11':
            roi_right = image[pos_y1_P11:pos_y2_P11, pos_right_x1_P11:pos_right_x2_P11]
        else:
            roi_right = image[pos_y1_Pn:pos_y2_Pn, pos_right_x1_Pn:pos_right_x2_Pn]

        roi_right_prepared = prepare_for_classifier(roi_right)

        if debug:
            roi_right = cv2.cvtColor(roi_right, cv2.COLOR_BGR2GRAY)  # convert Image to grayscale
            roi_right = cv2.resize(roi_right, dsize=(image_width, image_width),
                               interpolation=cv2.INTER_CUBIC)  # Resize and interpolate
            cv2.imshow('object detection_right', roi_right)
        return self.classifier.predict(roi_right_prepared)
