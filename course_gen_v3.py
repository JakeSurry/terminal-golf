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

        sector = np.rand.randint(0, 2) * 10
        sector_xx = green[0][sector:sector+10]
        sector_yy = green[1][sector:sector+10]

        '''
        TODO:   At each sector value, generate two points
                The first should be one yard from sector point along the normal axis
                The second should be avg_width yard from first point along the same axis
                Turn set of points into shape, hopefully a sand trap appears.
                Maybe shrink distance between points at the edges, but only if necessary. splev seems to just work most of the time.
                The following code is stolen from course_gen_v2.py green generation, fix it for specific use-case.

                Good luck, don't quit!

        prev_xx = sector_xx[:-1]
        prev_yy = sector_yy[:-1]
        normals_run = sector_yy[1:] - prev_yy
        normals_rise = prev_xx - sector_xx[1:]
        normals_magnitude = np.sqrt(normals_run**2 + normals_rise**2)
        unclosed_green = np.array([xx[1:] + green_inset*(normals_run/normals_magnitude), 
                                   yy[1:] + green_inset*(normals_rise/normals_magnitude)])

        tck, u = splprep([unclosed_green[0], unclosed_green[1]], s=0, per=True)
        green = splev(np.linspace(0, 1, green_length), tck)
        green_path = Path(np.column_stack((green[0], green[1])))
        '''


    def generate(self, length=350):
        green = self._generate_green() 
        return green


def main():
    xx = np.linspace(0, 350, 50) 
    course = CourseGenerator()
    green = course.generate()

    fig, ax = plt.subplots()
    # ax.plot(xx, center_line(xx), 'r-', label='')
    ax.fill(green[0], green[1], alpha=.5, color='seagreen')

    ax.grid(True)
    ax.legend(loc='best')
    ax.axis('equal')
    plt.show()


if __name__ == '__main__':
    main()