import cv2
import numpy as np
import logging as logger
import svm.number_classifier as svm

debug = False
logger.basicConfig(format='%(levelname)s: %(asctime)s %(message)s', level=logger.DEBUG)
correct_threshold = 94.0
shift_begin_sec = 10


classifier = svm.NumberClassifier()
classifier.train_classifier()

cap = cv2.VideoCapture(svm.video_path)
fps = cap.get(cv2.CAP_PROP_FPS)

# extract images from video for 0-9
for i in range(0, len(svm.begin_timestamps)):
    logger.info("Starting number classifier test for label: " + str(i))
    correct_predicted = 0
    begin_sec = svm.timestamp_to_sec(svm.begin_timestamps[i]) + shift_begin_sec
    frame_pos_start = int(begin_sec * fps)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos_start)

    for j in range(0, svm.nr_of_frames_to_extract):
        ret, image_np = cap.read()
        roi_left = svm.preprocess_and_extract_roi(image_np, left=(i != 21))
        roi_left = np.divide(roi_left, 255)
        predict = classifier.predict(roi_left.reshape((1, -1)))

        if int(predict) == i:
            correct_predicted += 1

        if debug:
            cv2.imshow('number_left', image_np)
            cv2.imshow('roi_left', roi_left)
            if cv2.waitKey(25) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break

    percentage_correct = (correct_predicted / svm.nr_of_frames_to_extract) * 100
    if percentage_correct >= correct_threshold:
        logger.info('Correct classified for label ' + str(i) + ': ' + str(percentage_correct) + "%")
    else:
        logger.warning('Correct classified for label ' + str(i) + ': ' + str(percentage_correct) + "%")
