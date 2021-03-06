from math import ceil

import matplotlib.pylab as plt
from matplotlib.lines import Line2D


def _contained_in_larger_interval(i, j, not_sig):
    for i1, j1 in not_sig:
        if (i1 <= i and j1 > j) or (i1 < i and j1 >= j):
            return True
    return False


def merge_nonsignificant_cliques(not_sig):
    # keep only longest
    longest = [(i, j) for i, j in not_sig if
               not _contained_in_larger_interval(i, j, not_sig)]
    return longest


def do_plot(x, insignificant_indices, names=None,
            arrow_vgap=.2, link_voffset=.15, link_vgap=.1,
            xlabel=None):
    """
    Draws a critical difference graph, which is used to display  the
    differences in methods' performance. This is inspired by the plots used in:

    See Janez Demsar, Statistical Comparisons of Classifiers over
    Multiple Data Sets, 7(Jan):1--30, 2006.

    Methods are drawn on an axis and connected with a line if their
    performance is not significantly different.

    :param x: List of average methods' scores.
    :type x: list-like
    :param insignificant_indices: list of  tuples that specify the indices of
    all pairs of methods that are not significantly different and should be
    connected in the diagram. Each tuple must be sorted, and no duplicate
    tuples should be contained in the list.

        Examples:
         - [(0, 1), (3, 4), (4, 5)] is correct
         - [(0, 1), (3, 4), (4, 5), (3,4)] contains a duplicate
         - [(4, 3)] contains a non-sorted tuple

    If there is a cluster of non-significant differences (e.g. 1=2, 2=3,
    1=3), `graph_ranks` will draw just a single link connecting all of them.

    Note: the indices returned by this callable should refer to positions in
    `scores` after it is sorted in increasing order. It is to avoid confusion
    this function raises if `scores` is not sorted.

    :param names: List of methods' names.
    :param arrow_vgap: vertical space between the arrows that point to method
     names.  Scale is 0 to 1, fraction of axis
    :param link_vgap: vertical space between the lines that connect methods
    that are not significantly different. Scale is 0 to 1, fraction of axis size
    :param link_voffset: offset from the axis of the links that connect
    non-significant methods
    """
    if names is None:
        names = list(range(len(x)))

    for pair in insignificant_indices:
        assert all(0 <= idx < len(x) for idx in pair), 'Check indices'

    # remove both axes and the frame: http://bit.ly/2tBIlWv
    fig, ax = plt.subplots(1, 1, figsize=(6, 2), subplot_kw=dict(frameon=False))
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().set_visible(False)

    size = len(x)
    y = [0] * size
    ax.plot(x, y, 'ko')

    plt.xlim(0.9 * x[0], 1.1 * x[-1])
    plt.ylim(0, 1)

    # draw the x axis again
    # this must be done after plotting
    xmin, xmax = ax.get_xaxis().get_view_interval()
    ymin, ymax = ax.get_yaxis().get_view_interval()
    ax.add_artist(Line2D((xmin, xmax), (ymin, ymin),
                         color='black', linewidth=2))

    # add an optional label to the x axis
    if xlabel:
        ax.annotate(xlabel, xy=(xmax, 0), xytext=(0.95, 0.1),
                    textcoords='axes fraction', ha='center', va='center',
                    fontsize=9)  # text slightly smaller

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
                    arrowprops={'arrowstyle': '-',
                                'connectionstyle': 'angle,angleA=0,angleB=90'})

    # draw horizontal lines linking non-significant methods
    linked_methods = merge_nonsignificant_cliques(insignificant_indices)
    # where do the existing lines begin and end, (X, Y) coords
    used_endpoints = set()
    y = link_voffset
    dy = link_vgap

    def overlaps_any(foo, existing):
        """
        Checks if the proposed horizontal line (given with its x-y coordinates)
        overlaps any of the existing horizontal lines
        """
        return _contained_in_larger_interval(foo[0], foo[1], existing)

    for i, (x1, x2) in enumerate(sorted(linked_methods)):
        # determine how far up/down the line should be drawn
        # 1. can we lower it any further- not if it would be too low and if it
        # would overlap another line
        if y > link_voffset and overlaps_any((x1, y - dy), used_endpoints):
            y -= dy
        # 2. can we draw it at the current value of y- not if its left
        # end would overlap with the right end of an existing line
        # need to lift up a bit
        elif overlaps_any((x1, y), used_endpoints):
            y += dy
        else:
            pass

        plt.hlines(y, x[x1], x[x2], linewidth=3)  # y, x0, x1

        used_endpoints.add((x1, y))
        used_endpoints.add((x2, y))


if __name__ == "__main__":
    insignificant_indices = [
        (0, 1), (1, 2), (2, 3),  # these three should be drawn on 2 level
        (3, 4), (3, 5), (4, 5),  # this is a clique, just one line
    ]

    scores = sorted([31.43, 20.00, 28.93, 19.64, 25, 33.4])
    names = ['first', 'second', 'third', 'fourth', 'fifth', 'sixth']
    do_plot(scores, insignificant_indices, names, xlabel='accuracy, %')
