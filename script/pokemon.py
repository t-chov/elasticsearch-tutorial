import csv
import json
import re
import sys
from typing import Any, Generator, Iterator, TextIO

NAME_JA_REGEXP = re.compile(r'[ァ-ヴ].+')


def read_pokemon_csv(input: TextIO) -> Generator[Iterator[dict[str, Any]], None, None]:
    reader = csv.DictReader(f=input)
    for row in reader:
        types = [row["type1"]]
        if len(row["type2"]) > 0:
            types.append(row["type2"])
        yield {
            "index": { "_index": "pokemon", "_id": row["pokedex_number"] },
        }
        yield {
            "pokedex_number": int(row["pokedex_number"]),
            "name_en": row["name"],
            "name_ja": NAME_JA_REGEXP.search(row["japanese_name"]).group(),
            "base_total": int(row["base_total"]),
            "attack": int(row["attack"]),
            "defense": int(row["defense"]),
            "sp_attack": int(row["sp_attack"]),
            "sp_defense": int(row["sp_defense"]),
            "speed": int(row["speed"]),
            "hp": int(row["hp"]),
            "capture_rate": int(row["capture_rate"]),
            "experience_growth": int(row["experience_growth"]),
            "types": types,
            "classification": row["classification"],
            "generation": int(row["generation"]),
            "is_legendary": row["is_legendary"] == "1",
        }


if __name__ == '__main__':
    for doc in read_pokemon_csv(sys.stdin):
        print(json.dumps(doc))
