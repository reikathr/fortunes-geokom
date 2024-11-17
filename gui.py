import tkinter as tk
from tkinter import filedialog
from voronoi import Voronoi

class MainWindow:
    RADIUS = 3
    LOCK_FLAG = False
    
    def __init__(self, master):
        self.master = master
        self.master.title("Fortune's Voronoi")
        
        # Mengatur ukuran window menjadi fixed/statis
        self.master.resizable(False, False)  # Menonaktifkan kemampuan resize window
        
        # Mendapatkan ukuran layar
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        
        # Menghitung posisi x dan y untuk menempatkan window di tengah
        x = (screen_width/2) - (500/2)
        y = (screen_height/2) - (500/2)
        
        # Mengatur geometri window: 'widthxheight+x+y'
        self.master.geometry('500x540+%d+%d' % (x, y))

        self.frmMain = tk.Frame(self.master, relief=tk.RAISED, borderwidth=1)
        self.frmMain.pack(fill=tk.BOTH, expand=1)

        self.w = tk.Canvas(self.frmMain, width=500, height=500)
        self.w.config(background='white')
        self.w.bind('<Button-1>', self.onClick)  # Single-click to add points
        self.w.pack()

        self.frmButton = tk.Frame(self.master)
        self.frmButton.pack()
        
        self.btnCalculate = tk.Button(self.frmButton, text='Calculate', width=25, command=self.onClickCalculate)
        self.btnCalculate.pack(side=tk.LEFT)
        
        self.btnClear = tk.Button(self.frmButton, text='Clear', width=25, command=self.onClickClear)
        self.btnClear.pack(side=tk.LEFT)
        
        self.btnLoad = tk.Button(self.frmButton, text='Load Points', width=25, command=self.onClickLoad)
        self.btnLoad.pack(side=tk.LEFT)
        
        self.points = []   # To store points for Voronoi calculation

    
    def onClickCalculate(self):
        if not self.points:
            tk.messagebox.showwarning("No Points", "No points to calculate Voronoi diagram")
            return

        if not self.LOCK_FLAG:
            self.LOCK_FLAG = True
            self.w.delete("lines")
            self.w.delete("circle")

            points = self.points.copy()
            epsilon = 1e-6
            points = [(x, y + epsilon * i) for i, (x, y) in enumerate(points)]
            try:
                vp = Voronoi(points)
                vp.process()
                lines = vp.get_output()
                if lines:
                    self.drawLinesOnCanvas(lines)

                largest_circle = vp.find_largest_empty_circle()
                if largest_circle:
                    self.drawCircleOnCanvas(largest_circle)
            except Exception as e:
                tk.messagebox.showerror("Calculation Error", f"An error occurred during calculation:\n\n{str(e)}")
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
            temp_points = []  # Temporary list to store points before sorting
            
            # Read and validate points
            with open(filename, 'r') as file:
                for line_num, line in enumerate(file, 1):
                    try:
                        parts = line.strip().split()
                        if len(parts) != 2:
                            raise ValueError(f"Line {line_num}: Expected 2 values, got {len(parts)}")
                        x, y = map(float, parts)
                        if x < 0 or x > 500 or y < 0 or y > 500:
                            raise ValueError(f"Line {line_num}: Coordinates out of bounds (0-500)")
                        temp_points.append((x, y))
                    except ValueError as e:
                        error_messages.append(str(e))
            
            # Sort points first by x, then by y
            temp_points.sort(key=lambda point: (point[0], point[1]))
            
            # Clear existing points and add sorted points
            self.points = []
            for x, y in temp_points:
                self.points.append((x, y))
                self.w.create_oval(x-self.RADIUS, y-self.RADIUS, 
                                x+self.RADIUS, y+self.RADIUS, 
                                fill="black")
            
            if error_messages:
                error_text = "\n".join(error_messages)
                tk.messagebox.showerror("Input Error", f"The following errors occurred:\n\n{error_text}")
                
    def drawLinesOnCanvas(self, lines):
        for l in lines:
            self.w.create_line(l[0], l[1], l[2], l[3], fill='blue', tags="lines")

    def drawCircleOnCanvas(self, largest_circle):
        if largest_circle:
            for circle in largest_circle:
                ox, oy, radius = circle
                self.w.create_oval(ox - radius, oy - radius, ox + radius, oy + radius, outline="red", width=2, tags="circle")

def main(): 
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()

if __name__ == '__main__':
    main()