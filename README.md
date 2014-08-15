Critical difference
=======

Draws a critical difference graph, which is used to display  the differences in methods'
performance. This is inspired by the plots used in:

`Janez Demsar, Statistical Comparisons of Classifiers over Multiple Data Sets, 7(Jan):1--30, 2006. `

The performance of several methods is marked on an axis. Methods are connected with
 a line if their performance is not significantly different. Note this program does
 provide any statistical tests. Instead, the user writes a function that returns a
 list of all pairs of methods that are not significantly different.

Demo
=======

First we define a bunch of method names and their respective scores.
```python
names = ['first', 'second', 'third', 'fourth', 'fifth', 'sixth']
scores = [31.43, 20.00, 28.93, 19.64, 25, 33.4]

```
We then write a function that takes the scores and returns the indices of methods
that are not different
```
def my_get_lines(method_scores):
    return [(3, 4), (4, 5), (3, 5)]
```
This program performs little to no validation of the inputs, so it's your
responsibility to ensure that each tuple in the returned list is be sorted and
that no duplicate are should be contained in the list. Examples:
 - `[(0, 1), (3, 4), (4, 5)]` is correct
 - `[(0, 1), (3, 4), (4, 5), (3,4)]` contains a duplicate
 - `[(4, 3)]` contains a non-sorted tuple

We can then plot the desired diagram and save it to disk:

```python
from critical_difference.plot import graph_ranks, print_figure

fig = graph_ranks(scores, names, my_get_lines)
print_figure(fig, "test.png", format='png')

```

![Screenshot 1](img/1.png "Example 1")


Here is another real-word example:

License
===
This program is a modified version of that found in [Orange](https://bitbucket.org/biolab/orange/src/a4303110189426d004156ce053ddb35a410e428a/Orange/evaluation/scoring.py)
and is distributed under the terms of the GNU General Public License Version 3.
