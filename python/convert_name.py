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
from typing import List, Dict, Optional
from docopt import docopt
from retry import retry
from colorama import init, Fore, Style


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
    profession = row['primaryProfession'].split(',') if row['primaryProfession'] != '\\N' else []
    return Person(
        primary_name=row['primaryName'],
        primary_profession=profession,
        birth_year=birth_year,
        death_year=death_year
    )


@retry(tries=3, delay=1)
def put_document(es_endpoint:str, doc_id:str, doc:Person):
    url = '{}/{}'.format(es_endpoint, doc_id)
    header = {
        'Content-Type': 'application/json'
    }
    response = requests.put(url, data=json.dumps(doc.todict()), headers=header)
    response.raise_for_status()


if __name__ == "__main__":
    init()
    options = docopt(__doc__)
    input_filepath = options['--file']
    with open(input_filepath) as input_file:
        print(info('load {}').format(input_filepath))
        reader = csv.DictReader(input_file, delimiter="\t")
        for row in reader:
            es_doc = convert(row)
            doc_id = row['nconst']
            print(info(doc_id), end="\r")
            put_document(options['<ES_ENDPOINT>'], doc_id, es_doc)