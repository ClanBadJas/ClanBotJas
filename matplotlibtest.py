import io

import matplotlib.pyplot as plt
import numpy as np

if __name__ == "__main__":
    height = [3, 12, 5, 18, 45]
    bars = ('A', 'B', 'C', 'D', 'E')
    y_pos = np.arange(len(bars))


    plt.rcdefaults()
    fig, ax = plt.subplots()
    ax.barh(y_pos, height, align='center')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(bars)
    ax.invert_yaxis()  # labels read top-to-bottom
    ax.set_xlabel('Performance')
    ax.set_title('How fast do you want to go today?')

    plt.savefig("nope.png")
