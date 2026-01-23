import numpy as np
np.random.seed(5)

from scipy.interpolate import BSpline, PchipInterpolator, splprep, splev
import matplotlib.pyplot as plt
from matplotlib.path import Path

class Course():
    def __init__(self, par=4, dogleg=False, intensity=1):
        self.par = par
        self.dogleg = dogleg
        self.intensity = intensity 

        self.length = 0
        self.center_line = None
        self.fairway = [[]]
        self.fairway_path = None
        self.green = [[]]
        self.green_path = None

    def _generate_length(self):
        match self.par:
            case 3:
                length = 150
            case 4:
                length = 350
            case 5:
                length = 550

        return length

    def _generate_center_line(self, length):
        inflection_points = 7
        x_points = np.linspace(0, length, inflection_points) # x positions where bends occur
        y_points = np.zeros(inflection_points)
        
        if self.dogleg == True:
            bend_location = 3 # 3 is central
            bend_direction = 1 # 1 arcs up, -1 arcs down
            intensity_scaler = 30 # arbitrary
            bend_intensity = self.intensity * intensity_scaler * bend_direction
            for i in range(1, inflection_points-1):
                y_points[i] = bend_intensity * np.exp(-((i-bend_location)/2)**2)

        center_line_function = PchipInterpolator(x_points, y_points)
        
        return center_line_function

    def _generate_width(self, length):
        degree = 6
        num_control_points = 10
        control_array = np.zeros(num_control_points + degree+1)
        knot_array = np.linspace(0, length, num_control_points+2)
        knot_array = np.concatenate((np.zeros(degree),  \
                                     knot_array,        \
                                     np.full(shape=degree, fill_value=knot_array[-1]))) #Duplicate boundry knots

        min_width = 20
        for i in range(len(control_array)):
            offset = abs(min_width//2 + (min_width//2)*np.random.uniform(low=0.0, high=2.0))
            control_array[i] = offset

        control_array[0] = 0
        control_array[-1] = 0

        width_function = BSpline(knot_array, control_array, degree)

        return width_function
    
    def _generate_fairway_shape(self, length, center_line, top_width, bottom_width):
        curve_sample_resolution = 50
        xx = np.linspace(0, length, curve_sample_resolution)

        top_bound = center_line(xx) + top_width(xx)
        bottom_bound = center_line(xx) - bottom_width(xx)

        fairway_x = np.concatenate((xx, xx[-2:0:-1]))
        fairway_y = np.concatenate((top_bound, bottom_bound[-2:0:-1]))

        shape_generation_resolution = np.linspace(0, 1, 400)
        tck, u = splprep([fairway_x, fairway_y], s=0, per=True)
        fairway = splev(shape_generation_resolution, tck)
        fairway_path = Path(np.column_stack([fairway[0], fairway[1]]))

        return fairway, fairway_path
    
    def _generate_green_shape(self, length, fairway):
        green_start_x = length - 30

        fairway_x_coords = fairway[0]
        fairway_y_coords = fairway[1]
        
        top_mask = (fairway_x_coords[:200] >= green_start_x)
        bottom_mask = (fairway_x_coords[200:] >= green_start_x)

        # MIRROR LATTER HALF OF GREEN FOR FIRST HALF SO ITS ROUND
        
        green_top_x = fairway_x_coords[:200][top_mask]
        green_top_y = fairway_y_coords[:200][top_mask]
        
        green_bottom_x = fairway_x_coords[200:][bottom_mask][::-1]
        green_bottom_y = fairway_y_coords[200:][bottom_mask][::-1]
        
        green = [np.concatenate([green_top_x, green_bottom_x[-2:0:-1]]),
                 np.concatenate([green_top_y, green_bottom_y[-2:0:-1]])]
        
        green_path = Path(np.column_stack((green[0], green[1])))

        return green, green_path
    
    def generate(self):
        length = self._generate_length()
        center_line = self._generate_center_line(length)
        top_width = self._generate_width(length)
        bottom_width = self._generate_width(length)
        fairway, fairway_path = self._generate_fairway_shape(length, center_line, top_width, bottom_width)
        green, green_path = self._generate_green_shape(length, fairway)

        self.center_line = center_line
        self.fairway = fairway
        self.fairway_path = fairway_path
        self.green = green
        self.green_path = green_path

    def on_fairway(self):
        return bool

course = Course(dogleg=True)
course.generate()

center_line = course.center_line
fairway = course.fairway
green = course.green
xx = np.linspace(0, course.length, 50)

fig, ax = plt.subplots()

ax.plot(xx, center_line(xx), 'r-', label='Center Line')
ax.plot(fairway[0], fairway[1], 'b-', linewidth=2, label='Fairway')
ax.fill(fairway[0], fairway[1], alpha=0.3, color='forestgreen')
ax.plot(green[0], green[1], 'g-', linewidth=2, label='Green')
ax.fill(green[0], green[1], alpha=0.3, color='limegreen')

ax.grid(True)
ax.legend(loc='best')
ax.axis('equal')
plt.show()