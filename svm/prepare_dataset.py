import cv2
import os
import numpy as np
import logging
from sklearn.model_selection import train_test_split
from sklearn import datasets, svm, metrics

video_path = 'D:/gamestory18-data/train_set/2018-03-02_P11.mp4'
dest_path = 'images'

image_width = 28
nr_of_samples = image_width * image_width
pos_y1 = 10
pos_y2 = 26

pos_single_left_x1 = 274
pos_single_left_x2 = 290

search_duration = 20
nr_of_frames_to_extract = 500
begin_timestamps = ['1:05:55', '1:06:41', '1:08:52', '1:09:37', '1:11:25', '1:12:26', '1:16:50', '1:18:24', '1:20:57', '1:22:56']

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

def preprocess_and_extract_roi(image):
    """Preprocesses and extracts the left roi

    Args:
        image: Input image

    Returns:
        the preprocessed roi where the left round number is shown

    """
    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    roi = image_gray[pos_y1:pos_y2, pos_single_left_x1:pos_single_left_x2]
    roi = cv2.resize(roi, dsize=(image_width, image_width), interpolation=cv2.INTER_CUBIC)
    roi = cv2.threshold(roi, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    return roi

def extract_images():
    """
        extracts the images for svm training set
        NOTE: images should be inspected manually for detecting outliers
    """
    logging.info("Starting extraction of training images for svm (number detection)")
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)

    # extract images from video for 0-9
    for i in range(0, 10):
        if not os.path.exists(dest_path + '/' + str(i)):
            os.makedirs(dest_path + '/' + str(i))

        begin_sec = timestamp_to_sec(begin_timestamps[i])
        frame_pos_start = int(begin_sec * fps)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos_start)

        for j in range(0, nr_of_frames_to_extract):
            ret, image_np = cap.read()
            roi_left = preprocess_and_extract_roi(image_np)
            cv2.imwrite('images/' + str(i) + '/' + str(j) + '.png', roi_left)


def load_dataset():
    """
        loads the training dataset
     Returns:
        training dataset
    """
    if not os.path.exists(dest_path):
        extract_images()
    else:

        all_images_data = []
        all_images_target = []

        for i in range(0, 10):
            current_dest_path = os.getcwd() + '/' + dest_path + '/' + str(i) + '/'
            files = [f for f in os.listdir(current_dest_path) if os.path.isfile(os.path.join(current_dest_path, f))]

            nr_of_files = len(files)

            array_for_data = np.empty((nr_of_files, nr_of_samples))
            array_for_target = np.empty(nr_of_files)

            for j in range(0, nr_of_files):
                # load every image, reshape it and store in single array
                image = cv2.imread(os.path.join(current_dest_path + files[i]), 0)
                image = image.reshape(nr_of_samples)

                array_for_data[j] = image
                array_for_target[j] = i # store corresponding label

            all_images_data.append(array_for_data)
            all_images_target.append(array_for_target)

        # At this point all data is in all_images_data and all_images_target
        # merge data together
        target_array_size = 0
        for image_targets in all_images_target:
            target_array_size += image_targets.size

        data = np.concatenate([image for image in all_images_data])
        target = np.concatenate([target for target in all_images_target])

        dataset = {'target_names': np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9]), 'data': data, 'target': target}
        return dataset

dataset = load_dataset()

X_train, X_test, y_train, y_test = train_test_split(dataset['data'], dataset['target'])

print('Training data and target sizes: \n{}, {}'.format(X_train.shape,y_train.shape))
print('Test data and target sizes: \n{}, {}'.format(X_test.shape,y_test.shape))

# Create a classifier: a support vector classifier
classifier = svm.SVC(gamma=0.001)
#fit to the trainin data
classifier.fit(X_train, y_train)

# now to Now predict the value of the digit on the test data
y_pred = classifier.predict(X_test)

print("Classification report for classifier %s:\n%s\n"
      % (classifier, metrics.classification_report(y_test, y_pred)))

print("Confusion matrix:\n%s" % metrics.confusion_matrix(y_test, y_pred))

