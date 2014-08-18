from itertools import combinations
from math import ceil
import matplotlib.pylab as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.lines import Line2D


def print_figure(fig, *args, **kwargs):
    canvas = FigureCanvasAgg(fig)
    canvas.print_figure(*args, **kwargs)


def merge_nonsignificant_cliques(not_sig):
    # keep only longest
    def contained_in_larger_interval(i, j, not_sig):
        for i1, j1 in not_sig:
            if (i1 <= i and j1 > j) or (i1 < i and j1 >= j):
                return True
        return False

    longest = [(i, j) for i, j in not_sig if not contained_in_larger_interval(i, j, not_sig)]

    return longest


def do_plot(x, get_linked_methods, names=None,
            arrow_vgap=.2,
            link_voffset=.15, link_vgap=.1
):
    """
    Draws a critical difference graph, which is used to display  the differences in methods'
    performance. This is inspired by the plots used in:

    See Janez Demsar, Statistical Comparisons of Classifiers over
    Multiple Data Sets, 7(Jan):1--30, 2006.

    Methods are drawn on an axis and connected with a line if their performance is not significantly
    different.

    Requires `matplotlib`

    :param x: List of average methods' scores.
    :type x: list-like

    :param names: List of methods' names.
    :param get_linked_methods: callable that returns a list of tuples of indices of all pairs of methods
    that are not significantly different and should be connected in the diagram. Each tuple must be sorted,
    and no duplicate tuples should be contained in the list.

        Examples:
         - [(0, 1), (3, 4), (4, 5)] is correct
         - [(0, 1), (3, 4), (4, 5), (3,4)] contains a duplicate
         - [(4, 3)] contains a non-sorted tuple

    If there is a cluster of non-significant differences (e.g. 1=2, 2=3, 1=3), `graph_ranks` will draw
    just a single link connecting all of them.

    Note: the indices returned by this callable should refer to positions in `scores` after it is sorted in increasing
    order. It is to avoid confusion this function raises if `scores` is not sorted.
    :param arrow_vgap: vertical space between the arrows that point to method names.  Scale is 0 to 1, fraction of axis
    :param link_vgap: vertical space between the lines that connect methods that are not significantly different.
     Scale is 0 to 1, fraction of axis size
    :param link_voffset: offset from the axis of the links that connect non-significant methods
    """
    if names is None:
        names = range(len(x))

    # remove both axes and the frame
    # http://www.shocksolution.com/2011/08/removing-an-axis-or-both-axes-from-a-matplotlib-plot/
    fig, ax = plt.subplots(1, 1, figsize=(6, 2), subplot_kw=dict(frameon=False))
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().set_visible(False)

    size = len(x)
    y = [0] * size
    ax.plot(x, y, 'ko')

    plt.xlim(0.8 * x[0] - 0.1, 1.2 * x[-1] + 0.1)
    plt.ylim(0, 1)

    # draw the x axis again
    # this must be done after plotting
    xmin, xmax = ax.get_xaxis().get_view_interval()
    ymin, ymax = ax.get_yaxis().get_view_interval()
    ax.add_artist(Line2D((xmin, xmax), (ymin, ymin), color='black', linewidth=2))

    half = int(ceil(len(x) / 2.))
    # make sure the topmost annotation in at 90% of figure height
    ycoords = list(reversed([0.9 - arrow_vgap * i for i in range(half)]))
    ycoords.extend(reversed(ycoords))
    for i in range(size):
        ax.annotate(str(names[i]),
                    xy=(x[i], y[i]),
                    xytext=(-.05 if i < half else .95,  # x coordinate
                            ycoords[i]),  # y coordinate
                    textcoords='axes fraction',
                    ha='center', va='center',
                    arrowprops=dict(arrowstyle='-',
                                    connectionstyle='angle,angleA=0,angleB=90'))

    linked_methods = merge_nonsignificant_cliques(get_linked_methods())
    used_endpoints = set()
    y = link_voffset
    for i, (x1, x2) in enumerate(sorted(linked_methods)):
        # not lift if it will overlap with an existing line
        if any(x1 <= foo for foo in used_endpoints):
            y += link_vgap
        plt.hlines(y, x[x1], x[x2], linewidth=3)  # y, x0, x1

        used_endpoints.add(x2)
    return fig


def get_close_pairs(scores, threshold=1):
    # get all pairs
    n_methods = len(scores)
    allpairs = list(combinations(range(n_methods), 2))

    not_sig = [(i, j) for i, j in allpairs if abs(scores[i] - scores[j]) <= threshold]
    return not_sig


def my_get_lines(*args):
    return [(3, 4), (4, 5), (3, 5), (2, 3)]


if __name__ == "__main__":
    scores = sorted([31.43, 20.00, 28.93, 19.64, 25, 33.4])
    names = ['first', 'second', 'third', 'fourth', 'fifth', 'sixth']
    fig = do_plot(scores, my_get_lines, names)
    print_figure(fig, "test.png", format='png')