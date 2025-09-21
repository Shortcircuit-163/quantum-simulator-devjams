import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

def draw_bloch(ax, vector=[0,0,1], title="Bloch Sphere"):
    # Sphere surface
    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(0, np.pi, 100)
    x = np.outer(np.cos(u), np.sin(v))
    y = np.outer(np.sin(u), np.sin(v))
    z = np.outer(np.ones(np.size(u)), np.cos(v))
    ax.plot_surface(x, y, z, color='lightblue', alpha=0.2, edgecolor='gray')

    # Axes
    ax.quiver(0,0,0, 1,0,0, color="purple")   # x
    ax.quiver(0,0,0, 0,1,0, color="green")    # y
    ax.quiver(0,0,0, 0,0,1, color="red")      # z

    # State vector (black arrow)
    ax.quiver(0,0,0, vector[0], vector[1], vector[2], color="black", linewidth=2)

    # Labels
    ax.text(0,0,1.1,"|0>")
    ax.text(0,0,-1.1,"|1>")
    ax.text(1.1,0,0,"|+>")
    ax.text(-1.1,0,0,"|->")
    ax.text(0,1.1,0,"|+i>")
    ax.text(0,-1.1,0,"|-i>")

    ax.set_title(title)
    ax.set_box_aspect([1,1,1])
    ax.axis("off")

def show_two_spheres(parent):
    new_win = tk.Toplevel(parent)
    new_win.title("Two Bloch Spheres")

    fig = Figure(figsize=(8,4))
    ax1 = fig.add_subplot(121, projection='3d')
    ax2 = fig.add_subplot(122, projection='3d')

    draw_bloch(ax1, [0,0,1], title="|0> state")
    draw_bloch(ax2, [1,0,0], title="|+> state")

    canvas = FigureCanvasTkAgg(fig, master=new_win)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

if __name__ == '__main__':
    root = tk.Tk()
    root.title("Bloch Sphere GUI")

    btn = tk.Button(root, text="Show Two Bloch Spheres", command=lambda: show_two_spheres(root))
    btn.pack(pady=20)

    root.mainloop()
