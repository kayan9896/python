import numpy as np
from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

#Load the digits dataset
digits = datasets.load_digits()
X = digits.data
y = digits.target

#Split the data into training and validation sets
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

#Define the activation functions
def sigmoid(x):
    # Prevent overflow by clipping the input
    x = np.clip(x, -500, 500)
    return 1 / (1 + np.exp(-x))

def softmax(x):
    x = np.clip(x, -500, 500)
    return np.exp(x) / np.sum(np.exp(x), axis=1, keepdims=True)

#Define the learning rates and epochs to try
learning_rates = [0.1, 0.01, 0.001, 0.0001, 0.00001]
epochs = [50, 100, 200]

#Initialize the best accuracy and the corresponding hyperparameters
best_accuracy = 0
best_learning_rate = None
best_epoch = None

#Perform the grid search
for learning_rate in learning_rates:
    for epoch in epochs:
        # Initialize the weights and biases for the layers
        np.random.seed(42)
        weights1 = np.random.rand(64, 32)
        bias1 = np.zeros((32,))
        weights2 = np.random.rand(32, 16)
        bias2 = np.zeros((16,))
        weights3 = np.random.rand(16, 10)
        bias3 = np.zeros((10,))

    # Train the network
    for _ in range(epoch):
        # Forward pass
        hidden_layer1 = sigmoid(np.dot(X_train, weights1) + bias1)
        hidden_layer2 = sigmoid(np.dot(hidden_layer1, weights2) + bias2)
        output_layer = softmax(np.dot(hidden_layer2, weights3) + bias3)

        # Backward pass
        output_error_grad = output_layer - np.eye(10)[y_train]
        hidden_error_grad2 = output_error_grad.dot(weights3.T) * hidden_layer2 * (1 - hidden_layer2)
        hidden_error_grad1 = hidden_error_grad2.dot(weights2.T) * hidden_layer1 * (1 - hidden_layer1)

        # Weight updates
        weights3 -= learning_rate * hidden_layer2.T.dot(output_error_grad)
        bias3 -= learning_rate * output_error_grad.mean(axis=0)
        weights2 -= learning_rate * hidden_layer1.T.dot(hidden_error_grad2)
        bias2 -= learning_rate * hidden_error_grad2.mean(axis=0)
        weights1 -= learning_rate * X_train.T.dot(hidden_error_grad1)
        bias1 -= learning_rate * hidden_error_grad1.mean(axis=0)

    # Evaluate the network on the validation set
    hidden_layer1 = sigmoid(np.dot(X_val, weights1) + bias1)
    hidden_layer2 = sigmoid(np.dot(hidden_layer1, weights2) + bias2)
    output_layer = softmax(np.dot(hidden_layer2, weights3) + bias3)
    predictions = np.argmax(output_layer, axis=1)
    accuracy = accuracy_score(y_val, predictions)

    # Update the best accuracy and the corresponding hyperparameters
    if accuracy > best_accuracy:
        best_accuracy = accuracy
        best_learning_rate = learning_rate
        best_epoch = epoch
#Print the best accuracy and the corresponding hyperparameters
print("Best accuracy:", best_accuracy)
print("Best learning rate:", best_learning_rate)
print("Best epoch:", best_epoch)

int randomLevel() {
    int level = 1;
    while ((rand() % (1 << level)) == 0 && level < MAX_LEVEL) {
        level++;
    }
    return level;
}
