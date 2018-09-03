import cv2
import numpy as np

def binarize(roi):
    return cv2.threshold(roi, 0, 255,
                         cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

video_path = 'D:/gamestory18-data/train_set/2018-03-02_P11.mp4'
start_pos_in_video_sec = 4460
end_pos_in_video_sec = 5000
roi_terrorists = []
roi_ct = []


cap = cv2.VideoCapture(video_path)
fps = cap.get(cv2.CAP_PROP_FPS)
nr_of_frames = 0

frame_pos_start = int(start_pos_in_video_sec * fps)
frame_pos_end = int(end_pos_in_video_sec * fps)

current_frame = frame_pos_start
cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos_start)

skull = cv2.imread('images/skull/skull.png', 0)
norm_threshold = 3000
print(skull)


while current_frame <= frame_pos_end:
    ret, image_np = cap.read()

    current_frame += 1
    nr_of_frames += 1

    image_gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
    cv2.imshow('kill', image_np)

    roi_0 = image_gray[239:255, 16:29]
    roi_1 = image_gray[262:278, 16:29]
    roi_2 = image_gray[285:301, 16:29]
    roi_3 = image_gray[307:323, 16:29]
    roi_4 = image_gray[330:346, 16:29]

    roi_5 = image_gray[239:255, 611:624]
    roi_6 = image_gray[262:278, 611:624]
    roi_7 = image_gray[285:301, 611:624]
    roi_8 = image_gray[307:323, 611:624]
    roi_9 = image_gray[330:346, 611:624]

    roi_0_bin = binarize(roi_0)
    roi_1_bin = binarize(roi_1)
    roi_2_bin = binarize(roi_2)
    roi_3_bin = binarize(roi_3)
    roi_4_bin = binarize(roi_4)
    roi_5_bin = binarize(roi_5)
    roi_6_bin = binarize(roi_6)
    roi_7_bin = binarize(roi_7)
    roi_8_bin = binarize(roi_8)
    roi_9_bin = binarize(roi_9)


    norm = np.linalg.norm(skull.ravel() - roi_6_bin.ravel(), ord=1) # ravel converts 2d into 1d array

    cv2.imshow('roi_0', roi_0_bin)
    cv2.imshow('roi_1', roi_1_bin)
    cv2.imshow('roi_2', roi_2_bin)
    cv2.imshow('roi_3', roi_3_bin)
    cv2.imshow('roi_4', roi_4_bin)
    cv2.imshow('roi_5', roi_5_bin)
    cv2.imshow('roi_6', roi_6_bin)
    cv2.imshow('roi_7', roi_7_bin)
    cv2.imshow('roi_8', roi_8_bin)
    cv2.imshow('roi_9', roi_9_bin)



    if cv2.waitKey(25) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break