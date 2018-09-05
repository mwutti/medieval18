import tensorflow as tf
from tensorflow import keras

mnist = tf.keras.datasets.mnist

TRAINING_DIR = 'training'
DATA_DIR = 'data'
LABEL_MAP = 'mscoco_label_map.pbtxt'
MODEL_NAME = 'mnist'

# model_path = "training/mnist/mnist.h5"
model_path = "training/mnist/cnn.h5"
# Path to frozen detection graph. This is the actual model that is used for the object detection.
PATH_TO_CKPT = TRAINING_DIR + '/' + MODEL_NAME + '/frozen_inference_graph.pb'

# List of the strings that is used to add correct label for each box.
PATH_TO_LABELS = TRAINING_DIR + '/' + MODEL_NAME + '/' + LABEL_MAP

NUM_CLASSES = 90
max_boxes_to_draw = 20
class_map = []
detector_labels = ['person', 'vase', 'cup', 'wine glass']

(train_images, train_labels), (test_images, test_labels) = tf.keras.datasets.mnist.load_data()

train_labels = train_labels[:1000]
test_labels = test_labels[:1000]

train_images = train_images[:1000].reshape(-1, 28 * 28) / 255.0
test_images = test_images[:1000].reshape(-1, 28 * 28) / 255.0

# load model and evaluate
model = keras.models.load_model(model_path)
loss, acc = model.evaluate(test_images, test_labels)

model.summary()

print("Restored model, accuracy: {:5.2f}%".format(100 * acc))


def predict(img):
    return model.predict(img)
