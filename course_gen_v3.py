import numpy as np
from scipy.interpolate import BSpline, PchipInterpolator, splprep, splev
import matplotlib.pyplot as plt
from matplotlib.path import Path

np.random.seed(67)

class CourseGenerator():
    def __init__(self):
        pass


    def _generate_green(self):
        avg_radius = 15
        variance = 2
        xx = []
        yy = []

        thetas = np.linspace(0, 2 * np.pi, 12)
        for theta in thetas:
            hypotnuse = avg_radius + (variance * np.random.randn())
            xx.append(hypotnuse * np.cos(theta))
            yy.append(hypotnuse * np.sin(theta))

        tck, _ = splprep([xx, yy], s=0, per=True)
        green = splev(np.linspace(0, 1, 30), tck) # 30 IS A PLACEHOLDER VALUE
        green_path = Path(np.column_stack((green[0], green[1])))

        return green


    def _generate_green_traps(self, green):
        avg_width = 5
        trap_outset = 1

        sector = np.random.randint(0, 2) * 10 # 10 is one third of the placeholder value 30 in _generate_green()
        sector_xx = green[0][sector:sector+10]
        sector_yy = green[1][sector:sector+10]

        prev_xx = sector_xx[:-1]
        prev_yy = sector_yy[:-1]
        normals_run = sector_yy[1:] - prev_yy
        normals_rise = prev_xx - sector_xx[1:]
        normals_direction = np.sqrt(normals_run**2 + normals_rise**2)

        trap_top = [[], []]
        trap_bottom = [[], []]
        for point_index in range(1, len(sector_xx)):
            width = avg_width + 2*np.random.randn()
            x_scaler = (normals_run[point_index-1]/normals_direction[point_index-1])
            y_scaler = (normals_rise[point_index-1]/normals_direction[point_index-1])
            trap_bottom[0].append(sector_xx[point_index] + trap_outset*x_scaler)
            trap_bottom[1].append(sector_yy[point_index] + trap_outset*y_scaler)
            trap_top[0].append(trap_bottom[0][-1] + width*x_scaler)
            trap_top[1].append(trap_bottom[1][-1] + width*y_scaler)
        
        unclosed_trap = np.array([
            np.concatenate((trap_bottom[0], trap_top[0][::-1])),
            np.concatenate((trap_bottom[1], trap_top[1][::-1]))
            ])
        
        tck, _ = splprep(unclosed_trap, s=0, per=True)
        trap = splev(np.linspace(0, 1, 50), tck) # 50 is another placeholder value
        green_path = Path(np.column_stack((trap[0], trap[1])))

        return trap


    def generate(self, length=350):
        green = self._generate_green() 
        trap = self._generate_green_traps(green)
        return green, trap


def main():
    xx = np.linspace(0, 350, 50) 
    course = CourseGenerator()
    green, trap = course.generate()

    fig, ax = plt.subplots()
    # ax.plot(xx, center_line(xx), 'r-', label='')
    ax.fill(green[0], green[1], alpha=.5, color='seagreen')
    ax.fill(trap[0], trap[1], alpha=.5, color='red')

    ax.grid(True)
    ax.legend(loc='best')
    ax.axis('equal')
    plt.show()


if __name__ == '__main__':
    main()