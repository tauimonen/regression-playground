import tkinter as tk
import numpy as np
import statsmodels.api as sm

points = []

CANVAS_WIDTH = 600
CANVAS_HEIGHT = 400
PADDING = 50

# Axes ranges
X_MIN, X_MAX = 0, 100
Y_MIN, Y_MAX = 0, 100

# Language dictionaries
TEXTS = {
    "en": {
        "instruction": "Enter a point (X and Y) or click on the canvas to add a point. Press 'Make Analysis' or right-click on the canvas to compute the regression.",
        "x_label": "X:",
        "y_label": "Y:",
        "add_point": "Add Point",
        "make_analysis": "Make Analysis",
        "new_analysis": "New Analysis",
        "slope": "Slope (β1)",
        "intercept": "Intercept (β0)",
        "residuals": "Residuals e_i",
        "r2": "R²",
        "adj_r2": "Adjusted R²",
        "p_values": "P-values",
        "f_stat": "F-statistic",
        "std_err": "Standard Errors",
    },
    "fi": {
        "instruction": "Syötä piste (X ja Y) tai klikkaa asteikkoa lisätäksesi pisteen. Paina 'Laske analyysi' tai hiiren oikeaa näppäintä.",
        "x_label": "X:",
        "y_label": "Y:",
        "add_point": "Lisää piste",
        "make_analysis": "Laske analyysi",
        "new_analysis": "Uusi analyysi",
        "slope": "Kulmakerroin (β1)",
        "intercept": "Leikkauspiste (β0)",
        "residuals": "Jäännökset e_i",
        "r2": "R²",
        "adj_r2": "Korjattu R²",
        "p_values": "P-arvot",
        "f_stat": "F-testitilasto",
        "std_err": "Keskivirheet",
    },
}

current_lang = "en"


def switch_language(lang):
    global current_lang
    current_lang = lang
    # Update all labels and buttons
    instruction_label.config(text=TEXTS[lang]["instruction"])
    x_label.config(text=TEXTS[lang]["x_label"])
    y_label.config(text=TEXTS[lang]["y_label"])
    add_button.config(text=TEXTS[lang]["add_point"])
    make_analysis_button.config(text=TEXTS[lang]["make_analysis"])
    new_button.config(text=TEXTS[lang]["new_analysis"])


root = tk.Tk()
root.title("Linear Regression Interactive Tool")

# Instruction label
instruction_label = tk.Label(root, text="", font=("Arial", 12))
instruction_label.pack(pady=5)

# Frame for entry fields and buttons
entry_frame = tk.Frame(root)
entry_frame.pack(pady=5)

x_label = tk.Label(entry_frame, text="")
x_label.grid(row=0, column=0)
x_entry = tk.Entry(entry_frame, width=8)
x_entry.grid(row=0, column=1, padx=5)

y_label = tk.Label(entry_frame, text="")
y_label.grid(row=0, column=2)
y_entry = tk.Entry(entry_frame, width=8)
y_entry.grid(row=0, column=3, padx=5)

# Language selection frame
lang_frame = tk.Frame(root)
lang_frame.pack(pady=5)

# Label for language selection
lang_label = tk.Label(lang_frame, text="Change Language / Vaihda kieltä:")
lang_label.pack(side="left", padx=5)

# Language buttons
tk.Button(lang_frame, text="English", command=lambda: switch_language("en")).pack(
    side="left", padx=5
)
tk.Button(lang_frame, text="Suomi", command=lambda: switch_language("fi")).pack(
    side="left", padx=5
)

# Canvas and labels
canvas = tk.Canvas(root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="white")
canvas.pack()

info_label = tk.Label(root, text="", justify="left", font=("Courier", 10))
info_label.pack()


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


def add_point_from_entry():
    try:
        x_graph = float(x_entry.get())
        y_graph = float(y_entry.get())
    except ValueError:
        return

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

    residuals_rounded = [round(float(r), 2) for r in Y - model.fittedvalues]
    bse_rounded = [round(float(b), 2) for b in model.bse]
    params_rounded = [round(float(p), 2) for p in model.params]
    pvalues_rounded = [round(float(p), 3) for p in model.pvalues]

    t = TEXTS[current_lang]
    info_label.config(
        text=(
            f"{t['slope']} = {params_rounded[1]}\n"
            f"{t['intercept']} = {params_rounded[0]}\n"
            f"{t['residuals']} = {residuals_rounded}\n"
            f"{t['r2']} = {model.rsquared:.3f}\n"
            f"{t['adj_r2']} = {model.rsquared_adj:.3f}\n"
            f"{t['p_values']} = {pvalues_rounded}\n"
            f"{t['f_stat']} = {model.fvalue:.2f}, p={model.f_pvalue:.3f}\n"
            f"{t['std_err']} = {bse_rounded}\n"
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


# Buttons
add_button = tk.Button(entry_frame, text="", command=add_point_from_entry)
add_button.grid(row=0, column=4, padx=10)

new_button = tk.Button(entry_frame, text="", command=new_analysis)
new_button.grid(row=0, column=5, padx=10)

make_analysis_button = tk.Button(entry_frame, text="", command=finish_analysis)
make_analysis_button.grid(row=0, column=6, padx=10)

canvas.bind("<Button-1>", add_point)
canvas.bind("<Button-3>", finish_analysis)

# Initialize language to English
switch_language("en")

root.mainloop()
