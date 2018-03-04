import pandas as pd
import tensorflow as tf
import os

FILE = os.path.abspath(os.path.dirname(__file__))
TRAIN_PATH = '{0}/{1}'.format(FILE,'data_ignore/training.csv')
TEST_PATH = '{0}/{1}'.format(FILE,'data_ignore/test.csv')

def load_data():
    '''Parse train and test CSV'''
    # Use panda to read both CSVs and store it in a [DataFrame](https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.html).
    train = pd.read_csv(filepath_or_buffer=TRAIN_PATH);
    test = pd.read_csv(filepath_or_buffer=TEST_PATH);

    # Remove the 'id' column from both datasets.
    train.pop(train.columns[0])
    test.pop(test.columns[0])

    # Each set divides in two pieces: ft, or feature, contains the relevant data to use and label wich contains the classification.
    train_ft, train_label = train, train.pop(train.columns[-1])
    test_ft, test_label = test, test.pop(test.columns[-1])

    return (train_ft, train_label), (test_ft, test_label)

def train_input_fn(features, labels, batch_size):
    """An input function for training"""
    # Convert the inputs to a Dataset.
    dataset = tf.data.Dataset.from_tensor_slices((dict(features), labels))

    # Shuffle, repeat, and batch the examples.
    dataset = dataset.shuffle(1000).repeat().batch(batch_size)

    # Return the dataset.
    return dataset

def eval_input_fn(features, labels, batch_size):
    """An input function for evaluation or prediction"""
    features=dict(features)
    if labels is None:
        # No labels, use only features.
        inputs = features
    else:
        inputs = (features, labels)

    # Convert the inputs to a Dataset.
    dataset = tf.data.Dataset.from_tensor_slices(inputs)

    # Batch the examples
    assert batch_size is not None, "batch_size must not be None"
    dataset = dataset.batch(batch_size)

    # Return the dataset.
    return dataset
