from itertools import combinations
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
import numpy


def print_figure(fig, *args, **kwargs):
    canvas = FigureCanvasAgg(fig)
    canvas.print_figure(*args, **kwargs)


def merge_nonsignificant_cliques(not_sig):
    # keep only longest
    def no_longer(i, j, not_sig):
        for i1, j1 in not_sig:
            if (i1 <= i and j1 > j) or (i1 < i and j1 >= j):
                return False
        return True

    longest = [(i, j) for i, j in not_sig if no_longer(i, j, not_sig)]

    return longest


def graph_ranks(scores, names, get_linked_methods,
                lowv=None, highv=None, width=6, textspace=1.5,
                reverse=False, tickstep=3, **kwargs):
    """
    Draws a critical difference graph, which is used to display  the differences in methods'
    performance. This is inspired by the plots used in:

    See Janez Demsar, Statistical Comparisons of Classifiers over
    Multiple Data Sets, 7(Jan):1--30, 2006. 

    Methods are drawn on an axis and connected with a line if their performance is not significantly
    different.

    Needs matplotlib to work.

    Code here is a modified version of that found in Orange:
    https://bitbucket.org/biolab/orange/src/a4303110189426d004156ce053ddb35a410e428a/Orange/evaluation/scoring.py

    :param scores: List of average methods' scores.
    :param names: List of methods' names.
    :param get_linked_methods: callable that returns a list of tuples of indices of all pairs of methods
    that are not significantly different and should be connected in the diagram. Each tuple must be sorted,
    and no duplicate tuples should be contained in the list.

        Examples:
         - [(0, 1), (3, 4), (4, 5)] is correct
         - [(0, 1), (3, 4), (4, 5), (3,4)] contains a duplicate
         - [(4, 3)] contains a non-sorted tuple

    If there is a cluster of non-significant differences (e.g. 1=2, 2=3, 1=3), `graph_ranks` will draw
    just a single link connecting all of them
    :param lowv: The lowest shown score, if None, use min(scores).
    :param highv: The highest shown score, if None, use max(scores).
    :param width: Width of the drawn figure in inches, default 6 in.
    :param textspace: Space on figure sides left for the description
                      of methods, default 1 in.
    :param tickstep: space between ticks on the axis, in whatever units `scores` is in
    :param reverse:  If True, the lowest rank is on the right. Default is False.

    """
    width = float(width)
    textspace = float(textspace)

    tempsort = sorted([(a, i) for i, a in enumerate(scores)], reverse=reverse)
    ssums = [foo[0] for foo in tempsort]
    sortidx = [foo[1] for foo in tempsort]
    nnames = [names[x] for x in sortidx]

    if lowv is None:
        lowv = min(scores)
    if highv is None:
        highv = max(scores)

    cline = 0.4

    k = len(scores)

    scalewidth = width - 2 * textspace

    def rankpos(rank):
        if not reverse:
            a = rank - lowv
        else:
            a = highv - rank
        return textspace + scalewidth / (highv - lowv) * a

    # get pairs of non significant methods
    linked = get_linked_methods(ssums)
    lines = merge_nonsignificant_cliques(linked)
    linesblank = 0.2 + 0.2 + (len(lines) - 1) * 0.1

    # add scale
    distanceh = 0.25
    cline += distanceh

    # calculate height needed height of an image
    minnotsignificant = max(2 * 0.2, linesblank)
    height = cline + ((k + 1) / 2) * 0.2 + minnotsignificant

    fig = Figure(figsize=(width, height))
    ax = fig.add_axes([0, 0, 1, 1])  # reverse y axis
    ax.set_axis_off()

    hf = 1. / height  # height factor
    wf = 1. / width

    def hfl(l):
        return [a * hf for a in l]

    def wfl(l):
        return [a * wf for a in l]


    # Upper left corner is (0,0).

    ax.plot([0, 1], [0, 1], c="w")
    ax.set_xlim(0, 1)
    ax.set_ylim(1, 0)

    def line(l, color='k', **kwargs):
        """
        Input is a list of pairs of points.
        """
        a = [x[0] for x in l]
        b = [x[1] for x in l]
        ax.plot(wfl(a), hfl(b), color=color, **kwargs)

    def text(x, y, s, *args, **kwargs):
        ax.text(wf * x, hf * y, s, *args, **kwargs)

    # main axis
    line([(textspace, cline), (width - textspace, cline)], linewidth=0.7)

    bigtick = 0.1
    smalltick = 0.05

    tick = None
    # ticks on the x-axis
    for a in list(numpy.arange(lowv, highv, tickstep)) + [highv]:
        tick = smalltick
        if a == int(a): tick = bigtick
        line([(rankpos(a), cline - tick / 2), (rankpos(a), cline)], linewidth=0.7)

    # tick labels on the x axis
    for a in list(numpy.arange(lowv, highv + 1, tickstep)) + [highv]:
        a = int(a)
        # todo add bbox=dict(facecolor='red', alpha=0.5) to see how text is aligned to ticks
        text(rankpos(a), cline - tick / 2, str(a), ha="left", va="bottom")

    k = len(ssums)

    # 'arrows' pointing to the first half of the method names
    for i in range((k + 1) // 2):
        chei = cline + minnotsignificant + i * 0.2
        line([(rankpos(ssums[i]), cline), (rankpos(ssums[i]), chei), (textspace - 0.1, chei)], linewidth=0.7)
        text(textspace - 0.2, chei, nnames[i], ha="right", va="center", **kwargs)
    # arrows pointing to the second half of method names
    for i in range((k + 1) // 2, k):
        chei = cline + minnotsignificant + (k - i - 1) * 0.2
        line([(rankpos(ssums[i]), cline), (rankpos(ssums[i]), chei), (textspace + scalewidth + 0.1, chei)],
             linewidth=0.7)
        text(textspace + scalewidth + 0.2, chei, nnames[i], ha="left", va="center", **kwargs)

    # if cd and cdmethod is None:
    #     # if we want to annotate a single method with the critical difference
    #
    #     # upper scale
    #     if not reverse:
    #         begin, end = rankpos(lowv), rankpos(lowv + cd)
    #     else:
    #         begin, end = rankpos(highv), rankpos(highv - cd)
    #
    #     # draw a line as large as the CD above the main plot to give a sense of scale
    #     # line([(begin, distanceh), (end, distanceh)], linewidth=0.7)
    #     # line([(begin, distanceh + bigtick / 2), (begin, distanceh - bigtick / 2)], linewidth=0.7)
    #     # line([(end, distanceh + bigtick / 2), (end, distanceh - bigtick / 2)], linewidth=0.7)
    #     # text((begin + end) / 2, distanceh - 0.05, "CD", ha="center", va="bottom")
    #
    def draw_lines(lines, side=0.01, height=0.1):
        # side = how much horizontal overhang should there be
        # height = how much vertical space between lines connecting non-significant methods
        start = cline + .2 # vertical offset from the axis
        for l, r in lines:
            line([(rankpos(ssums[l]) - side, start), (rankpos(ssums[r]) + side, start)], linewidth=2.5)
            start += height

    # draw the lines that connect methods that are not significantly different
    draw_lines(lines)
    #
    # elif cd:
    #     # draw a single fat line on the x axis centered around `cdmethod`
    #     begin = rankpos(scores[cdmethod] - cd)
    #     end = rankpos(scores[cdmethod] + cd)
    #     line([(begin, cline), (end, cline)], linewidth=2.5)
    #     line([(begin, cline + bigtick / 2), (begin, cline - bigtick / 2)], linewidth=2.5)
    #     line([(end, cline + bigtick / 2), (end, cline - bigtick / 2)], linewidth=2.5)

    return fig



def get_close_pairs(scores, threshold=1):
    # get all pairs
    n_methods = len(scores)
    allpairs = list(combinations(range(n_methods), 2))

    not_sig = [(i, j) for i, j in allpairs if abs(scores[i] - scores[j]) <= threshold]
    return not_sig

def my_get_lines(*args):
    return [(3, 4), (4, 5), (3, 5)]

def all_but_the_extremes(scores):
    k = len(scores)
    allpairs = list(combinations(range(k), 2))
    allpairs.pop(k-2)
    return allpairs

if __name__ == "__main__":
    avranks = [31.43, 20.00, 28.93, 19.64, 25, 33.4]
    names = ['first', 'second', 'third', 'fourth', 'fifth', 'sixth']
    fig = graph_ranks(avranks, names, my_get_lines, fontsize=10)
    print_figure(fig, "test.png", format='png')