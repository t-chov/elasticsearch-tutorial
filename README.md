# elasticsearch-tutorial

Elasticsearch tutorial.

## how to use

1. Use docker-compose
2. Provision data
    - It uses IMDb datasets.(sanitize with some condition)
    - Data will place in `rawdata/`

```sh
$ docker-compose up
$ bash provision.sh
```

notice: If you use Mac, you have to increase memory limit for docker.

## check URL

- http://localhost:9200/_cat/indices?v
- http://localhost:9200/imdb_persons/_search?q=kurosawa
