import numpy as np
np.random.seed(4)

from scipy.interpolate import BSpline, PchipInterpolator
import matplotlib.pyplot as plt
from PIL import Image
import time

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

        print(knot_array)
        print(control_array)
        width_function = BSpline(knot_array, control_array, degree)

        return width_function
    
    def generate(self):
        self._generate_center_line()

    def on_fairway(self):

        return bool

course = Course(dogleg=True)

centerline = course._generate_center_line()
top_bound = course._generate_width()
bottom_bound = course._generate_width()

fig, ax = plt.subplots()
xx = np.linspace(0, course.length, 50)

ax.plot(xx, centerline(xx), 'b-', lw=4, alpha=0.7, label='centerline')
ax.plot(xx, centerline(xx)+top_bound(xx), 'g-', lw=4, alpha=0.7, label='Fairway Boundry')
ax.plot(xx, centerline(xx)-bottom_bound(xx), 'g-', lw=4, alpha=0.7)

ax.grid(True)
ax.legend(loc='best')
ax.axis('equal')
plt.show()