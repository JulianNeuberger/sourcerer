import argparse
import csv
import operator
from typing import Sequence, List, Callable, Any

from matplotlib import pyplot as plt

from source import Source


def plot_citations_per_year(sources: List[Source], predicate: Callable[[Source], bool]):
    sources = [source for source in sources if predicate(source)]
    sources.sort(key=lambda source: source.cites_per_year)

    bins = {
        (-1e7, 0): '0',
        (0, 1): '0-1',
        (1, 10): '1-10',
        (10, 25): '10-25',
        (25, 100): '25-100',
        (100, 1e7): '>100'
    }

    values = {}

    for s in sources:
        try:
            active_bin = next((x for x in bins.keys() if x[0] < s.cites_per_year <= x[1]))
        except StopIteration:
            print(f'No label for value {s.cites_per_year}')
            raise Exception()
        label = bins[active_bin]
        if label not in values:
            values[label] = 0
        values[label] += 1

    plt.figure(0)
    plt.title('Number of publications by avg. citations per year')
    plt.bar(values.keys(), values.values())
    plt.xticks(rotation=90)
    plt.show()


def plot_year(sources: List[Source], predicate: Callable[[Source], bool]):
    sources = [source for source in sources if predicate(source)]
    sources.sort(key=lambda source: str(source.year))

    by_years = {}

    for s in sources:
        year = str(s.year)
        if year not in by_years:
            by_years[year] = 0
        by_years[year] += 1

    plt.figure(1)
    plt.title('Number of publications by year')
    plt.bar(by_years.keys(), by_years.values())
    plt.xticks(rotation=90)
    plt.show()


def build_predicate(from_str: str):
    def base_predicate(source: Source):
        if not hasattr(source, attr_name):
            return False
        actual_value = getattr(source, attr_name)
        if actual_value is None:
            return False
        return op(actual_value, float(attr_value))

    if from_str == '' or from_str is None:
        return lambda source: True

    if '>=' in from_str:
        attr_name, attr_value = from_str.split('>=')
        op = operator.ge
    elif '<=' in from_str:
        attr_name, attr_value = from_str.split('<=')
        op = operator.le
    elif '>' in from_str:
        attr_name, attr_value = from_str.split('>')
        op = operator.gt
    elif '<' in from_str:
        attr_name, attr_value = from_str.split('<')
        op = operator.lt
    else:
        raise ValueError(f'Unknown operator in expression "{from_str}"')

    return base_predicate


def analyze(raw_args: Sequence[str]):
    perspectives = {
        'year': plot_year,
        'citations_per_year': plot_citations_per_year
    }

    parser = argparse.ArgumentParser()

    parser.add_argument('sources', help='path to file with sources to analyze')
    parser.add_argument('--perspective',
                        help='', required=True,
                        choices=perspectives.keys())
    parser.add_argument('--verbosity', '-v',
                        help='level of verbosity', default='progress',
                        choices=['silent', 'progress', 'all'])
    parser.add_argument('--filter', '-f',
                        help='use an expression to filter sources, '
                             'e.g. "year>2000" to plot only sources published after 2000. '
                             'Allowed attributes: year, num_cites, cites_per_year, cites_per_author',
                        required=False)

    args = parser.parse_args(raw_args)

    with open(args.sources, 'r', encoding='utf8') as f:
        reader = csv.reader(f)
        # skip header
        next(reader, None)
        sources = [Source.from_processed_csv_row(r, args.verbosity) for r in reader]

    perspectives[args.perspective](sources, build_predicate(args.filter))
