import tkinter as tk
from tkinter import filedialog, messagebox
from voronoi.voronoi import Voronoi
from random import randint
from collections import Counter

class MainWindow:
    RADIUS, LOCK_FLAG, CANVAS_WIDTH, CANVAS_HEIGHT, BUTTON_WIDTH = 3, False, 650, 500, 25
    
    def __init__(self, master):
        self.master = master
        self.master.title("Fortune's Voronoi")
        self.master.resizable(False, False)
        
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        x = (screen_width - self.CANVAS_WIDTH) // 2
        y = (screen_height - self.CANVAS_HEIGHT - 40) // 2
        
        self.master.geometry(f'{self.CANVAS_WIDTH}x{self.CANVAS_HEIGHT+40}+{x}+{y}')

        self.frmMain = tk.Frame(self.master, relief=tk.RAISED, borderwidth=1)
        self.frmMain.pack(fill=tk.BOTH, expand=1)

        self.w = tk.Canvas(self.frmMain, width=self.CANVAS_WIDTH, height=self.CANVAS_HEIGHT, bg='white')
        self.w.bind('<Button-1>', self.onClick)
        self.w.pack()

        self.frmButton = tk.Frame(self.master)
        self.frmButton.pack()
        
        buttons = [
            ('Calculate', self.onClickCalculate),
            ('Calculate with Noise', self.onClickCalculateWithNoise),
            ('Clear', self.onClickClear),
            ('Load Points', self.onClickLoad)
        ]
        
        for i, (text, command) in enumerate(buttons):
            button = tk.Button(self.frmButton, text=text, width=self.BUTTON_WIDTH, command=command)
            button.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")

        self.frmButton.grid_columnconfigure(tuple(range(len(buttons))), weight=1)

        self.points = []

    def onClickCalculate(self):
        if not self.points:
            messagebox.showwarning("No Points", "No points to calculate Voronoi diagram")
            return

        if not self.LOCK_FLAG:
            self.LOCK_FLAG = True
            self.w.delete("segments", "circle")

            points = self.points
            
            try:
                vp = Voronoi(points)
                vp.process()
                segments = vp.get_segments()
                if segments:
                    self.drawLinesOnCanvas(segments)

                largest_circle = vp.find_largest_empty_circle()
                if largest_circle:
                    self.drawCircleOnCanvas(largest_circle)
            except Exception as e:
                messagebox.showerror("Calculation Error", f"An error occurred during calculation:\n\n{e}")
            finally:
                self.LOCK_FLAG = False

    def onClickCalculateWithNoise(self):
        if not self.points:
            messagebox.showwarning("No Points", "No points to calculate Voronoi diagram")
            return

        if not self.LOCK_FLAG:
            self.LOCK_FLAG = True
            self.w.delete("segments", "circle")
            points = [(x, y + 1e-9 * randint(1,i+1)) for i, (x, y) in enumerate(self.points)]
            
            try:
                vp = Voronoi(points)
                vp.process()
                segments = vp.get_segments()
                if segments:
                    self.drawLinesOnCanvas(segments)

                largest_circle = vp.find_largest_empty_circle()
                if largest_circle:
                    self.drawCircleOnCanvas(largest_circle)
            except Exception as e:
                messagebox.showerror("Calculation Error", f"An error occurred during calculation:\n\n{e}")
            finally:
                self.LOCK_FLAG = False

    def onClickClear(self):
        self.LOCK_FLAG = False
        self.w.delete("all")
        self.points.clear()

    def onClick(self, event):
        if not self.LOCK_FLAG:
            self.points.append((event.x, event.y))
            self.w.create_oval(event.x-self.RADIUS, event.y-self.RADIUS, event.x+self.RADIUS, event.y+self.RADIUS, fill="black")

    def onClickLoad(self):
        filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if filename:
            self.onClickClear()
            error_messages = []
            temp_points = []
            
            with open(filename, 'r') as file:
                for line_num, line in enumerate(file, 1):
                    try:
                        parts = line.strip().split()
                        if len(parts) != 2:
                            raise ValueError(f"Line {line_num}: Expected 2 values, got {len(parts)}")
                        x, y = map(float, parts)
                        if not (0 <= x <= self.CANVAS_WIDTH and 0 <= y <= self.CANVAS_HEIGHT):
                            raise ValueError(f"Line {line_num}: Coordinates out of bounds (0-{self.CANVAS_WIDTH})")
                        temp_points.append((x, y))
                    except ValueError as e:
                        error_messages.append(str(e))
            self.points_set = set(temp_points)
            self.points = list(self.points_set)
            self.points = sorted(self.points, key=lambda point: (point[0], point[1]))
            
            for x, y in self.points:
                self.w.create_oval(x-self.RADIUS, y-self.RADIUS, x+self.RADIUS, y+self.RADIUS, fill="black")
            
            if error_messages:
                messagebox.showerror("Input Error", "The following errors occurred:\n\n" + "\n".join(error_messages))

    def drawLinesOnCanvas(self, segments):
        for s in segments:
            self.w.create_line(*s, fill='purple', tags="segments")

    def drawCircleOnCanvas(self, largest_circle):
        for ox, oy, radius in largest_circle:
            self.w.create_oval(ox - radius, oy - radius, ox + radius, oy + radius, outline="red", width=2, tags="circle")

def main(): 
    root = tk.Tk()
    MainWindow(root)
    root.mainloop()

if __name__ == '__main__':
    main()