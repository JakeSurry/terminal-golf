import numpy as np
from scipy.interpolate import CubicSpline
from perlin_noise import PerlinNoise  # pip install perlin-noise
import time
from PIL import Image

class GolfCourse:
    def __init__(self, length=400, width=50, bends=0):
        self.length = length # Length of course
        self.width = width # Width of fairway
        self.bends = bends + 2 # How curvy the fairway will be
        
        # Grid dimensions
        self.grid_x = length
        self.grid_z = width * 3  # extra space for rough
        
        # Heightmap (y-values at each x,z position)
        self.heights = np.zeros((self.grid_z, self.grid_x))
        
        # Centerline of fairway
        self.centerline = None
        self.fairway_width = None
    
    def _generate_centerline(self):
        """Create curved fairway path"""    
        x_points = np.linspace(0, self.length, self.bends) # x position where bends occur
        z_points = np.random.randn(self.bends) * 20 + (self.grid_z // 2) # z position at the apex of bend

        # Start and end centerline in the middle of the course
        z_points[0] = self.grid_z // 2  
        z_points[-1] = self.grid_z // 2 
        
        # Smooth with cubic spline (lerp on crack)
        spline = CubicSpline(x_points, z_points)
        
        # Get center line position every one yard
        x_samples = np.arange(0, self.length)
        z_samples = spline(x_samples)
        
        # Store centerline z pos with respective x pos
        self.centerline = np.column_stack([x_samples, z_samples])
        
    def _define_fairway(self):
        """Define fairway width along the centerline"""
        # Vary width - narrower at doglegs, wider on straights
        num_points = len(self.centerline)
        
        self.fairway_width = np.ones(num_points) * self.width
        
    def _generate_terrain(self, seed):
        """Generate height values using Perlin noise"""
        # Create noise generator with octaves for detail
        noise = PerlinNoise(4, seed)
        
        scale = 100.0  # larger = smoother terrain
        
        for z in range(self.grid_z):
            for x in range(self.grid_x):
                # Generate noise value (returns values roughly in [-0.5, 0.5])
                height = noise([x/scale, z/scale])
                self.heights[z, x] = height * 10  # scale to meters
                
    def generate(self, seed=None):
        np.random.seed = seed
        start_time = time.time()

        task_time = time.time()
        print('Generating centerline...')
        self._generate_centerline()
        print(f'Task completed in {time.time()-task_time} seconds!') 

        task_time = time.time()
        print('Generating fairway bounds...')        
        self._define_fairway()
        print(f'Task completed in {time.time()-task_time} seconds!') 
        
        task_time = time.time()
        print('Generating terrain height...')        
        self._generate_terrain(seed)
        print(f'Task completed in {time.time()-task_time} seconds!') 
        
        print(f'Course complete! Total generation time: {time.time()-start_time} seconds!')

    def get_height(self, x, z):
        """Get terrain height at world position (x, z)"""
        # Bounds check
        if 0 <= z < self.grid_z and 0 <= x < self.grid_x:
            return self.heights[z, x]
        return 0.0
        
    def get_slope(self, x, z):
        """Get terrain slope at position (returns dx, dz gradients)"""
        h = self.get_height(x, z)
        h_x = self.get_height(x + 1, z)
        h_z = self.get_height(x, z + 1)
        
        dx = (h_x - h)
        dz = (h_z - h)
        
        return dx, dz
    
    def is_on_fairway(self, x, z):
        """Check if position is on fairway vs rough"""
        # Find nearest centerline point
        if x >= len(self.centerline):
            return False

        center_z = self.centerline[x, 1]
        width = self.fairway_width[x]
        
        # Check lateral distance from centerline
        distance = abs(z - center_z)
        return distance < width / 2

# Usage example
course = GolfCourse(bends=2) 
course.generate(seed=67)  # Use seed for reproducible courses

# Physics calculations
ball_x, ball_z = 150, 75
height = course.get_height(ball_x, ball_z)
slope_x, slope_z = course.get_slope(ball_x, ball_z)
on_fairway = course.is_on_fairway(ball_x, ball_z)

print(f"Height: {height:.2f}y")
print(f"Slope: ({slope_x:.3f}, {slope_z:.3f})")
print(f"On fairway: {on_fairway}")

# height_image = []
# for row in course.heights:
#     row_list = []
#     for cell in row:
#         if cell >=0:
#             row_list.append((0, cell*50, 0))
#         else:
#             row_list.append((abs(cell)*50, 0, 0))
#     height_image.append(row_list)

# arr_np = np.array(height_image, dtype=np.uint8)

# Image.fromarray(arr_np, mode='RGB').show()

fairway_bounds = []
for z in range(course.grid_z-1):
    row = []
    for x in range(course.grid_x-1):
        if course.is_on_fairway(x, z):
            row.append((0, 200, 50))
        else:
            row.append((0, 0, 0))
    fairway_bounds.append(row)
    
arr_np = np.array(fairway_bounds, dtype=np.uint8)

Image.fromarray(arr_np, mode='RGB').show()
