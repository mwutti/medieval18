import cv2
import os
import numpy as np
import logging as logger
from sklearn.model_selection import train_test_split
from sklearn import svm, metrics

debug = False
video_path = 'D:/gamestory18-data/train_set/2018-03-02_P11.mp4'
dest_path = "D:/gamestory18-data/svm_training_images"

image_width = 28
nr_of_samples = image_width * image_width
pos_y1 = 10
pos_y2 = 26

pos_single_left_x1 = 274
pos_single_left_x2 = 290

pos_single_right_x1 = 349
pos_single_right_x2 = 365

search_duration = 20
nr_of_frames_to_extract = 500

begin_timestamps = ['1:05:55',  # 0
                    '1:06:41',  # 1
                    '1:08:52',  # 2
                    '1:09:37',  # 3
                    '1:11:25',  # 4
                    '1:12:26',  # 5
                    '1:16:50',  # 6
                    '1:18:24',  # 7
                    '1:20:57',  # 8
                    '1:22:56',  # 9
                    '4:06:30',  # 10
                    '4:09:10',  # 11
                    '4:12:00',  # 12
                    '4:17:30',  # 13
                    '4:23:10',  # 14
                    '4:44:00',  # 15
                    '4:46:30',  # 16
                    '4:49:20',  # 17
                    '4:53:10',  # 18
                    '5:09:10',  # 19
                    '5:11:40',  # 20
                    '5:11:40']  # 21 on the right side

verify_timestamp = '3:39:50'

def prepare_for_classifier(image):
    # image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # convert Image to grayscale
    image = cv2.resize(image, dsize=(image_width, image_width), interpolation=cv2.INTER_CUBIC)  # Resize and interpolate
    image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]  # binarize it
    image = image.reshape(1, -1)  # and reshape

    return image

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


def preprocess_and_extract_roi(image, left=True):
    """Preprocesses and extracts the left roi

    Args:
        image: Input image
        left: extract from left side

    Returns:
        the preprocessed roi where the left/right round number is shown

    """
    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    if left:
        roi = image_gray[pos_y1:pos_y2, pos_single_left_x1:pos_single_left_x2]
    else:
        roi = image_gray[pos_y1:pos_y2, pos_single_right_x1:pos_single_right_x2]

    roi = cv2.resize(roi, dsize=(image_width, image_width), interpolation=cv2.INTER_CUBIC)
    roi = cv2.threshold(roi, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    return roi


def extract_images():
    """
        extracts the images for svm training set
        NOTE: images should be inspected manually for detecting outliers
    """
    logger.info("Starting extraction of training images for svm (number detection)")
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)

    # extract images from video for 0-9
    for i in range(0, len(begin_timestamps)):
        if not os.path.exists(dest_path + '/' + str(i)):
            os.makedirs(dest_path + '/' + str(i))

        begin_sec = timestamp_to_sec(begin_timestamps[i])
        frame_pos_start = int(begin_sec * fps)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos_start)

        for j in range(0, nr_of_frames_to_extract):
            ret, image_np = cap.read()
            roi_left = preprocess_and_extract_roi(image_np, left=(i != 21))
            cv2.imwrite(dest_path + '/' + str(i) + '/' + str(j) + '.png', roi_left)


class NumberClassifier:
    def __init__(self):
        self.dataset = None
        self.classifier = svm.SVC(gamma=0.001)

    def load_dataset(self):
        """
            loads the training dataset
         Returns:
            training dataset
        """
        logger.info("Load dataset for training")
        if not os.path.exists(dest_path):
            extract_images()

        all_images_data = []
        all_images_target = []

        for i in range(0, len(begin_timestamps)):
            current_dest_path = dest_path + '/' + str(i) + '/'
            files = [f for f in os.listdir(current_dest_path) if os.path.isfile(os.path.join(current_dest_path, f))]

            nr_of_files = len(files)

            array_for_data = np.empty((nr_of_files, nr_of_samples))
            array_for_target = np.empty(nr_of_files)

            for j in range(0, nr_of_files):
                # load every image, reshape it and store in single array
                image = cv2.imread(os.path.join(current_dest_path + files[i]), 0)
                image = np.divide(image, 255)
                image = image.reshape(nr_of_samples)

                array_for_data[j] = image
                array_for_target[j] = i  # store corresponding label

            all_images_data.append(array_for_data)
            all_images_target.append(array_for_target)

        # At this point all data is in all_images_data and all_images_target
        # merge data together
        target_array_size = 0
        for image_targets in all_images_target:
            target_array_size += image_targets.size

        data = np.concatenate([image for image in all_images_data])
        target = np.concatenate([target for target in all_images_target])

        self.dataset = {'target_names': np.array([i for i in range(0, len(begin_timestamps))], dtype=np.int8),
                        'data': data, 'target': target}
        return self.dataset

    def train_classifier(self):
        self.load_dataset()

        logger.info("Start training classifier")
        X_train, X_test, y_train, y_test = train_test_split(self.dataset['data'], self.dataset['target'], test_size=0.4, random_state=0)
        self.classifier.fit(X_train, y_train)
        y_pred = self.classifier.predict(X_test)

        if debug:
            print('Training data and target sizes: \n{}, {}'.format(X_train.shape, y_train.shape))
            print('Test data and target sizes: \n{}, {}'.format(X_test.shape, y_test.shape))
            print("Classification report for classifier %s:\n%s\n"
                  % (self.classifier, metrics.classification_report(y_test, y_pred)))
            print("Confusion matrix:\n%s" % metrics.confusion_matrix(y_test, y_pred))

    def predict(self, image):
        return self.classifier.predict(image)[0]



