#!/use/bin/env bash
set -o pipefail

readonly C=$(cd $(dirname $0); pwd)

function download_imdb_dataset {
    curl 'https://datasets.imdbws.com/name.basics.tsv.gz' -o - | \
      gzip -d | \
      awk -F"\t" '{ if ($6 != "\\N" && $5 != "" && $3 != "\\N") { print $0 }}' > ${C}/rawdata/name.basics.tsv
    curl 'https://datasets.imdbws.com/title.ratings.tsv.gz' | gzip -d > ${C}/rawdata/title.ratings.tsv
    curl 'https://datasets.imdbws.com/title.basics.tsv.gz' -o - | \
      gzip -d | \
      awk -F"\t" '{ if ($2 == "movie" && $6 >= 2000) { print $0 } }' | \
      join - ${C}/rawdata/title.ratings.tsv > ${C}/rawdata/title.basics.tsv
}

function provision_index {
    curl -XPUT 'http://localhost:9200/imdb_persons' -H 'Content-Type: application/json' -d '
    {
        "settings": {
            "number_of_shards": "1",
            "number_of_replicas": "1"
        },
        "mappings": {
            "properties": {
                "primary_name": {
                    "type": "text"
                },
                "birth_year": {
                    "type": "integer"
                },
                "death_year": {
                    "type": "integer"
                },
                "primary_profession": {
                    "type": "keyword"
                }
            }
        }
    }
    '
    curl -XPUT 'http://localhost:9200/movies' -H 'Content-Type: application/json' -d '
    {
        "settings": {
            "number_of_shards": "1",
            "number_of_replicas": "1"
        },
        "mappings": {
            "properties": {
                "primary_title": {
                    "type": "text"
                },
                "original_title": {
                    "type": "text"
                },
                "film_year": {
                    "type": "integer"
                },
                "runtime_minutes": {
                    "type": "integer"
                },
                "genres": {
                    "type": "keyword"
                },
                "average_rating": {
                    "type": "double"
                },
                "num_of_votes": {
                    "type": "long"
                },
                "persons": {
                    "type": "text"
                }
            }
        }
    }
    '
}

function convert {
    if [[ ! -d ${C}/python/venv ]]
    then
        python3 -m venv ${C}/python/venv
        source ${C}/python/venv/bin/activate
        pip3 install -r ${C}/python/requirements.txt
        deactivate
    fi
    source ${C}/python/venv/bin/activate
    python3 ${C}/python/convert_name.py 'http://localhost:9200/imdb_persons' -f rawdata/name.basics.tsv
    deactivate
}

function main {
    download_imdb_dataset || return $?
    provision_index || return $?
    convert || return $?
}

main
