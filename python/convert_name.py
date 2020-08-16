"""
Usage:
    convert_name.py <ES_ENDPOINT> -f <INPUT_FILE>

Options:
    ES_ENDPOINT                           elasticsearch endpoint.
    -f <INPUT_FILE>, --file=<INPUT_FILE>  input file path.
"""
import json
import csv
import requests

from dataclasses import dataclass
from typing import List, Dict, Optional, Iterable
from docopt import docopt
from retry import retry
from colorama import init, Fore, Style

CHUNK_SIZE = 2000


@dataclass(frozen=True)
class Person:
    primary_name: str
    primary_profession: List[str]
    birth_year: Optional[int]
    death_year: Optional[int]

    def todict(self) -> Dict:
        person = {
            'primary_name': self.primary_name,
            'primary_profession': self.primary_profession,
        }
        if self.birth_year:
            person['birth_year'] = self.birth_year
        if self.death_year:
            person['death_year'] = self.death_year
        return person


def info(text: str) -> str:
    return Fore.CYAN + text + Style.RESET_ALL


def convert(row: Dict) -> Person:
    birth_year = int(row['birthYear']) if row['birthYear'] != '\\N' else None
    death_year = int(row['deathYear']) if row['deathYear'] != '\\N' else None
    profession = row['primaryProfession'].split(
        ',') if row['primaryProfession'] != '' else []
    return Person(
        primary_name=row['primaryName'],
        primary_profession=profession,
        birth_year=birth_year,
        death_year=death_year
    )


@retry(tries=3, delay=1)
def put_document(es_endpoint: str, docs: Iterable[str]):
    url = '{}/_bulk'.format(es_endpoint)
    header = {
        'Content-Type': 'application/json'
    }
    response = requests.put(url, data="\n".join(docs) + "\n", headers=header)
    response.raise_for_status()


if __name__ == "__main__":
    init()
    options = docopt(__doc__)
    input_filepath = options['--file']
    with open(input_filepath) as input_file:
        print(info('load {}').format(input_filepath))
        reader = csv.DictReader(input_file, delimiter="\t")
        chunked = []
        for row in reader:
            es_doc = convert(row)
            doc_id = row['nconst']
            print(info(doc_id), end="\r")
            if len(chunked) < CHUNK_SIZE * 2:
                chunked.append('{"index":{"_id":"' + doc_id + '"}}')
                chunked.append(json.dumps(es_doc.todict()))
            else:
                put_document(options['<ES_ENDPOINT>'], chunked)
                chunked = []
        put_document(options['<ES_ENDPOINT>'], chunked)
