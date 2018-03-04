import tensorflow as tf
import data as d

BATCH_SIZE = 500
STEPS = 10000

def main():
    # Load data from CSV files.
    (train_ft, train_label), (test_ft, test_label) = d.load_data()

    # Create feature columns to describe input usage.
    my_feature_columns = []
    for key in train_ft.keys():
        my_feature_columns.append(tf.feature_column.numeric_column(key=key))

    # Build 2 hidden layer DNN with 10, 10 units respectively.
    classifier = tf.estimator.DNNClassifier(
        feature_columns=my_feature_columns,
        # Two hidden layers of 10 nodes each.
        hidden_units=[10, 10],
        # The model must choose between 3 classes.
        n_classes=2)
    # Train the Model.
    classifier.train(input_fn=lambda:d.train_input_fn(train_ft, train_label, BATCH_SIZE), steps=STEPS)

    # Evaluate the model.
    eval_result = classifier.evaluate(input_fn=lambda:d.eval_input_fn(test_ft, test_label, BATCH_SIZE))

    print('\nTest set accuracy: {accuracy:0.3f}\n'.format(**eval_result))

main()