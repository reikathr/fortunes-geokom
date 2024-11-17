import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
from scipy.spatial import Voronoi, voronoi_plot_2d
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from typing import List, Tuple
import math

class VoronoiGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Voronoi Diagram Generator")
        
        # Initialize points list
        self.points = []
        
        # Create main frame
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.main_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create buttons frame
        button_frame = tk.Frame(self.main_frame)
        button_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add buttons
        tk.Button(button_frame, text="Load Points", command=self.load_points).pack(pady=5)
        tk.Button(button_frame, text="Clear", command=self.clear).pack(pady=5)
        tk.Button(button_frame, text="Generate", command=self.generate).pack(pady=5)
        
        # Bind mouse click
        self.canvas_widget.bind("<Button-1>", self.add_point)
        
        # Set up the plot
        self.setup_plot()
        
    def setup_plot(self):
        """Initialize the plot with proper settings"""
        self.ax.set_xlim(0, 800)
        self.ax.set_ylim(0, 600)
        self.ax.set_aspect('equal')
        self.ax.grid(True)
        self.canvas.draw()
        
    def add_point(self, event):
        """Add a point where the user clicked"""
        # Convert from screen coordinates to data coordinates
        x = event.x
        y = self.canvas_widget.winfo_height() - event.y  # Invert y coordinate
        
        # Scale coordinates to match plot limits
        x = x * 800 / self.canvas_widget.winfo_width()
        y = y * 600 / self.canvas_widget.winfo_height()
        
        self.points.append([x, y])
        self.update_plot()
        
    def update_plot(self):
        """Update the plot with current points"""
        self.ax.clear()
        self.setup_plot()
        
        if self.points:
            points_array = np.array(self.points)
            self.ax.scatter(points_array[:, 0], points_array[:, 1], c='black', s=20)
            
        self.canvas.draw()
        
    def find_empty_circles(self, vor):
        """Find empty circles passing through three or more sites"""
        circles = []
        vertices = vor.vertices
        ridge_points = vor.ridge_points
        ridge_vertices = vor.ridge_vertices
        
        # Find circles from Voronoi vertices
        for i, vertex in enumerate(vertices):
            # Find all ridges connected to this vertex
            connected_sites = set()
            for j, ridge in enumerate(ridge_vertices):
                if i in ridge:
                    connected_sites.update(ridge_points[j])
                    
            if len(connected_sites) >= 3:
                # Get coordinates of connected sites
                site_coords = vor.points[list(connected_sites)]
                
                # Calculate radius as distance to any connected site
                radius = np.linalg.norm(vertex - site_coords[0])
                
                circles.append((vertex, radius))
                
        return circles
        
    def generate(self):
        """Generate Voronoi diagram"""
        if len(self.points) < 3:
            messagebox.showwarning("Warning", "Need at least 3 points")
            return
            
        try:
            # Convert points to numpy array
            points_array = np.array(self.points)
            
            # Add far points to ensure bounded diagram
            center = points_array.mean(axis=0)
            radius = 2 * np.max(np.linalg.norm(points_array - center, axis=1))
            far_points = self.get_bounding_box_points(center, radius)
            points_with_bounds = np.vstack([points_array, far_points])
            
            # Compute Voronoi diagram
            vor = Voronoi(points_with_bounds)
            
            # Clear the plot and setup again
            self.ax.clear()
            self.setup_plot()
            
            # Plot original points
            self.ax.scatter(points_array[:, 0], points_array[:, 1], c='black', s=20)
            
            # Plot Voronoi edges
            for simplex in vor.ridge_vertices:
                if -1 not in simplex:
                    self.ax.plot(vor.vertices[simplex, 0], vor.vertices[simplex, 1], 'b-')
                    
            # Find and plot empty circles
            circles = self.find_empty_circles(vor)
            for center, radius in circles:
                circle = plt.Circle(center, radius, fill=False, color='red')
                self.ax.add_artist(circle)
                
            self.canvas.draw()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate diagram: {str(e)}")
            
    def get_bounding_box_points(self, center, radius):
        """Generate points for bounding box"""
        x, y = center
        return np.array([
            [x - radius, y - radius],
            [x - radius, y + radius],
            [x + radius, y - radius],
            [x + radius, y + radius]
        ])
        
    def load_points(self):
        """Load points from a text file"""
        filename = filedialog.askopenfilename()
        if filename:
            try:
                points = np.loadtxt(filename)
                if points.shape[1] != 2:
                    raise ValueError("File must contain x y coordinates")
                self.points = points.tolist()
                self.update_plot()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {str(e)}")
                
    def clear(self):
        """Clear all points and reset the plot"""
        self.points = []
        self.ax.clear()
        self.setup_plot()
        self.canvas.draw()

def main():
    root = tk.Tk()
    app = VoronoiGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()