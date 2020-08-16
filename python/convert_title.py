"""
Usage:
    convert_title.py <ES_ENDPOINT> -t <TITLE_FILE> -n <NAME_FILE>

Options:
    ES_ENDPOINT                            elasticsearch endpoint.
    -t <TITLE_FILE>, --title=<TITLE_FILE>  input titles path.
    -n <NAME_FILE>, --name=<NAME_FILE>     input names path.
"""
import json
import csv

from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from docopt import docopt

from helper import info, put_document

CHUNK_SIZE = 2000

TITLE_TO_NAME = {}

HEADERS = (
    'tconst',
    'titleType',
    'primaryTitle',
    'originalTitle',
    'isAdult',
    'startYear',
    'endYear',
    'runtimeMinutes',
    'genres',
    'averageRating',
    'numOfVotes',
)


@dataclass(frozen=True)
class Movie:
    primary_title: str
    original_title: str
    film_year: str
    genres: List[str]
    average_rating: float
    num_of_votes: int
    persons: List[str]


def convert(row: Dict, title_to_name: Dict) -> Movie:
    title_id = row['tconst']
    if title_id in title_to_name:
        persons = list(title_to_name[title_id])
    else:
        persons = []
    return Movie(
        primary_title=row['primaryTitle'],
        original_title=row['originalTitle'],
        film_year=int(row['startYear']),
        genres=row['genres'].split(','),
        average_rating=float(row['averageRating']),
        num_of_votes=int(row['numOfVotes']),
        persons=persons
    )


if __name__ == "__main__":
    options = docopt(__doc__)
    name_filepath = options['--name']
    title_filepath = options['--title']
    with open(name_filepath) as name_file:
        print(info('load {}').format(name_filepath))
        reader = csv.DictReader(name_file, delimiter="\t")
        for row in reader:
            name = row['primaryName']
            titles = row['knownForTitles'].split(',')
            for title in titles:
                if title not in TITLE_TO_NAME:
                    TITLE_TO_NAME[title] = set()
                TITLE_TO_NAME[title].add(name)

    chunked = []
    with open(title_filepath) as title_file:
        print(info('load {}').format(title_filepath))
        reader = csv.DictReader(title_file, delimiter="\t", fieldnames=HEADERS)
        for row in reader:
            es_doc = convert(row, TITLE_TO_NAME)
            doc_id = row['tconst']
            print(info(doc_id), end="\r")
            if len(chunked) < CHUNK_SIZE * 2:
                chunked.append('{"index":{"_id":"' + doc_id + '"}}')
                chunked.append(json.dumps(asdict(es_doc)))
            else:
                put_document(options['<ES_ENDPOINT>'], chunked)
                chunked = []
        put_document(options['<ES_ENDPOINT>'], chunked)

    
    

