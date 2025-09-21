import numpy as np
import tkinter as tk
from tkinter import messagebox, simpledialog
from Basic_1 import zero_state, apply_single_qubit_gate, cnot_on_n_qubits, toffoli_on_n_qubits, H, X, Y, Z
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random

# Aesthetic settings
BG_COLOR = "#2E2E2E"
FG_COLOR = "#FFFFFF"
GATE_COLOR = "#5F9EA0"
CONTROL_COLOR = "#E9967A"
MEASURE_COLOR = "#98FB98"
BUTTON_BG = "#4A4A4A"
BUTTON_FG = "#FFFFFF"
FONT_FAMILY = "Helvetica"
FONT_SIZE_NORMAL = 10
FONT_SIZE_BOLD = 12

CELL_WIDTH = 80
CELL_HEIGHT = 50
TEXT_COLOR = "black"
GATE_SPACING = 30

class Circuit:
    def __init__(self, n_qubits):
        self.n = n_qubits
        self.state = zero_state(n_qubits)
        self.diagram = []  # list of gate info tuples
        self.step_index = -1  # for step-by-step simulation
        self.measurements = {}  # record {qubit: outcome}

    def add_gate(self, gate, targets, controls=[]):
        self.diagram.append((gate, targets, controls))

    def apply_gate(self, index):
        if index >= len(self.diagram):
            return
        gate, targets, controls = self.diagram[index]

        if gate in ["H", "X", "Y", "Z"]:
            self.state = apply_single_qubit_gate(
                self.state, {"H": H, "X": X, "Y": Y, "Z": Z}[gate], targets[0], self.n)
        elif gate == "CNOT":
            self.state = cnot_on_n_qubits(control=controls[0], target=targets[0], n_qubits=self.n) @ self.state
        elif gate == "TOFFOLI":
            self.state = toffoli_on_n_qubits(control1=controls[0], control2=controls[1],
                                             target=targets[0], n_qubits=self.n) @ self.state
        elif gate == "MEASURE":
            q = targets[0]
            probs = np.abs(self.state.flatten())**2
            outcome = self.measure_qubit(probs, q)
            self.measurements[q] = outcome
            self.state = self.collapse_state(q, outcome)


    def measure_qubit(self, probs, qubit):
        """Return simulated measurement result (0 or 1) for given qubit"""
        n = self.n
        outcome_probs = [0, 0]
        for i, p in enumerate(probs):
            bit = (i >> (n-1-qubit)) & 1
            outcome_probs[bit] += p
        return 0 if random.random() < outcome_probs[0] else 1

    def collapse_state(self, qubit, outcome):
        """Collapse the state vector to the outcome on the given qubit"""
        new_state = self.state.copy()
        n = self.n
        for i in range(len(new_state)):
            bit = (i >> (n-1-qubit)) & 1
            if bit != outcome:
                new_state[i] = 0
        norm = np.linalg.norm(new_state)
        return new_state / norm if norm > 0 else new_state

    def reset(self):
        self.state = zero_state(self.n)
        self.step_index = -1
        self.measurements = {}


