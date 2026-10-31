"""SVNIT Surat — Department of Artificial Intelligence
Agentic AI (IA462) — Semester VIII
Experiment 9: Artificial Neural Network — Multilayer Perceptron Trained by Backpropagation
Roll No: U23AI042
"""

import os
import numpy as np

os.makedirs("outputs", exist_ok=True)

X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=np.float64)
Y = np.array([[0], [1], [1], [0]], dtype=np.float64)

def sigmoid(z):
    z = np.clip(z, -25.0, 25.0)
    return 1.0 / (1.0 + np.exp(-z))

def sigmoid_deriv(a):
    return a * (1.0 - a)

def tanh_act(z):
    return np.tanh(z)

def tanh_deriv(a):
    return 1.0 - a ** 2

class MLP:
    def __init__(self, n_input, n_hidden, n_output, lr=0.5, seed=42,
                 zero_init=False, hidden_activation="sigmoid"):
        rng = np.random.RandomState(seed)
        if zero_init:
            self.W1 = np.zeros((n_input, n_hidden))
            self.b1 = np.zeros((1, n_hidden))
            self.W2 = np.zeros((n_hidden, n_output))
            self.b2 = np.zeros((1, n_output))
        else:
            self.W1 = rng.uniform(-1, 1, (n_input, n_hidden))
            self.b1 = np.zeros((1, n_hidden))
            self.W2 = rng.uniform(-1, 1, (n_hidden, n_output))
            self.b2 = np.zeros((1, n_output))
        self.lr = lr
        if hidden_activation == "tanh":
            self.h_act = tanh_act
            self.h_deriv = tanh_deriv
        else:
            self.h_act = sigmoid
            self.h_deriv = sigmoid_deriv
    
    def forward(self, X):
        self.z1 = X @ self.W1 + self.b1
        self.a1 = self.h_act(self.z1)
        self.z2 = self.a1 @ self.W2 + self.b2
        self.a2 = sigmoid(self.z2)
        return self.a2
    
    def backward(self, X, Y):
        delta2 = (self.a2 - Y) * sigmoid_deriv(self.a2)
        delta1 = (delta2 @ self.W2.T) * self.h_deriv(self.a1)
        self.W2 -= self.lr * (self.a1.T @ delta2)
        self.b2 -= self.lr * np.sum(delta2, axis=0, keepdims=True)
        self.W1 -= self.lr * (X.T @ delta1)
        self.b1 -= self.lr * np.sum(delta1, axis=0, keepdims=True)
    
    def mse(self, Y):
        return 0.5 * np.mean((self.a2 - Y) ** 2)
    
    def train(self, X, Y, max_epochs=6000, tol=0.005, check_interval=1, record_history=False):
        history = []
        for epoch in range(1, max_epochs + 1):
            self.forward(X)
            if record_history:
                history.append(self.mse(Y))
            self.backward(X, Y)
            if epoch % check_interval == 0:
                err = self.mse(Y)
                preds = (self.a2 > 0.5).astype(float)
                if err < tol and np.all(preds == Y):
                    return epoch, err, history
        return max_epochs, self.mse(Y), history

