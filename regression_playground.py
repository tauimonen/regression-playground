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

canvas = tk.Canvas(root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="white")
canvas.pack()

info_label = tk.Label(root, text="", justify="left", font=("Courier", 10))
info_label.pack()

# Axes ranges
X_MIN, X_MAX = 0, 100
Y_MIN, Y_MAX = 0, 100


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


draw_axes()


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


def finish(event):
    if len(points) < 2:
        return

    X = np.array([p[0] for p in points]).reshape(-1, 1)
    Y = np.array([p[1] for p in points])

    # Add constant term for intercept
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

    # Calculate residuals
    residuals = Y - model.fittedvalues

    # Calculate VIF (for single variable it's always 1)
    vif = [variance_inflation_factor(X_const, i) for i in range(X_const.shape[1])]

    # Round and display statistics
    residuals_rounded = [round(float(r), 2) for r in residuals]
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

    canvas.unbind("<Button-1>")
    canvas.unbind("<Button-3>")


canvas.bind("<Button-1>", add_point)
canvas.bind("<Button-3>", finish)

root.mainloop()
