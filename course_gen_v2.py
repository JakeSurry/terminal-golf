import numpy as np
from scipy.interpolate import BSpline, PchipInterpolator, splprep, splev
import matplotlib.pyplot as plt
from matplotlib.path import Path

np.random.seed(10)

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
        length = 0
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
            intensity_scaler = 50 # arbitrary
            bend_intensity = self.intensity * intensity_scaler * bend_direction
            for i in range(1, inflection_points-1):
                y_points[i] = bend_intensity * np.exp(-((i-bend_location)/2)**2)

        center_line_function = PchipInterpolator(x_points, y_points)
        
        return center_line_function
    

    def _generate_width(self, length):
        degree = 5
        num_control_points = 10
        control_array = np.zeros(num_control_points + degree+1)
        knot_array = np.linspace(0, length, num_control_points+2)
        knot_array = np.concatenate((np.zeros(degree),
                                     knot_array,
                                     np.full(shape=degree, fill_value=knot_array[-1]))) #Duplicate boundry knots


        min_width = 10
        for i in range(len(control_array)):
            loop_pos = (i/(len(control_array)-1)) * 2 # 0 -> 2, 0 at i = 0, 2 at i = n (last loop)
            center_scaler = -2 * loop_pos * (loop_pos - 2) # 0 -> 2, 0 at i = 0, 2 at i = n// 2, 0 at i = n (quadratic)
            center_scaler *= min_width // 2
            # offset = min_width//2 + (min_width)*np.random.uniform(low=0.0, high=2.0)*center_scaler
            # offset = abs(min_width//2 + (min_width // 2)*np.random.randn() + center_scaler)
            offset = min_width + abs((min_width)*np.random.randn())
            control_array[i] = offset

        control_array[0] = 0
        control_array[-1] = min_width
        control_array[-4] = min_width // 4

        width_function = BSpline(knot_array, control_array, degree)

        return width_function
    
    
    def _generate_fairway_shape(self, length, center_line, top_width, bottom_width):
        xx = np.linspace(0, length)

        top_bound = center_line(xx) + top_width(xx)
        bottom_bound = center_line(xx) - bottom_width(xx)
        fairway_x = np.concatenate((xx, xx[-1:0:-1]))
        fairway_y = np.concatenate((top_bound, bottom_bound[-1:0:-1]))

        fairway_generation_resolution = np.linspace(0, 1, length)
        fairway_tck, _ = splprep([fairway_x, fairway_y], s=0, per=True)
        fairway = splev(fairway_generation_resolution, fairway_tck)
        fairway_path = Path(np.column_stack([fairway[0], fairway[1]]))

        rough_top_bound = top_bound + 20
        rough_bottom_bound = bottom_bound - 20
        rough_x = np.concatenate((xx, xx[-1:0:-1]))
        rough_y = np.concatenate((rough_top_bound, rough_bottom_bound[-1:0:-1]))

        rough_generation_resolution = np.linspace(0, 1, length//4)
        rough_tck, _ = splprep([rough_x, rough_y], s=0, per=True)
        rough = splev(rough_generation_resolution, rough_tck)
        rough_path = Path(np.column_stack([rough[0], rough[1]]))

        return fairway, fairway_path, rough, rough_path
    
    
    def _generate_green_shape(self, length, fairway):
        green_length = 30
        green_inset = 2 # Distance of green from the edge of the fairway

        green_start_x = length - green_length
        mask = (fairway[0] >= green_start_x)

        xx = fairway[0][mask]
        yy = fairway[1][mask]
        xx_prev = xx[:-1]
        yy_prev = yy[:-1]
        normals_run = yy[1:] - yy_prev
        normals_rise = xx_prev - xx[1:]
        normals_magnitude = np.sqrt(normals_run**2 + normals_rise**2)
        unclosed_green = np.array([xx[1:] + green_inset*(normals_run/normals_magnitude), 
                                   yy[1:] + green_inset*(normals_rise/normals_magnitude)])

        tck, u = splprep([unclosed_green[0], unclosed_green[1]], s=0, per=True)
        green = splev(np.linspace(0, 1, green_length), tck)
        green_path = Path(np.column_stack((green[0], green[1])))
        
        return green, green_path


    def generate(self):
        length = self._generate_length()
        center_line = self._generate_center_line(length)
        top_width = self._generate_width(length)
        bottom_width = self._generate_width(length)
        fairway, fairway_path, rough, rough_path = self._generate_fairway_shape(length, center_line, top_width, bottom_width)
        green, green_path = self._generate_green_shape(length, fairway)

        self.center_line = center_line
        self.fairway = fairway
        self.fairway_path = fairway_path
        self.rough = rough
        self.rough_path = rough_path
        self.green = green
        self.green_path = green_path


    def on_fairway(self):
        return bool


def main():
    course = Course(dogleg=True)
    course.generate()

    center_line = course.center_line
    fairway = course.fairway
    rough = course.rough
    green = course.green
    xx = np.linspace(0, course.length, 50)

    fig, ax = plt.subplots()

    # ax.plot(xx, center_line(xx), 'r-', label='Center Line')
    # ax.plot(rough[0], rough[1], 'b-', linewidth=2, label='Rough')
    ax.fill(rough[0], rough[1], alpha=.5, color='seagreen')
    # ax.plot(fairway[0], fairway[1], 'b-', linewidth=2, label='Fairway')
    ax.fill(fairway[0], fairway[1], alpha=0.7, color='forestgreen')
    # ax.plot(green[0], green[1], 'g-', linewidth=2, label='Green')
    ax.fill(green[0], green[1], alpha=0.7, color='limegreen')

    ax.grid(True)
    ax.legend(loc='best')
    ax.axis('equal')
    plt.show()

if __name__ == "__main__":
    main()