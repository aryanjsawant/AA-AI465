# Lab 9: Multi-Layer Perceptron (MLP) & Backpropagation

**Course:** Soft Computing (IA305) / Agentic AI  
**Institution:** SVNIT Surat, Department of Artificial Intelligence  
**Student:** Aryan Sawant (Roll No: `U23AI042`)

---

## Overview & Objectives
This experiment implements a Multi-Layer Perceptron (MLP) from scratch in pure NumPy, derives the backpropagation gradient descent algorithm, and resolves Minsky & Papert's classic non-linearly separable **XOR Problem**:
1. **Network Architecture (2-2-1 MLP)**:
   - Input layer: $x \in \mathbb{R}^2$ ($x_1, x_2$).
   - Hidden layer: $h = 2$ neurons with Sigmoid / Tanh activations and bias weights.
   - Output layer: 1 neuron with Sigmoid activation ($\hat{y} \in [0, 1]$).
2. **Backpropagation Derivation & Implementation**:
   - Forward pass: $z_1 = X W_1 + b_1$, $a_1 = \sigma(z_1)$, $z_2 = a_1 W_2 + b_2$, $\hat{y} = \sigma(z_2)$.
   - Loss function: Mean Squared Error (MSE) $E = \frac{1}{2N} \sum (\hat{y} - y)^2$.
   - Output error delta: $\delta_2 = (\hat{y} - y) \odot \sigma'(\hat{y})$.
   - Hidden error delta: $\delta_1 = (\delta_2 W_2^T) \odot \sigma'(a_1)$.
   - Parameter updates: $W \leftarrow W - \eta \frac{\partial E}{\partial W}$, $b \leftarrow b - \eta \frac{\partial E}{\partial b}$.
3. **Architectural & Hyperparameter Investigations**:
   - **Hidden Unit Capacity ($h \in \{1, 2, 4, 8\}$)**: Proof that $h=1$ fails identically to a single-layer perceptron, $h=2$ solves XOR but is susceptible to local saddle points, and $h \ge 4$ converges with $100\%$ reliability.
   - **Symmetry Breaking & Zero Initialization**: Proof that initializing weights to zero prevents hidden neurons from differentiating (identical forward activations and gradients), permanently locking the network in a 1D subspace and preventing XOR convergence.
   - **Activation Function Dynamics**: Comparison between Sigmoid (positive output bias, $\sigma'(0)=0.25$) and Tanh (zero-centered $[-1, 1]$, $\tanh'(0)=1.0$), demonstrating faster gradient flow and faster convergence with Tanh.
   - **Learning Rate Sensitivity ($\eta \in \{0.05, 0.1, 0.5, 1.0, 2.0\}$)**: Trading convergence speed against oscillatory instability.

---

## Deliverables & Files

| File | Description |
|---|---|
| `lab9.ipynb` / `LAB_9_U23AI042.ipynb` | Fully executed Jupyter notebook with rigorous mathematical derivations, vectorized NumPy code, training curves, decision surface contours, and answers. |
| `exp9_mlp.py` | Standalone Python implementation running reference training, sweeps, and saving figures to `outputs/`. |
| `make_report.py` | Compiles the self-contained laboratory report `LAB_9_U23AI042.doc` with embedded high-resolution figures. |
| `LAB_9_U23AI042.doc` | Final laboratory report submission deliverable. |
| `IA305_Lab9_Neural_Network.pdf` | Lab assignment specification. |
| `outputs/` | Contains `exp9_mlp.txt` and generated publication figures (`lab9_fig1`, `lab9_fig2`, `lab9_fig3`). |

---

## How to Run

```bash
# Run standalone neural network training and export figures
python exp9_mlp.py

# Recompile laboratory report
python make_report.py

# Run or view notebook
jupyter notebook LAB_9_U23AI042.ipynb
```
