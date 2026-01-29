import tkinter as tk
import time
import random

# ---------------- CONFIG ----------------
WIDTH = 1100
HEIGHT = 520
TOP_MARGIN = 80
BAR_WIDTH = 32

SIDE_GAP = 35
PIVOT_GAP = 25

MAX_DELAY = 1.0     # slowest
MIN_DELAY = 0.05    # fastest
FINAL_DELAY = 2.0
# ----------------------------------------


class QuickSortVisualizer:
    def __init__(self, arr):
        self.arr = arr
        self.n = len(arr)
        self.active_calls = 0

        self.paused = False
        self.delay = 0.35   # actual delay used internally

        self.root = tk.Tk()
        self.root.title("Quick Sort Visualization – Interactive")

        # ---------- UI CONTROLS ----------
        control_frame = tk.Frame(self.root)
        control_frame.pack(fill="x", pady=5)

        tk.Label(control_frame, text="Speed (Slow ⟶ Fast)").pack(side="left", padx=5)

        self.speed_slider = tk.Scale(
            control_frame,
            from_=0,
            to=100,
            orient="horizontal",
            length=250,
            command=self.update_speed
        )
        self.speed_slider.set(65)  # default speed
        self.speed_slider.pack(side="left")

        self.pause_btn = tk.Button(
            control_frame,
            text="Pause",
            width=10,
            command=self.toggle_pause
        )
        self.pause_btn.pack(side="left", padx=10)

        # ---------- CANVAS ----------
        self.canvas = tk.Canvas(self.root, width=WIDTH, height=HEIGHT, bg="white")
        self.canvas.pack()

        self.max_val = max(abs(x) for x in self.arr)
        self.zero_y = (HEIGHT + TOP_MARGIN) // 2

        self.draw_bars(note="Starting Quick Sort")
        self.root.after(1000, lambda: self.quick_sort(0, self.n - 1))
        self.root.mainloop()

    # ---------- CONTROLS ----------
    def update_speed(self, val):
        """
        Slider value increases -> animation speed increases
        Internally converts speed to delay
        """
        speed_ratio = int(val) / 100
        self.delay = MAX_DELAY - speed_ratio * (MAX_DELAY - MIN_DELAY)

    def toggle_pause(self):
        self.paused = not self.paused
        self.pause_btn.config(text="Resume" if self.paused else "Pause")

    def wait(self, extra=0.0):
        while self.paused:
            self.root.update()
            time.sleep(0.1)
        time.sleep(self.delay + extra)

    # ---------- DRAW ----------
    def draw_bars(self, low=None, high=None, pivot=None,
                  i=None, j=None, swap=None,
                  note="", final=False):

        self.canvas.delete("all")

        self.canvas.create_text(
            WIDTH // 2,
            TOP_MARGIN // 2,
            text=note,
            font=("Arial", 16, "bold")
        )

        self.canvas.create_line(0, self.zero_y, WIDTH, self.zero_y, fill="black")

        x_pos = 50

        for idx, val in enumerate(self.arr):

            if not final:
                if low is not None and idx == low:
                    x_pos += SIDE_GAP
                if pivot is not None and idx == pivot:
                    x_pos += PIVOT_GAP

            x0 = x_pos
            x1 = x0 + BAR_WIDTH

            height = (abs(val) / self.max_val) * 180
            y0, y1 = (
                (self.zero_y - height, self.zero_y)
                if val >= 0 else
                (self.zero_y, self.zero_y + height)
            )

            color = "lightgray"
            label = ""

            if not final and low is not None and high is not None:
                if idx < low or idx > high:
                    color = "#dddddd"

            if swap and idx in swap:
                color = "orange"
                label = "SWAP"
            elif idx == pivot and not final:
                color = "red"
                label = "PIVOT"
            elif idx == i:
                color = "green"
                label = "i"
            elif idx == j:
                color = "blue"
                label = "j"

            if final:
                color = "#4CAF50"

            self.canvas.create_rectangle(x0, y0, x1, y1, fill=color)
            self.canvas.create_text(
                x0 + BAR_WIDTH // 2,
                y0 - 12 if val >= 0 else y1 + 12,
                text=str(val),
                font=("Arial", 10, "bold")
            )

            if label:
                self.canvas.create_text(
                    x0 + BAR_WIDTH // 2,
                    TOP_MARGIN + 5,
                    text=label,
                    fill=color,
                    font=("Arial", 10, "bold")
                )

            x_pos += BAR_WIDTH + 6

            if not final and high is not None and idx == high:
                x_pos += SIDE_GAP

        self.root.update()

    # ---------- PARTITION ----------
    def partition(self, low, high):
        pivot = self.arr[low]
        i = low + 1
        j = high

        self.draw_bars(low, high, pivot=low, i=i, j=j, note="Pivot selected")
        self.wait()

        while True:
            while i <= j and self.arr[i] <= pivot:
                self.draw_bars(low, high, pivot=low, i=i, j=j, note="Moving i →")
                self.wait()
                i += 1

            while i <= j and self.arr[j] > pivot:
                self.draw_bars(low, high, pivot=low, i=i, j=j, note="Moving j ←")
                self.wait()
                j -= 1

            if i > j:
                break

            self.draw_bars(low, high, pivot=low, i=i, j=j,
                           swap=(i, j), note="Swapping i and j")
            self.wait(extra=0.4)
            self.arr[i], self.arr[j] = self.arr[j], self.arr[i]

        self.draw_bars(low, high, pivot=low, j=j,
                       swap=(low, j), note="Placing pivot")
        self.wait(extra=0.4)
        self.arr[low], self.arr[j] = self.arr[j], self.arr[low]

        return j

    # ---------- QUICK SORT ----------
    def quick_sort(self, low, high):
        if low < high:
            self.active_calls += 1

            p = self.partition(low, high)
            self.quick_sort(low, p - 1)
            self.quick_sort(p + 1, high)

            self.active_calls -= 1

            if self.active_calls == 0:
                self.draw_bars(
                    note="ARRAY FINALLY SORTED",
                    final=True
                )
                self.wait(extra=FINAL_DELAY)


# ---------------- MAIN ----------------
user_input = input(
    "Enter array elements separated by space\n"
    "OR press Enter to generate a random array:\n"
).strip()

if user_input == "":
    arr = [random.randint(-5, 20) for _ in range(15)]
    print("Generated array:", arr)
else:
    arr = list(map(int, user_input.split()))

QuickSortVisualizer(arr)
