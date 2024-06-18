import numpy as np
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

# Sigmoid function
def sigmoid(x):
    return 1 / (1 + np.exp(-x))

# Derivative of sigmoid function
def sigmoid_derivative(x):
    return x * (1 - x)

# Softmax function
def softmax(x):
    x_max = np.max(x, axis=1, keepdims=True)
    x_exp = np.exp(x - x_max)
    return x_exp / np.sum(x_exp, axis=1, keepdims=True)

class NeuralNet:
    def __init__(self, input_size, hidden1_size, hidden2_size, output_size):
        """
        Initialize the neural network with the given layer sizes.

        Parameters:
        input_size (int): The number of neurons in the input layer.
        hidden1_size (int): The number of neurons in the first hidden layer.
        hidden2_size (int): The number of neurons in the second hidden layer.
        output_size (int): The number of neurons in the output layer.
        """
        self.weights1 = np.random.rand(input_size, hidden1_size)
        self.weights2 = np.random.rand(hidden1_size, hidden2_size)
        self.weights3 = np.random.rand(hidden2_size, output_size)

        self.mean1 = np.zeros((hidden1_size,))
        self.std1 = np.ones((hidden1_size,))
        self.mean2 = np.zeros((hidden2_size,))
        self.std2 = np.ones((hidden2_size,))

        self.beta1 = 0.9
        self.beta2 = 0.999
        self.epsilon = 1e-8
        self.m1 = np.zeros((input_size, hidden1_size))
        self.v1 = np.zeros((input_size, hidden1_size))
        self.m2 = np.zeros((hidden1_size, hidden2_size))
        self.v2 = np.zeros((hidden1_size, hidden2_size))
        self.m3 = np.zeros((hidden2_size, output_size))
        self.v3 = np.zeros((hidden2_size, output_size))

    def forward(self, X):
        """
        Perform a forward pass through the neural network.

        Parameters:
        X (numpy array): The input to the neural network.

        Returns:
        numpy array: The output of the neural network.
        """
        self.layer1 = sigmoid(self.batch_normalize(np.dot(X, self.weights1), self.mean1, self.std1))
        self.layer2 = sigmoid(self.batch_normalize(np.dot(self.layer1, self.weights2), self.mean2, self.std2))
        self.output = softmax(np.dot(self.layer2, self.weights3))
        return self.output

    def backward(self, X, y, output):
        """
        Perform a backward pass through the neural network to compute the gradients.

        Parameters:
        X (numpy array): The input to the neural network.
        y (numpy array): The true labels.
        output (numpy array): The predicted labels.

        Returns:
        numpy array, numpy array, numpy array: The gradients of the loss with respect to the weights.
        """
        d_output = 2 * (output - y)
        d_weights3 = np.dot(self.layer2.T, d_output)
        d_layer2 = np.dot(d_output, self.weights3.T) * sigmoid_derivative(self.layer2)
        d_weights2 = np.dot(self.layer1.T, d_layer2)
        d_layer1 = np.dot(d_layer2, self.weights2.T) * sigmoid_derivative(self.layer1)
        d_weights1 = np.dot(X.T, d_layer1)

        return d_weights1, d_weights2, d_weights3

    def update_weights(self, d_weights1, d_weights2, d_weights3, learning_rate, t):
        """
        Update the weights of the neural network using the gradients and the learning rate.

        Parameters:
        d_weights1 (numpy array): The gradient of the loss with respect to the first set of weights.
        d_weights2 (numpy array): The gradient of the loss with respect to the second set of weights.
        d_weights3 (numpy array): The gradient of the loss with respect to the third set of weights.
        learning_rate (float): The learning rate of the neural network.
        t (int): The current iteration.
        """
        self.m1 = self.beta1 * self.m1 + (1 - self.beta1) * d_weights1
        self.v1 = self.beta2 * self.v1 + (1 - self.beta2) * d_weights1 ** 2
        self.weights1 -= learning_rate * self.m1 / (np.sqrt(self.v1) + self.epsilon)

        self.m2 = self.beta1 * self.m2 + (1 - self.beta1) * d_weights2
        self.v2 = self.beta2 * self.v2 + (1 - self.beta2) * d_weights2 ** 2
        self.weights2 -= learning_rate * self.m2 / (np.sqrt(self.v2) + self.epsilon)

        self.m3 = self.beta1 * self.m3 + (1 - self.beta1) * d_weights3
        self.v3 = self.beta2 * self.v3 + (1 - self.beta2) * d_weights3 ** 2
        self.weights3 -= learning_rate * self.m3 / (np.sqrt(self.v3) + self.epsilon)

    def batch_normalize(self, x, mean, std):
        """
        Normalize the input to a layer using batch normalization.

        Parameters:
        x (numpy array): The input to the layer.
        mean (numpy array): The mean of the input.
        std (numpy array): The standard deviation of the input.

        Returns:
        numpy array: The normalized input.
        """
        mean = 0.9 * mean + 0.1 * np.mean(x, axis=0)
        std = 0.9 * std + 0.1 * np.std(x, axis=0)
        return (x - mean) / (std + 1e-8)

# Load MNIST dataset
digits = load_digits()
X = digits.data
y = np.zeros((len(digits.target), 10))
for i, target in enumerate(digits.target):
    y[i, target] = 1

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Standardize data
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Initialize neural network
nn = NeuralNet(64, 256, 128, 10)

# Train neural network
learning_rate = 0.01
for epoch in range(10000):
    output = nn.forward(X_train)
    d_weights1, d_weights2, d_weights3 = nn.backward(X_train, y_train, output)
    nn.update_weights(d_weights1, d_weights2, d_weights3, learning_rate, epoch + 1)
    if epoch % 100 == 0:
        print("Epoch: {}, Loss: {}".format(epoch, np.mean((output - y_train) ** 2)))

# Test neural network
output = nn.forward(X_test)
print("Test accuracy: {}".format(np.mean(np.argmax(output, axis=1) == np.argmax(y_test, axis=1))))

# Plot example digits
fig, axes = plt.subplots(2, 5, figsize=(15, 6))
for i in range(10):
    ax = axes[i // 5, i % 5]
    ax.imshow(digits.images[i], cmap='gray')
    ax.set_title("Digit: {}".format(digits.target[i]))
plt.tight_layout()
plt.show()

# Plot confusion matrix
predicted_labels = np.argmax(output, axis=1)
actual_labels = np.argmax(y_test, axis=1)
confusion_matrix = np.zeros((10, 10))
for i in range(len(predicted_labels)):
    confusion_matrix[actual_labels[i], predicted_labels[i]] += 1

plt.figure(figsize=(10, 8))
plt.imshow(confusion_matrix, cmap='Blues')
plt.xlabel("Predicted Labels")
plt.ylabel("Actual Labels")
plt.title("Confusion Matrix")
plt.show()
