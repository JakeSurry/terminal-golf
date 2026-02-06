import numpy as np
from scipy.interpolate import BSpline, PchipInterpolator, splprep, splev
import matplotlib.pyplot as plt
from matplotlib.path import Path
from dataclasses import dataclass

np.random.seed(1)

@dataclass
class Line:
    xx: tuple
    yy: tuple
    position: tuple = (0, 0)


@dataclass
class Feature:
    ftype: str
    xx: tuple
    yy: tuple
    path: Path
    height: tuple = ()
    position: tuple = (0, 0)
    parent: Line | Feature = None
    color: str = 'black'
    

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

        center_line_points = PchipInterpolator(x_points, y_points)
        
        return Line(xx=center_line_points[0], yy=center_line_points[1])


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
        green_path = Path(np.column_stack((green_shape[0], green_shape[1])))

        return Feature(ftype="green", shape=green_shape, path=green_path, parent=self.center_line, color='seagreen')


    def _generate_green_traps(self):
        resolution = 100
        avg_width = 8
        variance = 1
        trap_outset = 1
        green = self.features[0]

        sector_arc = len(green.shape[0]) // 3
        sector_start = np.random.randint(0, 2) * sector_arc
        sector_end = sector_start + sector_arc
        sector_xx = green.shape[0][sector_start:sector_end]
        sector_yy = green.shape[1][sector_start:sector_end]

        prev_xx = sector_xx[:-1]
        prev_yy = sector_yy[:-1]
        normals_run = sector_yy[1:] - prev_yy
        normals_rise = prev_xx - sector_xx[1:]
        normals_direction = np.sqrt(normals_run**2 + normals_rise**2)

        trap_top_x = []
        trap_top_y = []
        trap_bot_x = []
        trap_bot_y = []
        for point_index in range(1, sector_arc, sector_arc // 8):
            width = avg_width + variance*np.random.randn()
            x_scaler = (normals_run[point_index-1]/normals_direction[point_index-1])
            y_scaler = (normals_rise[point_index-1]/normals_direction[point_index-1])
            trap_bot_x.append(sector_xx[point_index] + trap_outset*x_scaler)
            trap_bot_y.append(sector_yy[point_index] + trap_outset*y_scaler)
            trap_top_x.append(trap_bot_x[-1] + width*x_scaler)
            trap_top_y.append(trap_bot_y[-1] + width*y_scaler)
        
        unclosed_trap = np.array([
            np.concatenate((trap_bot_x, trap_top_x[::-1])),
            np.concatenate((trap_bot_y, trap_top_y[::-1]))
            ])
        
        tck, _ = splprep(unclosed_trap, s=0, per=True)
        trap_shape = tuple(splev(np.linspace(0, 1, resolution), tck))
        trap_path = Path(np.column_stack((trap_shape[0], trap_shape[1])))

        return Feature(ftype="trap", shape=trap_shape, path=trap_path, parent=green, color='wheat')


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
        ax.fill(feature.shape[0], feature.shape[1], alpha=1, color=feature.color, label=feature.ftype)

    ax.grid(True)
    ax.legend(loc='best')
    ax.axis('equal')
    plt.show()


if __name__ == '__main__':
    main()