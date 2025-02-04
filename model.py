import os

import matplotlib.pyplot as plt
import pandas as pd
import tensorflow as tf
from keras.preprocessing.text import Tokenizer
from tensorflow import keras

from utils import save_embeddings
from visualization import plot_loss, plot_accuracy


def execute(sentence, save_word_embeddings=False, plot_loss_acc=False):
    """Returns the sentiment of the parsed sentence.

    Args:
        sentence (str) : The sentence to be analised.
        save_word_embeddings (bool) : If true, will save the embedding data.
        plot_loss_acc (bool) : If true, will plot the loss and accuracy during the training of the data.

    Returns
        score (float) : The sentiment score of the sentence. 1 - cyber abusive, 0 - not cyber abusive.
    """

    parsed_test = pd.DataFrame({"content": pd.Series(sentence)})

    current_directory = os.getcwd()
    train_data = pd.read_csv(current_directory + "/data/DataTurks/dump.csv")
    train_data = train_data.sample(frac=1).reset_index(drop=True)

    X_train = train_data['content'][:18000]
    X_test = parsed_test['content']

    y_train = train_data['label'][:18000]

    tokenizer = Tokenizer(num_words=10000)
    tokenizer.fit_on_texts(train_data['content'])

    train_sequences = tokenizer.texts_to_sequences(X_train.values)
    test_sequences = tokenizer.texts_to_sequences(X_test.values)

    vocab_size = 10000

    padded_train = keras.preprocessing.sequence.pad_sequences(train_sequences, padding='post',
                                                              maxlen=140)
    padded_test = keras.preprocessing.sequence.pad_sequences(test_sequences, padding='post',
                                                             maxlen=140)
    model = keras.Sequential()
    model.add(keras.layers.Embedding(vocab_size, 40))
    model.add(keras.layers.GlobalAveragePooling1D())
    model.add(keras.layers.Dense(4, activation=tf.nn.relu))
    model.add(keras.layers.Dense(1, activation=tf.nn.sigmoid))

    model.summary()

    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['acc'])

    split = int(len(X_train) / 4)  # number of comments halved

    x_val = padded_train[:split]
    partial_x_train = padded_train[split:]

    y_val = y_train[:split]
    partial_y_train = y_train[split:]

    history = model.fit(partial_x_train, partial_y_train, epochs=120, batch_size=512, validation_data=(x_val, y_val),
                        verbose=1)

    if save_word_embeddings == True:
        word_index = tokenizer.word_index
        save_embeddings(model, word_index)

    if plot_loss_acc == True:
        history_dict = history.history
        history_dict.keys()

        epochs = range(1, len(history_dict['acc']) + 1)

        plot_accuracy(epochs, history_dict['acc'], history_dict['val_acc'])
        plt.clf()
        plot_loss(epochs, history_dict['loss'], history_dict['val_loss'])


    sentiment_score = model.predict(padded_test)

    return str(sentiment_score[0][0])

print(execute("You are a bitch"))