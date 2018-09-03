import cv2
import numpy as np
import tensorflow as tf
from tensorflow import keras

video_path = 'D:/gamestory18-data/train_set'
model_path = "training/mnist/cnn.h5"
model = keras.models.load_model(model_path)


def get_round_begin(start_pos_in_video_sec, end_pos_in_video_sec, video_full_name, target_round_left,
                    target_round_right):
    cap = cv2.VideoCapture(video_path + '/' + '2018-03-02_P11.mp4')
    fps = cap.get(cv2.CAP_PROP_FPS)
    nr_of_frames = 0

    frame_pos_start = int(start_pos_in_video_sec * fps)
    frame_pos_end = int(end_pos_in_video_sec * fps)

    current_frame = frame_pos_start
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos_start)

    while current_frame <= frame_pos_end:
        ret, image_np = cap.read()
        current_frame += 1
        nr_of_frames += 1

        # pos_msec = cap.get(cv2.CAP_PROP_POS_MSEC)

        # convert Image to grayscale
        image_gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)

        # Region of interest for left and right round number
        roi_left = image_gray[10:26, 274:290]
        roi_right = image_gray[10:26, 347:363]

        # Resize for MNIST model
        roi_left = cv2.resize(roi_left, dsize=(28, 28), interpolation=cv2.INTER_CUBIC)
        roi_right = cv2.resize(roi_right, dsize=(28, 28), interpolation=cv2.INTER_CUBIC)

        # Binarize roi
        roi_left = cv2.threshold(roi_left, 0, 255,
                                 cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

        roi_right = cv2.threshold(roi_right, 0, 255,
                                  cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

        # reshape array for model use
        roi_left_expanded = roi_left.reshape(1, 28, 28, 1)
        roi_left_expanded = roi_left_expanded.astype('float32')
        roi_left_expanded /= 255

        roi_right_expanded = roi_right.reshape(1, 28, 28, 1)
        roi_right_expanded = roi_right_expanded.astype('float32')
        roi_right_expanded /= 255


        out_left = model.predict(roi_left_expanded)
        out_right = model.predict(roi_right_expanded)


        print("Left: " + str(np.argmax(out_left)))
        print("Right: " + str(np.argmax(out_right)))


        cv2.imshow('object detection_left', roi_left)
        cv2.imshow('object detection_right', roi_right)
        cv2.imshow('object detection', image_np)

        if cv2.waitKey(25) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break
