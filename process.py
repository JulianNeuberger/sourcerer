import argparse
import csv
import os
from typing import List, Sequence

from source import Source


def parse_file(directory_path: str, file_name: str, delimiter: str, verbosity: str) -> List[Source]:
    with open(os.path.join(directory_path, file_name), 'r', encoding='utf8') as f:
        reader = csv.reader(f, delimiter=delimiter)
        # ignore the header row
        next(reader, None)
        return [Source.from_raw_csv_row(r, verbosity) for r in reader]


def parse_directory(directory_path: str, delimiter: str, verbosity: str) -> List[List[Source]]:
    if not os.path.exists(directory_path):
        raise Exception(f'Directory {directory_path} does not exist.')

    files: List[str] = os.listdir(directory_path)
    files = [f for f in files if f.endswith('.csv')]

    if verbosity != 'silent':
        print(f'Parsing sources from {len(files)} .csv search result files...')
    sources = [parse_file(directory_path, f, delimiter, verbosity) for f in files]
    if verbosity != 'silent':
        print(f'Retrieved {sum([len(s) for s in sources])} sources from {len(files)} files, done!')

    return sources


def export_to_file(file_path: str, sources: List[Source], delimiter: str, verbosity: str) -> None:
    export_dir = os.path.dirname(file_path)
    os.makedirs(export_dir, exist_ok=True)

    if verbosity != 'silent':
        print(f'Writing {len(sources)} sources to csv...')
    with open(file_path, 'w', newline='', encoding='utf8') as f:
        writer = csv.writer(f, delimiter=delimiter)
        writer.writerow(['Cites', 'Title', 'Authors', 'Year', 'Source', 'Publisher', 'Url', 'Citations url', 'GS',
                         'Queried Date', 'ECC', 'Cites / Year', 'Cites / Author'])
        writer.writerows([s.to_csv_row() for s in sources])
    if verbosity != 'silent':
        print('Done!')


def process_sources(sources: List[List[Source]], method: str = 'union', equality_by_columns: List[str] = None) -> List[Source]:
    def _is_equal(s1: Source, s2: Source, _by_cols: List[str]):
        for col in _by_cols:
            a1 = getattr(s1, col)
            a2 = getattr(s2, col)

            if hasattr(a1, 'lower'):
                a1 = a1.lower()

            if hasattr(a2, 'lower'):
                a2 = a2.lower()

            if hasattr(a1, 'strip'):
                a1 = a1.strip()

            if hasattr(a2, 'strip'):
                a2 = a2.strip()

            if a1 != a2:
                return False
        return True

    def _is_in(_s: Source, _container: List[Source], _by_cols: List[str]):
        for _s2 in _container:
            if _is_equal(_s, _s2, _by_cols):
                return True
        return False

    def _count_occurrences(_s, _containers: List[List[Source]], _by_cols: List[str]) -> int:
        ret = 0
        for c in _containers:
            if _is_in(_s, c, _by_cols):
                ret += 1
        return ret

    def _diff(_sources: List[List[Source]], _cols: List[str]):
        all_sources = _union(_sources, _cols)
        ret = []
        for s in all_sources:
            if _count_occurrences(s, _sources, _cols) == 1:
                ret.append(s)
        return ret

    def _intersect(_sources: List[List[Source]], _cols: List[str]):
        all_sources = _union(_sources, _cols)
        num_containers = len(_sources)
        ret = []
        for s in all_sources:
            if _count_occurrences(s, _sources, _cols) == num_containers:
                ret.append(s)
        return ret

    def _union(_sources: List[List[Source]], _cols: List[str]):
        ret = []
        for cur in _sources:
            for s in cur:
                if not _is_in(s, ret, _cols):
                    ret.append(s)
        return ret

    if equality_by_columns is None:
        equality_by_columns = ['title']

    if method == 'union':
        return _union(sources, equality_by_columns)

    if method == 'intersect':
        return _intersect(sources, equality_by_columns)

    if method == 'difference':
        return _diff(sources, equality_by_columns)

    raise NotImplementedError(f'Unknown processing method "{method}".')


def process(raw_args: Sequence[str]):
    parser = argparse.ArgumentParser()

    parser.add_argument('input_directory',
                        help='directory where search results as .csv files can be found')
    parser.add_argument('output_file',
                        help='where to write the resulting .csv file')
    parser.add_argument('--method', '-m',
                        choices=['intersect', 'union', 'difference'],
                        help='how to process sources found in the given files')
    default_equality_cols = ['title']
    parser.add_argument('--by-column', '-c',
                        help=f'columns to use for equality checks, '
                             f'defaults to columns {",".join(default_equality_cols)}')
    parser.add_argument('--delimiter', '-d',
                        help='csv delimiter, defaults to comma: ","',
                        default=',')
    parser.add_argument('--remove-duplicates', '-r',
                        action='store_true',
                        help='whether duplicates should be removed or not, defaults to removing them')
    parser.add_argument('--verbosity', '-v',
                        help='level of verbosity', default='progress',
                        choices=['silent', 'progress', 'all'])

    args = parser.parse_args(raw_args)
    if args.by_column is None:
        args.by_column = default_equality_cols

    sources = parse_directory(args.input_directory, delimiter=args.delimiter, verbosity=args.verbosity)

    processed = process_sources(sources, method=args.method, equality_by_columns=args.by_column)

    processed.sort(key=lambda s: s.num_cites, reverse=True)

    export_to_file(args.output_file, processed, delimiter=args.delimiter, verbosity=args.verbosity)