class QuantumGUI:
    def __init__(self, root, circuit: Circuit):
        self.root = root
        self.circuit = circuit
        self.root.title("Quantum Circuit Simulator")
        self.root.configure(bg=BG_COLOR)

        # Zoom scale factor
        self.scale = 1.0

        # Screen size
        self.screen_width = root.winfo_screenwidth()
        self.screen_height = root.winfo_screenheight()

        # Toolbox
        self.toolbox_frame = tk.Frame(root, bg=BG_COLOR)
        self.toolbox_frame.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.create_toolbox()

        # Scrollable canvas
        self.canvas_frame = tk.Frame(root, bg=BG_COLOR)
        self.canvas_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.canvas = tk.Canvas(self.canvas_frame, bg="white", width=800, height=circuit.n * CELL_HEIGHT + 100)
        self.canvas.pack(side="left", fill="both", expand=True)

        # Scrollbars
        self.hbar = tk.Scrollbar(self.canvas_frame, orient="horizontal", command=self.canvas.xview)
        self.vbar = tk.Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.config(xscrollcommand=self.hbar.set, yscrollcommand=self.vbar.set)

        # Controls
        self.control_frame = tk.Frame(root, bg=BG_COLOR)
        self.control_frame.grid(row=2, column=0, pady=10, sticky="w")
        self.create_control_buttons()

        # Probability visualization
        self.fig, self.ax = plt.subplots(figsize=(6,2), facecolor=BG_COLOR)
        self.ax.tick_params(colors=FG_COLOR)
        self.ax.spines['bottom'].set_color(FG_COLOR)
        self.ax.spines['top'].set_color(FG_COLOR)
        self.ax.spines['left'].set_color(FG_COLOR)
        self.ax.spines['right'].set_color(FG_COLOR)
        self.prob_canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.prob_canvas.get_tk_widget().grid(row=3, column=0)

        # Measurement results label
        self.measure_label = tk.Label(root, text="Measurements: None", bg=BG_COLOR, fg=FG_COLOR, font=(FONT_FAMILY, FONT_SIZE_NORMAL))
        self.measure_label.grid(row=4, column=0, pady=10)

        self.update_canvas()

    def create_toolbox(self):
        gates = ["H", "X", "Y", "Z", "CNOT", "TOFFOLI", "MEASURE"]
        for i, g in enumerate(gates):
            b = tk.Button(self.toolbox_frame, text=g, width=8, command=lambda gate=g: self.add_gate_gui(gate),
                          bg=BUTTON_BG, fg=BUTTON_FG, font=(FONT_FAMILY, FONT_SIZE_NORMAL))
            b.grid(row=0, column=i, padx=5)

    def create_control_buttons(self):
        buttons = [
            ("Previous Gate", self.prev_gate),
            ("Next Gate", self.next_gate),
            ("Reset", self.reset_circuit),
            ("Zoom In (+)", self.zoom_in),
            ("Zoom Out (-)", self.zoom_out),
            ("Reset Zoom", self.reset_zoom)
        ]
        for i, (text, command) in enumerate(buttons):
            b = tk.Button(self.control_frame, text=text, command=command,
                          bg=BUTTON_BG, fg=BUTTON_FG, font=(FONT_FAMILY, FONT_SIZE_NORMAL))
            b.grid(row=0, column=i, padx=5)

    def add_gate_gui(self, gate):
        n = self.circuit.n
        if gate in ["H", "X", "Y", "Z", "MEASURE"]:
            target = self.ask_qubit(f"Select target qubit (0 to {n-1}) for {gate}:")
            if target is None: return
            self.circuit.add_gate(gate, targets=[target])
        elif gate == "CNOT":
            control = self.ask_qubit(f"Select control qubit (0 to {n-1}) for CNOT:")
            if control is None: return
            target = self.ask_qubit(f"Select target qubit (0 to {n-1}) for CNOT:")
            if target is None: return
            self.circuit.add_gate(gate, targets=[target], controls=[control])
        elif gate == "TOFFOLI":
            c1 = self.ask_qubit(f"Select first control qubit (0 to {n-1}) for TOFFOLI:")
            if c1 is None: return
            c2 = self.ask_qubit(f"Select second control qubit (0 to {n-1}) for TOFFOLI:")
            if c2 is None: return
            target = self.ask_qubit(f"Select target qubit (0 to {n-1}) for TOFFOLI:")
            if target is None: return
            self.circuit.add_gate(gate, targets=[target], controls=[c1,c2])
        self.update_canvas()

    def ask_qubit(self, prompt):
        answer = simpledialog.askinteger("Input", prompt)
        n = self.circuit.n
        if answer is None or not (0 <= answer < n):
            messagebox.showwarning("Invalid Input", f"Please enter a number between 0 and {n-1}")
            return None
        return answer

    def update_canvas(self):
        self.canvas.delete("all")
        self.canvas.configure(bg=BG_COLOR)
        n = self.circuit.n

        # Apply scaling
        sw = int((len(self.circuit.diagram) * (CELL_WIDTH + GATE_SPACING) + 100) * self.scale)
        sh = int((n * CELL_HEIGHT + 100) * self.scale)

        # Scrollbars control
        if sw < self.screen_width - 100:
            self.canvas.config(width=sw)
            self.hbar.pack_forget()
        else:
            self.canvas.config(width=self.screen_width - 100)
            self.hbar.pack(side="bottom", fill="x")
            self.canvas.config(scrollregion=(0, 0, sw, sh))

        if sh < self.screen_height - 200:
            self.canvas.config(height=sh)
            self.vbar.pack_forget()
        else:
            self.canvas.config(height=self.screen_height - 200)
            self.vbar.pack(side="right", fill="y")
            self.canvas.config(scrollregion=(0, 0, sw, sh))

        # Draw wires
        for i in range(n):
            y = int((30 + i * CELL_HEIGHT) * self.scale)
            self.canvas.create_line(50*self.scale, y, sw - 50*self.scale, y, width=2, fill=FG_COLOR)

        # Draw gates
        for col, gate_info in enumerate(self.circuit.diagram):
            gate, targets, controls = gate_info
            x = int((50 + col * (CELL_WIDTH + GATE_SPACING)) * self.scale)

            for c in controls:
                y = int((30 + c * CELL_HEIGHT) * self.scale)
                self.canvas.create_oval(x+15*self.scale, y-5*self.scale,
                                        x+25*self.scale, y+5*self.scale,
                                        fill=CONTROL_COLOR)

            if controls and targets:
                y1 = int((30 + min(controls + targets) * CELL_HEIGHT) * self.scale)
                y2 = int((30 + max(controls + targets) * CELL_HEIGHT) * self.scale)
                self.canvas.create_line(x+20*self.scale, y1, x+20*self.scale, y2, width=2, fill=FG_COLOR)

            for t in targets:
                y = int((30 + t * CELL_HEIGHT) * self.scale)
                if gate == "MEASURE":
                    self.canvas.create_rectangle(x-15*self.scale, y-15*self.scale,
                                                 x+45*self.scale, y+15*self.scale,
                                                 fill=MEASURE_COLOR, outline="black", width=2)
                    self.canvas.create_text(x+15*self.scale, y, text="M",
                                            font=(FONT_FAMILY, int(FONT_SIZE_BOLD*self.scale), "bold"))
                else:
                    self.canvas.create_rectangle(x-15*self.scale, y-15*self.scale,
                                                 x+45*self.scale, y+15*self.scale,
                                                 fill=GATE_COLOR, outline="black", width=2)
                    self.canvas.create_text(x+15*self.scale, y, text=gate,
                                            font=(FONT_FAMILY, int(FONT_SIZE_BOLD*self.scale), "bold"))

        self.update_probabilities()
        self.update_measurements()

    def update_probabilities(self):
        self.ax.clear()
        probs = np.abs(self.circuit.state.flatten())**2
        self.ax.bar(range(len(probs)), probs, color=GATE_COLOR)
        self.ax.set_ylim(0,1)
        self.ax.set_ylabel("Probability", color=FG_COLOR)
        self.ax.set_xlabel("Basis state", color=FG_COLOR)
        self.ax.set_facecolor(BG_COLOR)
        self.fig.patch.set_facecolor(BG_COLOR)
        self.prob_canvas.draw()

    def update_measurements(self):
        if self.circuit.measurements:
            text = ", ".join([f"q{q}={r}" for q,r in self.circuit.measurements.items()])
        else:
            text = "None"
        self.measure_label.config(text=f"Measurements: {text}")

    def next_gate(self):
        if self.circuit.step_index+1 >= len(self.circuit.diagram):
            messagebox.showinfo("Info", "No more gates to apply.")
            return
        self.circuit.step_index += 1
        self.circuit.apply_gate(self.circuit.step_index)
        self.update_canvas()

    def prev_gate(self):
        if self.circuit.step_index < 0:
            messagebox.showinfo("Info", "At initial state.")
            return
        self.circuit.reset()
        for i in range(self.circuit.step_index):
            self.circuit.apply_gate(i)
        self.circuit.step_index -= 1
        self.update_canvas()

    def reset_circuit(self):
        self.circuit.reset()
        self.update_canvas()

    # Zoom functions
    def zoom_in(self):
        self.scale *= 1.2
        self.update_canvas()

    def zoom_out(self):
        self.scale /= 1.2
        if self.scale < 0.3:  # prevent too tiny
            self.scale = 0.3
        self.update_canvas()

    def reset_zoom(self):
        self.scale = 1.0
        self.update_canvas()


def start_quantum_gui(parent, n_qubits):
    circuit = Circuit(n_qubits)
    new_win = tk.Toplevel(parent)
    gui = QuantumGUI(new_win, circuit)

def start_quantum_gui_with_bell_state(parent, n_qubits):
    circuit = Circuit(n_qubits)
    circuit.add_gate("H", targets=[0])
    circuit.add_gate("CNOT", targets=[1], controls=[0])
    new_win = tk.Toplevel(parent)
    gui = QuantumGUI(new_win, circuit)

if __name__ == "__main__":
    # This part is for standalone execution, e.g., for testing
    # You can set a default number of qubits here if you want to run it directly
    root = tk.Tk()
    n_qubits = simpledialog.askinteger("Qubits", "Enter the number of qubits:", initialvalue=2)
    if n_qubits:
        start_quantum_gui(root, n_qubits)
    root.mainloop()
