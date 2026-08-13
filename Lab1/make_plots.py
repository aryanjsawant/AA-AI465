"""
Generate high-quality plots for Lab 1 Exercises 2 and 3.
Saves PNG files to the outputs/ directory for embedding in lab reports.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path

# Set style for professional appearance
plt.style.use('default')
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 10

# Output directory
OUTPUT_DIR = Path(__file__).parent / 'outputs'
OUTPUT_DIR.mkdir(exist_ok=True)

# Color scheme
COLORS = {
    'reflex': '#2d5a6b',
    'noop': '#e8956b',
    'decay': '#9b6ba6',
    'lazy': '#a0a0a0',
    'naive': '#d9534f',
    'heading': '#5cb85c',
    'model': '#0275d8',
}

# ============================================================================
# EXERCISE 2: CORRIDOR SCALING
# ============================================================================

def plot_exercise_2():
    """Plot Exercise 2: Agent performance in corridors of varying length."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle('Exercise 2: 1×N Corridor — Agent Comparison',
                 fontsize=14, fontweight='bold', y=0.98)

    # Corridor lengths and scores
    n_values = [2, 4, 6, 8, 10]
    naive_scores = [2, -9, 2, 2, 24]
    heading_scores = [2, 13, 24, 35, 57]
    model_scores = [19, 26, 33, 40, 57]

    naive_dirty = [0, 2, 2, 3, 3]
    heading_dirty = [0, 0, 0, 0, 0]
    model_dirty = [0, 0, 0, 0, 0]

    # Plot 1: Task Score
    ax1.plot(n_values, naive_scores, marker='o', linewidth=2.5, markersize=8,
             label='Naive reflex (no state)', color=COLORS['naive'], alpha=0.8)
    ax1.plot(n_values, heading_scores, marker='s', linewidth=2.5, markersize=8,
             label='Reflex + heading (1 bit)', color=COLORS['heading'], alpha=0.8)
    ax1.plot(n_values, model_scores, marker='^', linewidth=2.5, markersize=8,
             label='Model-based (full belief)', color=COLORS['model'], alpha=0.8)

    ax1.set_xlabel('Corridor Length (N squares)', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Task Score', fontsize=11, fontweight='bold')
    ax1.set_xticks(n_values)
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.legend(loc='upper left', framealpha=0.95)
    ax1.axhline(y=0, color='black', linewidth=0.8, linestyle='-', alpha=0.3)

    # Plot 2: Dirty Squares Remaining
    width = 0.25
    x = np.arange(len(n_values))

    ax2.bar(x - width, naive_dirty, width, label='Naive reflex',
            color=COLORS['naive'], alpha=0.8)
    ax2.bar(x, heading_dirty, width, label='Reflex + heading',
            color=COLORS['heading'], alpha=0.8)
    ax2.bar(x + width, model_dirty, width, label='Model-based',
            color=COLORS['model'], alpha=0.8)

    ax2.set_xlabel('Corridor Length (N squares)', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Dirty Squares Remaining (after 20 steps)', fontsize=11, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(n_values)
    ax2.set_ylim([0, 3.5])
    ax2.legend(loc='upper left', framealpha=0.95)
    ax2.grid(True, alpha=0.3, axis='y', linestyle='--')

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'exp2_corridor_scaling.png', dpi=300, bbox_inches='tight')
    print(f"[OK] Saved: exp2_corridor_scaling.png")
    plt.close()


# ============================================================================
# EXERCISE 3: STOCHASTIC DIRT SENSITIVITY
# ============================================================================

def plot_exercise_3():
    """Plot Exercise 3: Agent performance across re-dirtying probabilities."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle('Exercise 3: Stochastic Dirt — Sensitivity to Re-dirtying Probability',
                 fontsize=14, fontweight='bold', y=0.98)

    # Data from sensitivity table
    p_values = [0.00, 0.02, 0.05, 0.10, 0.20, 0.40]
    reflex_scores = [-8.00, 3.44, 21.20, 47.16, 97.22, 163.54]
    noop_scores = [19.00, 23.20, 32.15, 45.65, 75.35, 133.70]
    decay_scores = [12.00, 21.68, 36.39, 58.03, 98.12, 155.67]
    lazy_scores = [10.00, 14.85, 23.60, 37.85, 68.45, 128.30]

    reflex_credit = [58.00, 57.41, 56.42, 54.53, 50.20, 41.22]
    noop_credit = [58.00, 50.74, 44.09, 38.38, 33.99, 31.50]
    decay_credit = [58.00, 56.67, 54.48, 51.66, 46.19, 38.03]
    lazy_credit = [30.00, 30.00, 30.00, 30.00, 30.00, 30.00]

    # Plot 1: Task Score
    ax1.plot(p_values, reflex_scores, marker='o', linewidth=2.5, markersize=7,
             label='Simple reflex', color=COLORS['reflex'], alpha=0.85)
    ax1.plot(p_values, noop_scores, marker='s', linewidth=2.5, markersize=7,
             label='Model-based + NoOp', color=COLORS['noop'], alpha=0.85)
    ax1.plot(p_values, decay_scores, marker='^', linewidth=2.5, markersize=7,
             label='Model-based + decay(3)', color=COLORS['decay'], alpha=0.85)
    ax1.plot(p_values, lazy_scores, marker='d', linewidth=2.5, markersize=7,
             label='Lazy (never moves)', color=COLORS['lazy'], alpha=0.85)

    ax1.set_xlabel('Re-dirtying Probability (p)', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Mean Task Score (200 runs, 30 steps)', fontsize=11, fontweight='bold')
    ax1.set_xticks(p_values)
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.legend(loc='upper left', framealpha=0.95, fontsize=9)
    ax1.axhline(y=0, color='black', linewidth=0.8, linestyle='-', alpha=0.3)

    # Plot 2: Clean-Square Credit
    ax2.plot(p_values, reflex_credit, marker='o', linewidth=2.5, markersize=7,
             label='Simple reflex', color=COLORS['reflex'], alpha=0.85)
    ax2.plot(p_values, noop_credit, marker='s', linewidth=2.5, markersize=7,
             label='Model-based + NoOp', color=COLORS['noop'], alpha=0.85)
    ax2.plot(p_values, decay_credit, marker='^', linewidth=2.5, markersize=7,
             label='Model-based + decay(3)', color=COLORS['decay'], alpha=0.85)
    ax2.plot(p_values, lazy_credit, marker='d', linewidth=2.5, markersize=7,
             label='Lazy (never moves)', color=COLORS['lazy'], alpha=0.85)

    ax2.set_xlabel('Re-dirtying Probability (p)', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Mean Clean-Square Credit (max 60)', fontsize=11, fontweight='bold')
    ax2.set_xticks(p_values)
    ax2.grid(True, alpha=0.3, linestyle='--')
    ax2.legend(loc='upper right', framealpha=0.95, fontsize=9)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'exp3_stochastic_sensitivity.png', dpi=300, bbox_inches='tight')
    print(f"[OK] Saved: exp3_stochastic_sensitivity.png")
    plt.close()


# ============================================================================
# EXERCISE 1: COMPARISON (Simple vs Model-Based)
# ============================================================================

def plot_exercise_1():
    """Plot Exercise 1: Simple reflex vs Model-based agent."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle('Exercise 1: Simple Reflex vs Model-Based Agent (20 steps)',
                 fontsize=14, fontweight='bold', y=0.98)

    # Data from the output
    steps = np.arange(1, 21)
    simple_scores = [10, 9, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2]
    model_scores = [10, 9, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19]

    simple_credit = [1, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38]
    model_credit = [1, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38]

    # Plot 1: Task Score Over Time
    ax1.plot(steps, simple_scores, marker='o', linewidth=2, markersize=5,
             label='Simple reflex (no memory)', color=COLORS['reflex'], alpha=0.8)
    ax1.plot(steps, model_scores, marker='s', linewidth=2, markersize=5,
             label='Model-based (remembers)', color=COLORS['model'], alpha=0.8)

    ax1.set_xlabel('Time Step', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Cumulative Task Score', fontsize=11, fontweight='bold')
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.legend(loc='upper left', framealpha=0.95)
    ax1.set_xlim([0.5, 20.5])

    # Annotate key difference
    ax1.annotate('', xy=(20, 2), xytext=(20, 19),
                arrowprops=dict(arrowstyle='<->', color='red', lw=2, alpha=0.6))
    ax1.text(20.5, 10.5, '17-point\ndifference', fontsize=10, color='red', fontweight='bold')

    # Plot 2: Clean-Square Credit (same for both)
    ax2.plot(steps, simple_credit, marker='o', linewidth=2.5, markersize=5,
             label='Both agents', color=COLORS['decay'], alpha=0.8)

    ax2.set_xlabel('Time Step', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Cumulative Clean-Square Credit', fontsize=11, fontweight='bold')
    ax2.grid(True, alpha=0.3, linestyle='--')
    ax2.legend(loc='upper left', framealpha=0.95)
    ax2.set_xlim([0.5, 20.5])
    ax2.text(11, 20, 'Identical: both clean\nthe same squares',
            fontsize=10, color=COLORS['decay'], fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'exp1_comparison.png', dpi=300, bbox_inches='tight')
    print(f"[OK] Saved: exp1_comparison.png")
    plt.close()


# ============================================================================
# SUMMARY COMPARISON TABLE
# ============================================================================

def create_summary_table():
    """Create a summary table as an image."""
    fig, ax = plt.subplots(figsize=(11, 4))
    ax.axis('tight')
    ax.axis('off')

    # Data for the table
    data = [
        ['Exercise', 'Agents Tested', 'Key Finding', 'Winner'],
        ['1: Basic\nTwo Squares', 'Simple Reflex\nvs Model-Based', 'Memory stops oscillation:\n+2 vs +19 score (20 steps)', 'Model-Based\n(+17 advantage)'],
        ['2: Corridor\nN Squares', 'Naive Reflex\nvs Reflex+Heading\nvs Model-Based', 'One bit of state is enough\nto sweep; model adds early stop', 'Model-Based\n(full coverage)'],
        ['3: Stochastic\nRe-dirtying', 'Simple Reflex\nvs 3 Model Variants\nvs Lazy', 'Decay mechanism best:\nbalances exploration & exploitation', 'Model+Decay\n(adapts to noise)'],
    ]

    table = ax.table(cellText=data, cellLoc='left', loc='center',
                    colWidths=[0.15, 0.25, 0.35, 0.25])

    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2.2)

    # Style header row
    for i in range(4):
        cell = table[(0, i)]
        cell.set_facecolor('#2d5a6b')
        cell.set_text_props(weight='bold', color='white')

    # Alternate row colors
    for i in range(1, 4):
        for j in range(4):
            cell = table[(i, j)]
            if i % 2 == 0:
                cell.set_facecolor('#f0f0f0')
            cell.set_text_props(verticalalignment='center')

    plt.title('Lab 1 Exercises Summary', fontsize=13, fontweight='bold', pad=20)
    plt.savefig(OUTPUT_DIR / 'summary_table.png', dpi=300, bbox_inches='tight',
               facecolor='white', edgecolor='none')
    print(f"[OK] Saved: summary_table.png")
    plt.close()


if __name__ == "__main__":
    print("Generating plots for Lab 1 Exercises...\n")

    try:
        plot_exercise_1()
        plot_exercise_2()
        plot_exercise_3()
        create_summary_table()

        print(f"\n[SUCCESS] All plots saved to: {OUTPUT_DIR}")
        print("\nFiles created:")
        print("  • exp1_comparison.png          (Exercise 1: Simple vs Model-Based)")
        print("  • exp2_corridor_scaling.png    (Exercise 2: Corridor Performance)")
        print("  • exp3_stochastic_sensitivity.png (Exercise 3: Stochastic Dirt)")
        print("  • summary_table.png            (Lab Summary Table)")
        print("\nYou can now insert these images into your lab document.")

    except Exception as e:
        print(f"Error: {e}")
