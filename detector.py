import os

import cv2
import label_map_util
import numpy as np
import tensorflow as tf
video_url = 'D:\gamestory18-data/train_set/2018-03-04_P11.mp4'
# video_url = 'video/p11_cut.mp4'
cap = cv2.VideoCapture(video_url)
fps = cap.get(cv2.CAP_PROP_FPS)

#jump to 8:20 in video
frame_pos = 30000*60
cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)

TRAINING_DIR = 'training'
DATA_DIR = 'data'
LABEL_MAP = 'mscoco_label_map.pbtxt'
MODEL_NAME = 'coco'

# Path to frozen detection graph. This is the actual model that is used for the object detection.
PATH_TO_CKPT = TRAINING_DIR + '/' + MODEL_NAME + '/frozen_inference_graph.pb'

# List of the strings that is used to add correct label for each box.
PATH_TO_LABELS = TRAINING_DIR + '/' + MODEL_NAME + '/' + LABEL_MAP

NUM_CLASSES = 90

# ## Load a (frozen) Tensorflow model into memory.

detection_graph = tf.Graph()
with detection_graph.as_default():
    od_graph_def = tf.GraphDef()
    with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')

# ## Loading label map
# Label maps map indices to category names, so that when our convolution network predicts `5`, we know that this corresponds to `airplane`.  Here we use internal utility functions, but anything that returns a dictionary mapping integers to appropriate string labels would be fine

label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES,
                                                            use_display_name=True)
category_index = label_map_util.create_category_index(categories)

with detection_graph.as_default():
    with tf.Session(graph=detection_graph) as sess:
        while True:
            ret, image_np = cap.read()
            pos_msec = cap.get(cv2.CAP_PROP_POS_MSEC)

            # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
            image_np_expanded = np.expand_dims(image_np, axis=0)
            image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
            # Each box represents a part of the image where a particular object was detected.
            boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
            # Each score represent how level of confidence for each of the objects.
            # Score is shown on the result image, together with the class label.
            scores = detection_graph.get_tensor_by_name('detection_scores:0')
            classes = detection_graph.get_tensor_by_name('detection_classes:0')
            num_detections = detection_graph.get_tensor_by_name('num_detections:0')
            # Actual detection.
            (boxes, scores, classes, num_detections) = sess.run(
                [boxes, scores, classes, num_detections],
                feed_dict={image_tensor: image_np_expanded})

            # Visualization of the results of a detection.
            # vis_util.visualize_boxes_and_labels_on_image_array(
            #     image_np,
            #     np.squeeze(boxes),
            #     np.squeeze(classes).astype(np.int32),
            #     np.squeeze(scores),
            #     category_index,
            #     use_normalized_coordinates=True,
            #     line_thickness=8)

            #detect cups and trophies
            min_score_thresh = .5
            scores = np.squeeze(scores)
            classes = np.squeeze(classes).astype(np.int32)
            for i in range(boxes.shape[0]):
                if scores is None or scores[i] > min_score_thresh:
                    display_str = ''
                    # if not skip_labels:
                    if classes[i] in category_index.keys():
                        class_name = category_index[classes[i]]['name']
                        print(class_name + '@ ' + str(pos_msec))
                    else:
                        class_name = 'N/A'
                    display_str = str(class_name)

            cv2.imshow('object detection', cv2.resize(image_np, (800, 600)))
            if cv2.waitKey(25) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break
