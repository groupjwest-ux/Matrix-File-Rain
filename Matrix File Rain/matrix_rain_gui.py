#!/usr/bin/env python3
"""
matrix_rain_gui.py
===================

This script provides a simple graphical user interface for visualising the
contents of any binary file as a Matrix‑style digital rain effect.  A user can
choose a file via a standard open dialog, and its bytes are then read and
displayed as falling streams of characters.  The application uses Python's
built‑in ``tkinter`` library for the GUI, so it should run on any platform
where Tkinter is available (Linux, Windows, macOS).  The digital rain effect
uses a monospace font on a black canvas with green text, echoing the visual
language of the Matrix movies【685889069379834†L133-L139】.  Each vertical stream
represents a sequence of bytes from the selected file.  Streams may be one
character wide (ASCII mode) or two characters wide (hexadecimal mode), and
mixed mode randomly alternates between the two.  The application cycles
through the file contents repeatedly, so the rain effect continues
indefinitely even for small files.  Non‑printable characters in ASCII mode are
rendered as periods (``'.'``) just as in conventional hex dump tools【284123663540210†L55-L58】.

To run the application, simply execute this file with Python 3:

    python3 matrix_rain_gui.py

You'll be presented with a window containing a button to open a file and a
dropdown to select the display mode (ASCII, Hex or Mixed).  After choosing a
file, the digital rain begins immediately on the canvas.  Pressing the
``Open File`` button again resets the rain with the new file.  Close the
window to exit the program.

"""

import os
import random
import string
import tkinter as tk
from tkinter import filedialog, ttk, font


