import numpy as np
np.random.seed(4)

from scipy.interpolate import BSpline, PchipInterpolator, splprep, splev
import matplotlib.pyplot as plt
from matplotlib.path import Path

class Course():
    def __init__(self, par=4, dogleg=False, intensity=1):
        self.par = par
        self.dogleg = dogleg
        self.intensity = intensity 

        match self.par:
            case 3:
                self.length = 150
            case 4:
                self.length = 350
            case 5:
                self.length = 550
        self.width = 50
        
        self.center_line = None
        self.fairway = None
        self.fairway_path = None

    def _generate_center_line(self):
        inflection_points = 7
        x_points = np.linspace(0, self.length, inflection_points) # x positions where bends occur
        y_points = np.zeros(inflection_points)

        if self.dogleg == True:
            bend_location = 4
            bend_direction = 1
            bend_intensity = self.intensity * self.width * bend_direction
            for i in range(1, inflection_points-1):
                y_points[i] = bend_intensity * np.exp(-((i-bend_location)/2)**2)

        # Smooth with cubic spline
        center_line_function = PchipInterpolator(x_points, y_points)
        
        return center_line_function

    def _generate_width(self):
        degree = 6
        num_control_points = 10
        
        control_array = np.zeros(num_control_points + degree+1)
        knot_array = np.linspace(0, self.length, num_control_points+2)
        knot_array = np.concatenate((np.zeros(degree), knot_array, np.full(shape=degree, fill_value=knot_array[-1]))) #Duplicate boundry knots

        for i in range(len(control_array)):
            offset = abs(self.width//2 + (self.width//4)*np.random.uniform(low=0.0, high=2.0))
            control_array[i] = offset

        control_array[0] = 0
        control_array[-1] = 0

        width_function = BSpline(knot_array, control_array, degree)

        return width_function
    
    def _generate_fairway_shape(self, center_line, top_width, bottom_width):
        curve_sample_resolution = 50

        xx = np.linspace(0, self.length, curve_sample_resolution)

        top_bound = center_line(xx) + top_width(xx)
        bottom_bound = center_line(xx) - bottom_width(xx)

        fairway_x = np.concatenate((xx, xx[-2:0:-1]))
        fairway_y = np.concatenate((top_bound, bottom_bound[-2:0:-1]))

        shape_generation_resolution = np.linspace(0, 1, 400)
        tck, u = splprep([fairway_x, fairway_y], s=0, per=True)
        fairway = splev(shape_generation_resolution, tck)
        fairway_path = Path(np.column_stack([fairway[0], fairway[1]]))

        return fairway, fairway_path
    
    def generate(self):
        center_line = self._generate_center_line()
        top_width = self._generate_width()
        bottom_width = self._generate_width()
        fairway, fairway_path = self._generate_fairway_shape(center_line, top_width, bottom_width)

        self.center_line = center_line
        self.fairway = fairway
        self.fairway_path = fairway_path

    def on_fairway(self):
        return bool

course = Course(dogleg=True)
course.generate()

center_line = course.center_line
fairway = course.fairway
xx = np.linspace(0, course.length, 50)

fig, ax = plt.subplots()

ax.plot(xx, center_line(xx), 'r-', label='Center Line')
ax.plot(fairway[0], fairway[1], 'b-', linewidth=2, label='Fairway')
ax.fill(fairway[0], fairway[1], alpha=0.3, color='green')

ax.grid(True)
ax.legend(loc='best')
ax.axis('equal')
plt.show()