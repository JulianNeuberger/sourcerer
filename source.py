import datetime
from dataclasses import dataclass
from typing import List, Callable, Optional, Any


@dataclass
class Mapping:
    csv_index: int
    attribute_name: str
    factory: Optional[Callable[[str], Any]] = None


@dataclass
class Source:
    num_cites: int
    authors: List[str]
    title: str
    year: Optional[int]
    source: Optional[str]
    publisher: Optional[str]
    url: Optional[str]
    citations_url: Optional[str]
    gs_rank: Optional[int]
    queried_date: datetime.datetime
    ecc: Optional[int]
    cites_per_year: Optional[int]
    cites_per_author: Optional[int]
    full_text_url: Optional[str]

    @staticmethod
    def from_raw_csv_row(csv_row: List[str], verbosity: str):
        mappings = [
            Mapping(0, 'num_cites', int),
            Mapping(1, 'authors', lambda s: s.replace('...', ', et al.').split(', ')),
            Mapping(2, 'title', str),
            Mapping(3, 'year', int),
            Mapping(4, 'source'),
            Mapping(5, 'publisher'),
            Mapping(6, 'url'),
            Mapping(7, 'citations_url'),
            Mapping(8, 'gs_rank', int),
            Mapping(9, 'queried_date', lambda s: datetime.datetime.strptime(s, '%Y-%m-%d %H:%M:%S')),
            Mapping(18, 'ecc', int),
            Mapping(19, 'cites_per_year', float),
            Mapping(20, 'cites_per_author', int),
            Mapping(24, 'full_text_url')
        ]

        return Source._from_mappings(csv_row, mappings, verbosity)

    @staticmethod
    def from_processed_csv_row(csv_row: List[str], verbosity: str):
        mappings = [
            Mapping(0, 'num_cites', int),
            Mapping(1, 'title', str),
            Mapping(2, 'authors', lambda s: s.replace('...', ', et al.').split(', ')),
            Mapping(3, 'year', int),
            Mapping(4, 'source'),
            Mapping(5, 'publisher'),
            Mapping(6, 'url'),
            Mapping(7, 'citations_url'),
            Mapping(8, 'gs_rank', int),
            Mapping(9, 'queried_date', lambda s: datetime.datetime.strptime(s, '%Y-%m-%d %H:%M:%S')),
            Mapping(10, 'ecc', int),
            Mapping(11, 'cites_per_year', float),
            Mapping(12, 'cites_per_author', int),
            Mapping(13, 'full_text_url')
        ]

        return Source._from_mappings(csv_row, mappings, verbosity)

    def to_csv_row(self):
        return [
            self.num_cites,
            self.title,
            ', '.join(self.authors),
            self.year,
            self.source,
            self.publisher,
            self.url,
            self.citations_url,
            self.gs_rank,
            self.queried_date.strftime('%Y-%m-%d %H:%M:%S'),
            self.ecc,
            self.cites_per_year,
            self.cites_per_author,
            self.full_text_url
        ]

    @staticmethod
    def _from_mappings(csv_row: List[str], mappings: List[Mapping], verbosity: str) -> 'Source':
        values = {}

        for m in mappings:
            value = csv_row[m.csv_index]
            if m.factory is not None:
                try:
                    value = m.factory(value)
                except ValueError:
                    if verbosity == 'all':
                        msg = f'Could not parse value from "{value}" for mapping of attribute ' \
                              f'"{m.attribute_name}", setting to None.'
                        print(msg)
                    value = None
            values[m.attribute_name] = value

        source = Source(**values)
        return source

    def __str__(self):
        return f'"{self.title}", {", ".join(self.authors)}, ({self.year})'

    def __repr__(self):
        return self.__str__()
