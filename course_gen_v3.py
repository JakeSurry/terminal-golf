import numpy as np
from scipy.interpolate import BSpline, PchipInterpolator, splprep, splev
import matplotlib.pyplot as plt
from matplotlib.path import Path
from dataclasses import dataclass
from functools import cached_property

np.random.seed(1)

@dataclass
class Feature:
    ftype: str
    xx: tuple
    yy: tuple
    zz: tuple = ()
    pos: tuple = (0, 0)
    color: str = 'black'

    @cached_property
    def abs_xx(self):
        return [x+self.pos[0] for x in self.xx]
    
    @cached_property
    def abs_yy(self):
        return [y+self.pos[1] for y in self.yy]


class CourseGenerator():
    def __init__(self, length=350):
        self.length = length

        self.center_line = None
        self.features = []

        self.generate()


    def _generate_center_line(self):
        inflection_points = 7
        x_points = np.linspace(0, self.length, inflection_points) # x positions where bends occur
        y_points = np.zeros(inflection_points)
        
        # if self.dogleg == True:
        #     bend_location = 3 # 3 is central
        #     bend_direction = 1 # 1 arcs up, -1 arcs down
        #     intensity_scaler = 50 # arbitrary
        #     bend_intensity = self.intensity * intensity_scaler * bend_direction
        #     for i in range(1, inflection_points-1):
        #         y_points[i] = bend_intensity * np.exp(-((i-bend_location)/2)**2)

        return PchipInterpolator(x_points, y_points)


    def _generate_green(self):
        resolution = 100
        avg_radius = 15
        variance = 1

        xx = []
        yy = []
        thetas = np.linspace(0, 2 * np.pi, 12)
        for theta in thetas:
            hypotnuse = avg_radius + (variance * np.random.randn())
            xx.append(hypotnuse * np.cos(theta))
            yy.append(hypotnuse * np.sin(theta))

        tck, _ = splprep([xx, yy], s=0, per=True)
        green_shape = tuple(splev(np.linspace(0, 1, resolution), tck))
        green_pos = (self.length, self.center_line(self.length))

        return Feature(ftype="green", xx=green_shape[0], yy=green_shape[1], pos=green_pos,  color='seagreen')


    def _generate_green_traps(self):
        resolution = 100
        avg_width = 8
        variance = 1
        trap_outset = 1
        n_sample_points = 8
        green = self.features[0]

        sector_arc = len(green.xx) // 3
        sector_start = np.random.choice([0, sector_arc, 2 * sector_arc])
        sector_slice = slice(sector_start, sector_start + sector_arc)
        sector_xx = green.xx[sector_slice]
        sector_yy = green.yy[sector_slice]

        dxx = np.diff(sector_xx)
        dyy = np.diff(sector_yy)
        normals_length = np.sqrt(dxx**2 + dyy**2)
        nxx = dyy / normals_length        
        nyy = -dxx / normals_length

        point_indicies = np.arange(1, sector_arc, sector_arc // n_sample_points)
        widths = avg_width + variance * np.random.randn(len(point_indicies))

        bot_xx = sector_xx[point_indicies] + trap_outset * nxx[point_indicies-1] 
        bot_yy = sector_yy[point_indicies] + trap_outset * nyy[point_indicies-1] 
        top_xx = bot_xx + widths * nxx[point_indicies-1] 
        top_yy = bot_yy + widths * nyy[point_indicies-1] 

        rough_trap_xx = np.concatenate((bot_xx, top_xx[::-1]))
        rough_trap_yy = np.concatenate((bot_yy, top_yy[::-1]))
        
        tck, _ = splprep([rough_trap_xx, rough_trap_yy], s=0, per=True)
        trap_xx, trap_yy = splev(np.linspace(0, 1, resolution), tck)
        trap_pos = (self.length, self.center_line(self.length))

        return Feature(ftype="trap", xx=trap_xx, yy=trap_yy, pos=trap_pos,  color='wheat')


    def generate(self):
        self.center_line = self._generate_center_line()
        self.features.append(self._generate_green())
        self.features.append(self._generate_green_traps())
        

def main():
    length = 350
    xx = np.linspace(0, length, 50) 
    course = CourseGenerator(length)

    fig, ax = plt.subplots()
    # ax.plot(xx, center_line(xx), 'r-', label='')
    for feature in course.features:
        ax.fill(feature.abs_xx, feature.abs_yy, alpha=1, color=feature.color, label=feature.ftype)

    ax.grid(True)
    ax.legend(loc='best')
    ax.axis('equal')
    plt.show()


if __name__ == '__main__':
    main()