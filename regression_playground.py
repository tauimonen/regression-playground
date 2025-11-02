"""
Linear Regression Interactive Tool with Tkinter

This program allows users to interactively input 2D data points and perform
simple linear regression analysis. Users can add points by either clicking
on the canvas or entering X and Y coordinates manually, and then visualize
the regression line along with key statistical metrics.

Features:
- Interactive point input via mouse click or text entry fields.
- Display of X and Y axes with labeled ticks.
- "Add Point" button to add points from entry fields.
- "Make Analysis" button or right-click on the canvas to calculate and
  display regression line, residuals, R², adjusted R², standard errors,
  p-values, F-statistic, and variance inflation factor (VIF).
- "New Analysis" button to clear points and results and start fresh.
- Rounded and formatted display of statistics for readability.

Dependencies:
- tkinter: GUI for canvas, labels, and buttons.
- numpy: For numerical operations and array handling.
- statsmodels: For Ordinary Least Squares (OLS) regression and statistical metrics.

Usage:
1. Add points by clicking on the canvas or typing X and Y coordinates and
   pressing "Add Point".
2. Press "Make Analysis" or right-click on the canvas to perform regression.
3. Review the regression line and statistical information displayed below the canvas.
4. Use "New Analysis" to reset the canvas and start a new set of points.

Version: 1.0
Author: tauimonen
Date: 2.11.2025
"""

import tkinter as tk
import numpy as np
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor

points = []

CANVAS_WIDTH = 600
CANVAS_HEIGHT = 400
PADDING = 50

root = tk.Tk()
root.title("Linear Regression Statistics")

# Instruction label
instruction_label = tk.Label(
    root,
    text="Enter a point (X and Y) or click on the canvas to add a point. "
    "Press 'Make Analysis' or right-click on the canvas to compute the regression.",
    font=("Arial", 12),
)
instruction_label.pack(pady=5)

# Frame for entry fields and buttons
entry_frame = tk.Frame(root)
entry_frame.pack(pady=5)

tk.Label(entry_frame, text="X:").grid(row=0, column=0)
x_entry = tk.Entry(entry_frame, width=8)
x_entry.grid(row=0, column=1, padx=5)

tk.Label(entry_frame, text="Y:").grid(row=0, column=2)
y_entry = tk.Entry(entry_frame, width=8)
y_entry.grid(row=0, column=3, padx=5)


def graph_to_canvas(x, y):
    x_canvas = PADDING + (x - X_MIN) / (X_MAX - X_MIN) * (CANVAS_WIDTH - 2 * PADDING)
    y_canvas = (
        CANVAS_HEIGHT
        - PADDING
        - (y - Y_MIN) / (Y_MAX - Y_MIN) * (CANVAS_HEIGHT - 2 * PADDING)
    )
    return x_canvas, y_canvas


def draw_axes():
    canvas.delete("axes")
    # X-axis
    canvas.create_line(
        PADDING,
        CANVAS_HEIGHT - PADDING,
        CANVAS_WIDTH - PADDING,
        CANVAS_HEIGHT - PADDING,
        width=2,
        arrow=tk.LAST,
        tags="axes",
    )
    # Y-axis
    canvas.create_line(
        PADDING,
        CANVAS_HEIGHT - PADDING,
        PADDING,
        PADDING,
        width=2,
        arrow=tk.LAST,
        tags="axes",
    )
    # Labels
    canvas.create_text(
        CANVAS_WIDTH - PADDING + 15,
        CANVAS_HEIGHT - PADDING,
        text="X",
        anchor="nw",
        font=("Arial", 12),
        tags="axes",
    )
    canvas.create_text(
        PADDING, PADDING - 15, text="Y", anchor="nw", font=("Arial", 12), tags="axes"
    )
    # Ticks
    for i in range(11):
        x_val = X_MIN + i * (X_MAX - X_MIN) / 10
        x_tick, y_tick = graph_to_canvas(x_val, Y_MIN)
        canvas.create_line(
            x_tick,
            CANVAS_HEIGHT - PADDING - 5,
            x_tick,
            CANVAS_HEIGHT - PADDING + 5,
            tags="axes",
        )
        canvas.create_text(
            x_tick,
            CANVAS_HEIGHT - PADDING + 15,
            text=f"{x_val:.0f}",
            font=("Arial", 8),
            tags="axes",
        )
    for i in range(11):
        y_val = Y_MIN + i * (Y_MAX - Y_MIN) / 10
        x_tick, y_tick = graph_to_canvas(X_MIN, y_val)
        canvas.create_line(PADDING - 5, y_tick, PADDING + 5, y_tick, tags="axes")
        canvas.create_text(
            PADDING - 30, y_tick, text=f"{y_val:.0f}", font=("Arial", 8), tags="axes"
        )


