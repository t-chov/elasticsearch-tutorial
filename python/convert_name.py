"""
Usage:
    convert_name.py <ES_ENDPOINT> -f <INPUT_FILE>

Options:
    ES_ENDPOINT                           elasticsearch endpoint.
    -f <INPUT_FILE>, --file=<INPUT_FILE>  input file path.
"""
import json
import csv

from dataclasses import dataclass
from typing import List, Dict, Optional
from docopt import docopt
from helper import info, put_document

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


if __name__ == "__main__":
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
