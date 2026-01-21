import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import BSpline

"""

BSpline is an interpolation method to create a smooth curve using a peacewise polynomial function.

The first parameter o is a positive integer which dictates the order of the individual polynomials within the peacewise function.
The second parameter ka is an array of knots which indicate where the peacewise functions connect. 
The third parameter ca is an array of control points which act as a goal for which the spline attempts to reach.

Each segment of the BSpline spans ka[n:n+o], controlled by ca[n] 

For a BSpline of order n;
    - len(ka) >= 2 * (o + 1)
    - len(ca) == len(ka) - o + 1

The first at last knots in a knot array are often repeated n + 1 times to ensure the start and end of the spline falls at 
ca[0] and ca[-1] respectively.

"""

o = 2 
ka = [0, 0, 0, 3, 3, 3]
ca = [0, 5, -1]
spl = BSpline(ka, ca, o)


fig, ax = plt.subplots()
xx = np.linspace(0, 3, 50)
ax.plot(xx, spl(xx), 'b-', lw=4, alpha=0.7, label='BSpline')

ax.grid(True)
ax.legend(loc='best')
plt.show()