def add_point_from_entry():
    try:
        x_graph = float(x_entry.get())
        y_graph = float(y_entry.get())
    except ValueError:
        return  # Ignore invalid input

    # Check if within bounds
    if not (X_MIN <= x_graph <= X_MAX and Y_MIN <= y_graph <= Y_MAX):
        return

    points.append((x_graph, y_graph))
    cx, cy = graph_to_canvas(x_graph, y_graph)
    canvas.create_oval(cx - 3, cy - 3, cx + 3, cy + 3, fill="blue", tags="points")
    canvas.create_text(
        cx + 5,
        cy - 10,
        text=f"({x_graph:.1f},{y_graph:.1f})",
        anchor="nw",
        font=("Arial", 9),
        tags="points",
    )
    x_entry.delete(0, tk.END)
    y_entry.delete(0, tk.END)


def add_point(event):
    x_scale = (X_MAX - X_MIN) / (CANVAS_WIDTH - 2 * PADDING)
    y_scale = (Y_MAX - Y_MIN) / (CANVAS_HEIGHT - 2 * PADDING)

    x_graph = X_MIN + (event.x - PADDING) * x_scale
    y_graph = Y_MIN + (CANVAS_HEIGHT - PADDING - event.y) * y_scale

    points.append((x_graph, y_graph))
    cx, cy = graph_to_canvas(x_graph, y_graph)
    canvas.create_oval(cx - 3, cy - 3, cx + 3, cy + 3, fill="blue", tags="points")
    canvas.create_text(
        cx + 5,
        cy - 10,
        text=f"({x_graph:.1f},{y_graph:.1f})",
        anchor="nw",
        font=("Arial", 9),
        tags="points",
    )


def finish_analysis(event=None):
    if len(points) < 2:
        return

    X = np.array([p[0] for p in points]).reshape(-1, 1)
    Y = np.array([p[1] for p in points])

    X_const = sm.add_constant(X)
    model = sm.OLS(Y, X_const).fit()

    # Draw regression line
    y0 = model.params[0] + model.params[1] * X_MIN
    y1 = model.params[0] + model.params[1] * X_MAX
    x0_canvas, y0_canvas = graph_to_canvas(X_MIN, y0)
    x1_canvas, y1_canvas = graph_to_canvas(X_MAX, y1)
    canvas.create_line(
        x0_canvas, y0_canvas, x1_canvas, y1_canvas, fill="red", width=2, tags="points"
    )

    # Calculate residuals and round
    residuals_rounded = [round(float(r), 2) for r in Y - model.fittedvalues]
    bse_rounded = [round(float(b), 2) for b in model.bse]
    params_rounded = [round(float(p), 2) for p in model.params]
    pvalues_rounded = [round(float(p), 3) for p in model.pvalues]

    info_label.config(
        text=(
            f"Slope (β1) = {params_rounded[1]}\n"
            f"Intercept (β0) = {params_rounded[0]}\n"
            f"Residuals e_i = {residuals_rounded}\n"
            f"R² = {model.rsquared:.3f}\n"
            f"Adjusted R² = {model.rsquared_adj:.3f}\n"
            f"P-values = {pvalues_rounded}\n"
            f"F-statistic = {model.fvalue:.2f}, p={model.f_pvalue:.3f}\n"
            f"Standard Errors = {bse_rounded}\n"
            f"VIF = 1"
        )
    )


def new_analysis():
    global points
    points = []
    canvas.delete("points")
    info_label.config(text="")
    x_entry.delete(0, tk.END)
    y_entry.delete(0, tk.END)
    canvas.bind("<Button-1>", add_point)
    canvas.bind("<Button-3>", finish_analysis)


# Canvas and labels
canvas = tk.Canvas(root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="white")
canvas.pack()

info_label = tk.Label(root, text="", justify="left", font=("Courier", 10))
info_label.pack()

# Axes ranges
X_MIN, X_MAX = 0, 100
Y_MIN, Y_MAX = 0, 100

draw_axes()

# Buttons (New Analysis first, then Make Analysis)
add_button = tk.Button(entry_frame, text="Add Point", command=add_point_from_entry)
add_button.grid(row=0, column=4, padx=10)

new_button = tk.Button(entry_frame, text="New Analysis", command=new_analysis)
new_button.grid(row=0, column=5, padx=10)

make_analysis_button = tk.Button(
    entry_frame, text="Make Analysis", command=finish_analysis
)
make_analysis_button.grid(row=0, column=6, padx=10)

# Bind mouse clicks
canvas.bind("<Button-1>", add_point)
canvas.bind("<Button-3>", finish_analysis)

root.mainloop()