if __name__ == "__main__":
    # Reference Run
    net = MLP(n_input=2, n_hidden=2, n_output=1, lr=0.5, seed=42)
    epochs, final_mse, history = net.train(X, Y, max_epochs=6000, tol=0.005, record_history=True)
    outputs = net.forward(X)

    print("=" * 60)
    print("REFERENCE RUN: 2-2-1 MLP, lr=0.5, seed=42")
    print("=" * 60)
    print(f"Epochs to convergence: {epochs}")
    print(f"Final MSE:             {final_mse:.6f}")
    print("\nLearned Outputs:")
    print(f"  (0,0) -> {outputs[0,0]:.4f}  (target: 0)")
    print(f"  (0,1) -> {outputs[1,0]:.4f}  (target: 1)")
    print(f"  (1,0) -> {outputs[2,0]:.4f}  (target: 1)")
    print(f"  (1,1) -> {outputs[3,0]:.4f}  (target: 0)")
    print(f"  Correct: {np.all((outputs > 0.5).astype(float) == Y)}")
    print("\nLearned Weights:")
    print(f"  W1 (2x2):\n{net.W1}")
    print(f"  b1 (1x2): {net.b1}")
    print(f"  W2 (2x1):\n{net.W2}")
    print(f"  b2 (1x1): {net.b2}")

    # Exercise 1: Sweep
    hidden_units = [1, 2, 3, 4, 8]
    learning_rates = [0.1, 0.5, 1.0]
    n_seeds = 20
    MAX_EPOCHS = 5000
    TOL = 0.005

    print("\n" + "=" * 85)
    print("EXERCISE 1: HIDDEN UNIT & LEARNING RATE SWEEP (20 seeds per setting)")
    print("=" * 85)
    header = f"{'h':>3}  {'lr':>5}  {'Converged':>10}  {'Conv. Rate':>10}  {'Median Epochs':>14}  {'Min':>6}  {'Max':>6}"
    print(header)
    print("-" * len(header))

    for h in hidden_units:
        for lr in learning_rates:
            conv_count = 0
            conv_epochs = []
            for seed in range(n_seeds):
                net_test = MLP(n_input=2, n_hidden=h, n_output=1, lr=lr, seed=seed)
                ep, mse_final, _ = net_test.train(X, Y, max_epochs=MAX_EPOCHS, tol=TOL, check_interval=10)
                if ep < MAX_EPOCHS:
                    conv_count += 1
                    conv_epochs.append(ep)
            med_ep = int(np.median(conv_epochs)) if conv_epochs else -1
            min_ep = min(conv_epochs) if conv_epochs else -1
            max_ep = max(conv_epochs) if conv_epochs else -1
            rate_str = f"{conv_count}/{n_seeds}"
            med_str = f"{med_ep}" if med_ep > 0 else "N/A"
            min_str = f"{min_ep}" if min_ep > 0 else "N/A"
            max_str = f"{max_ep}" if max_ep > 0 else "N/A"
            print(f"{h:>3}  {lr:>5.1f}  {rate_str:>10}  {conv_count/n_seeds:>10.0%}  {med_str:>14}  {min_str:>6}  {max_str:>6}")
        print()

    # Exercise 2A: Zero init
    print("=" * 70)
    print("EXERCISE 2A: ZERO WEIGHT INITIALISATION (2-2-1, lr=0.5)")
    print("=" * 70)
    net_zero = MLP(n_input=2, n_hidden=2, n_output=1, lr=0.5, seed=42, zero_init=True)
    ep_zero, mse_zero, _ = net_zero.train(X, Y, max_epochs=5000, tol=0.005, record_history=False)
    out_zero = net_zero.forward(X)
    print(f"Epochs used:  {ep_zero}  {'(CONVERGED)' if ep_zero < 5000 else '(DID NOT CONVERGE)'}")
    print(f"Final MSE:    {mse_zero:.6f}")
    print("\nOutputs:")
    for i in range(4):
        print(f"  ({int(X[i,0])},{int(X[i,1])}) -> {out_zero[i,0]:.4f}  (target: {int(Y[i,0])})")
    print(f"\nHidden Weight Matrix W1 after training:\n{net_zero.W1}")
    print(f"\nHidden Bias b1 after training:\n{net_zero.b1}")
    print(f"\nOutput Weight Matrix W2 after training:\n{net_zero.W2}")

    # Exercise 2B: Tanh activation
    print("\n" + "=" * 70)
    print("EXERCISE 2B: TANH HIDDEN ACTIVATION (2-2-1, lr=0.5, seed=42)")
    print("=" * 70)
    net_tanh = MLP(n_input=2, n_hidden=2, n_output=1, lr=0.5, seed=42, hidden_activation="tanh")
    ep_tanh, mse_tanh, _ = net_tanh.train(X, Y, max_epochs=5000, tol=0.005, record_history=False)
    out_tanh = net_tanh.forward(X)
    print(f"Epochs to convergence: {ep_tanh}  {'(CONVERGED)' if ep_tanh < 5000 else '(DID NOT CONVERGE)'}")
    print(f"Final MSE:             {mse_tanh:.6f}")
    print("\nOutputs:")
    for i in range(4):
        print(f"  ({int(X[i,0])},{int(X[i,1])}) -> {out_tanh[i,0]:.4f}  (target: {int(Y[i,0])})")
