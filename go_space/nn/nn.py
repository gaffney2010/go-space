import os

from keras.callbacks import Callback, ModelCheckpoint
from keras.layers.convolutional import Conv2D, ZeroPadding2D
from keras.layers.core import Activation, Dense, Flatten
from keras.models import Sequential
from tensorflow.keras.optimizers import Adagrad

from go_space import consts
from go_space.nn import data_manager


def layers():
    return [
        ZeroPadding2D(padding=2, data_format="channels_last"),
        Conv2D(24, (5, 5), data_format="channels_last"),
        Activation("relu"),
        # ZeroPadding2D(padding=2, data_format='channels_last'),
        # Conv2D(48, (5, 5), data_format='channels_last'),
        # Activation('relu'),
        ZeroPadding2D(padding=1, data_format="channels_last"),
        Conv2D(12, (3, 3), data_format="channels_last"),
        Activation("relu"),
        Flatten(),
        Dense(64),
        Activation("relu"),
        Dense(16, activation="softmax"),
    ]


data_reader = data_manager.DataManager(
    os.path.join(consts.TOP_LEVEL_PATH, "data", "_processed_data")
)
data_reader.train_test_split(0.2)


class ResetDataReader(Callback):
    """Does some dumb end-of-epoch work."""

    def on_epoch_end(self, epoch, logs=None):
        # TODO: Can I avoid the global here?
        global data_reader
        data_reader.reset()


model = Sequential()
for layer in layers():
    model.add(layer)
model.compile(
    loss="categorical_crossentropy",
    optimizer=Adagrad(),
    metrics=["accuracy"],
)

print("ABOUT TO START")

BATCH_SIZE = 256

model.fit_generator(
    generator=data_reader.generate_batches(BATCH_SIZE, data_manager.TrainTest.TRAIN),
    epochs=20,
    # TODO: Fix off-by-a-few error.  It may not actually be there.
    steps_per_epoch=40000 * 0.8 // BATCH_SIZE - 5,
    validation_data=data_reader.generate_batches(128, data_manager.TrainTest.TEST),
    validation_steps=40000 * 0.2 // BATCH_SIZE - 5,
    callbacks=[
        # ModelCheckpoint(os.path.join(consts.TOP_LEVEL_PATH, "data", "checkpoints", "epoch_{epoch}.h5")),
        ResetDataReader(),
    ],
)

data_reader.reset()
print("=============")
print("FINAL METRICS")
print(
    model.evaluate_generator(
        generator=data_reader.generate_batches(128, data_manager.TrainTest.TEST),
        steps=40000 * 0.2 // BATCH_SIZE - 5,
    )
)

model.save(os.path.join(consts.TOP_LEVEL_PATH, "saved_models", "v1"))