class MatrixRainGUI(tk.Tk):
    """A GUI application that renders file bytes as Matrix‑style digital rain."""

    def __init__(self):
        super().__init__()
        self.title("Matrix Rain File Viewer")
        # Set a reasonable default size; users can resize the window as desired.
        self.geometry("800x600")
        # Configure the window background to black for contrast
        self.configure(bg="black")

        # Initialize file data storage
        self.file_data: bytes | None = None
        self.file_size: int = 0

        # Animation parameters
        self.update_delay = 50  # milliseconds between frames; lower is faster
        self.min_tail = 5       # minimum length of the trailing rain
        self.max_tail = 15      # maximum length of the trailing rain

        # Drop structures will be created once a file is loaded
        self.drops: list[dict] = []
        self.drop_items: list[list[int]] = []
        self.running = False

        # Build the UI
        self._create_widgets()

        # Font for rendering characters; use a monospace font so characters align
        self.font = font.Font(family="Courier", size=14)
        # Precompute the width and height of a single character.  The measured
        # values will be used to position text precisely on the canvas.
        self.char_width = self.font.measure("0")
        # ``linespace`` returns the total height of the character cell, which
        # includes space for ascenders and descenders.
        self.char_height = self.font.metrics("linespace")

        # Schedule a delayed initialisation of geometry‑dependent values.  The
        # canvas isn't fully sized until the mainloop has started; after idle
        # tasks run, ``_init_canvas_dimensions`` will populate geometry values.
        self.after(100, self._init_canvas_dimensions)

    def _create_widgets(self) -> None:
        """Create the control panel and canvas widgets."""
        # Create a top frame to hold controls
        control_frame = ttk.Frame(self)
        control_frame.pack(side=tk.TOP, fill=tk.X, pady=(10, 0))

        # Open file button
        open_button = ttk.Button(control_frame, text="Open File…", command=self.open_file)
        open_button.pack(side=tk.LEFT, padx=(10, 5))

        # Mode selection: ASCII, Hex, Mixed
        ttk.Label(control_frame, text="Display Mode:").pack(side=tk.LEFT, padx=(5, 2))
        self.mode_var = tk.StringVar(value="mixed")
        mode_select = ttk.Combobox(control_frame, textvariable=self.mode_var, state="readonly",
                                   values=["ascii", "hex", "mixed"])
        mode_select.pack(side=tk.LEFT, padx=(0, 10))
        mode_select.bind("<<ComboboxSelected>>", lambda e: self._reset_rain())

        # Canvas for drawing the rain effect
        # The canvas background is black to emulate the film's aesthetic【685889069379834†L133-L139】.
        self.canvas = tk.Canvas(self, bg="black", highlightthickness=0)
        self.canvas.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    def _init_canvas_dimensions(self) -> None:
        """Compute the number of columns and rows based on the current canvas size."""
        # Determine canvas size in pixels
        width_px = max(1, self.canvas.winfo_width())
        height_px = max(1, self.canvas.winfo_height())
        # Determine how many character positions fit horizontally and vertically
        self.cols = width_px // self.char_width
        self.rows = height_px // self.char_height
        # Initialize drop state if a file has already been loaded
        if self.file_data is not None:
            self._create_drops()

    def open_file(self) -> None:
        """Prompt the user to select a file and start the rain effect."""
        filename = filedialog.askopenfilename(title="Select a file to view")
        if not filename:
            return
        try:
            with open(filename, "rb") as f:
                data = f.read()
        except OSError as e:
            tk.messagebox.showerror("Error", f"Failed to open file: {e}")
            return
        if not data:
            tk.messagebox.showwarning("Warning", "Selected file is empty.")
            return
        self.file_data = data
        self.file_size = len(data)
        self._reset_rain()

    def _reset_rain(self) -> None:
        """Clear existing drops and restart the rain effect."""
        # Cancel any scheduled update calls
        if hasattr(self, "_after_id") and self._after_id:
            self.after_cancel(self._after_id)
        # Clear the canvas
        self.canvas.delete("all")
        # Reset drop structures
        self.drops = []
        self.drop_items = []
        if self.file_data is None:
            return
        # Compute current canvas dimensions (in case of resize)
        self._init_canvas_dimensions()
        # Create new drops based on selected mode and canvas size
        self._create_drops()
        # Start the animation loop
        self.running = True
        self._update_rain()

    def _create_drops(self) -> None:
        """Initialise drop objects across the canvas columns."""
        # Ensure that we have at least one column and one row
        if self.cols < 1 or self.rows < 1:
            return
        mode = self.mode_var.get()
        # Track occupied columns to avoid overlapping drops (especially hex mode
        # which occupies two columns).
        occupied = [False] * self.cols
        self.drops.clear()
        self.drop_items.clear()
        x = 0
        # Loop through potential column positions
        while x < self.cols:
            # Randomly decide whether to place a drop at this column
            if random.random() < 0.5:
                # Determine width based on selected mode
                if mode == "hex":
                    width = 2
                elif mode == "ascii":
                    width = 1
                else:  # mixed
                    # In mixed mode randomly choose 1 or 2, but ensure hex fits
                    if random.choice([True, False]) and x < self.cols - 1:
                        width = 2
                    else:
                        width = 1
                # If not enough space remains for a hex drop, skip to next column
                if width == 2 and x >= self.cols - 1:
                    x += 1
                    continue
                # Check that required columns are free
                if any(occupied[x:x + width]):
                    x += 1
                    continue
                # Mark columns as used
                for i in range(width):
                    occupied[x + i] = True
                # Create the drop dictionary
                drop = {
                    "x": x,                      # column index
                    "y": -random.randint(0, self.rows),  # start above the top
                    "width": width,              # 1 for ASCII, 2 for hex
                    "tail": random.randint(self.min_tail, self.max_tail),
                    "index": random.randrange(self.file_size),  # file index
                    "mode": mode                # store mode for drop
                }
                # For mixed mode, override per-drop mode
                if mode == "mixed":
                    drop["mode"] = random.choice(["ascii", "hex"])
                self.drops.append(drop)
                self.drop_items.append([])
                # Advance past the width of this drop
                x += width
            else:
                x += 1

    def _update_rain(self) -> None:
        """Update all drops and schedule the next frame."""
        if not self.running:
            return
        # Loop over each drop and update its state
        for i, drop in enumerate(self.drops):
            # If the drop has completely scrolled off the bottom, reset it
            if drop["y"] - drop["tail"] >= self.rows:
                # Randomly pick a new width based on global mode
                global_mode = self.mode_var.get()
                width = drop["width"]
                if global_mode == "mixed":
                    width = random.choice([1, 2])
                    if width == 2 and self.cols < 2:
                        width = 1
                elif global_mode == "ascii":
                    width = 1
                elif global_mode == "hex":
                    width = 2
                drop["width"] = width
                # Find a new x position that fits
                max_x = max(0, self.cols - width)
                drop["x"] = random.randint(0, max_x) if max_x > 0 else 0
                # Reset y, tail and file index
                drop["y"] = -random.randint(0, self.rows)
                drop["tail"] = random.randint(self.min_tail, self.max_tail)
                drop["index"] = random.randrange(self.file_size)
                # Update mode per drop
                if global_mode == "mixed":
                    drop["mode"] = random.choice(["ascii", "hex"])
                else:
                    drop["mode"] = global_mode
                # Delete any existing canvas items for this drop
                for item_id in self.drop_items[i]:
                    self.canvas.delete(item_id)
                self.drop_items[i] = []
                continue
            # Move the head of the drop down one row
            drop["y"] += 1
            # Draw the new head if it is on screen
            if 0 <= drop["y"] < self.rows:
                byte = self.file_data[drop["index"]]
                if drop["mode"] == "ascii":
                    # Render printable characters, otherwise use '.'
                    ch = chr(byte) if chr(byte) in string.printable and chr(byte) not in "\x0b\x0c" else '.'
                    text = ch
                else:
                    # Two‑digit hexadecimal string
                    text = f"{byte:02X}"
                # Calculate pixel coordinates
                x_px = drop["x"] * self.char_width
                y_px = drop["y"] * self.char_height
                # Create the text item; anchor northwest to align to grid
                item_id = self.canvas.create_text(
                    x_px,
                    y_px,
                    anchor='nw',
                    text=text,
                    fill='green',
                    font=self.font
                )
                # Append to the drop's item list
                self.drop_items[i].append(item_id)
                # Advance file index and wrap around
                drop["index"] = (drop["index"] + 1) % self.file_size
            # Remove items that have fallen beyond the tail
            # We maintain the list of item IDs; when its length exceeds the
            # tail length we delete the oldest.
            while len(self.drop_items[i]) > drop["tail"]:
                old_item = self.drop_items[i].pop(0)
                self.canvas.delete(old_item)
        # Schedule the next frame
        self._after_id = self.after(self.update_delay, self._update_rain)


def main() -> None:
    app = MatrixRainGUI()
    app.mainloop()


if __name__ == "__main__":
    main()