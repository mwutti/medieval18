import tensorflow as tf
from tensorflow import keras
import os

(train_images, train_labels), (test_images, test_labels) = tf.keras.datasets.mnist.load_data()

train_labels = train_labels[:1000]
test_labels = test_labels[:1000]

train_images = train_images[:1000].reshape(-1, 28 * 28) / 255.0
test_images = test_images[:1000].reshape(-1, 28 * 28) / 255.0

# checkpoint_path = "training/mnist/cp-{epoch:04d}.ckpt"
checkpoint_path = "training/mnist/mnist.h5"
checkpoint_dir = os.path.dirname(checkpoint_path)


def create_model():
    model = tf.keras.models.Sequential([
        keras.layers.Dense(512, activation=tf.nn.relu, input_shape=(784,)),
        keras.layers.Dropout(0.2),
        keras.layers.Dense(10, activation=tf.nn.softmax)
    ])

    model.compile(optimizer=tf.keras.optimizers.Adam(),
                  loss=tf.keras.losses.sparse_categorical_crossentropy,
                  metrics=['accuracy'])

    return model

model = create_model()

model.fit(train_images, train_labels,  epochs = 100,
          validation_data = (test_images,test_labels))

loss, acc = model.evaluate(test_images, test_labels)

model.summary()
model.save(checkpoint_path)

print("model, accuracy: {:5.2f}%".format(100 * acc))