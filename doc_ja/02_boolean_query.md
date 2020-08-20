# 触りながら学ぶ Elasticsearch 複合クエリ

## 複合クエリ

複合クエリは `must` `should` `must_not` `filter` の4つで構成される。

```json
{
    "query": {
        "bool": {
            "must": [ <queries> ],
            "should": [ <queries> ],
            "must_not": [ <queries> ],
            "filter": [ <queries> ]
        }
    }
}
```

たとえばフレーズクエリを利用して `The Girl with the Dragon Tattoo` を検索した場合、2009年のスウェーデン映画と2011年のハリウッド映画の両方がヒットする。

```sh
curl -i -X POST \
   -H "Content-Type:application/json" \
   -d \
'{
  "query": {
    "match_phrase": {
      "primary_title": {
        "query": "The Girl with the Dragon Tattoo"
      }
    }
  }
}' \
 'http://localhost:9200/movies/_search?pretty'
```

2011 年のほうに絞りたいのであれば、 bool クエリを利用する。

```sh
curl -i -X POST \
   -H "Content-Type:application/json" \
   -d \
'{
  "query": {
    "bool": {
      "must": [
        {"match_phrase": {"primary_title": {"query": "The Girl with the Dragon Tattoo"}}}
      ],
      "filter": [
        {"term":{"film_year":2011}}
      ]
    }
  }
}' \
 'http://localhost:9200/movies/_search?pretty'
```

備考: `must`, `should`, `must_not` はスコアに影響するが、 `filter` はスコアに影響しない。

## クエリのソート

たとえば `star wars` で検索すると、 [Saving Star Wars](https://en.wikipedia.org/wiki/Saving_Star_Wars) なる謎の映画がトップするので、 IMDb のレビュー数でソートしてみる。

謎のコメディ映画がヒットするクエリ

```sh
curl -i -X POST \
   -H "Content-Type:application/json" \
   -d \
'{
  "query": {
    "bool": {
      "must": [
        {"match_phrase": {"primary_title": {"query": "star wars"}}}
      ]
    }
  }
}' \
 'http://localhost:9200/movies/_search?pretty'
```

ソートしたクエリ

```sh
curl -i -X POST \
   -H "Content-Type:application/json" \
   -d \
'{
  "query": {
    "bool": {
      "must": [
        {"match_phrase": {"primary_title": {"query": "star wars"}}}
      ]
    }
  },
  "sort": [
    {"num_of_votes":{"order":"desc"}}
  ]
}' \
 'http://localhost:9200/movies/_search?pretty'
```

こうするとEP7がトップにヒットする。めでたしめでたし。

スコアソートをしたい場合は `_score` でソートする。

### 他の複合クエリ

例として使いやすいためスターウォーズを引き続き使う。

`must` と　`must_not` は併用できる。下記はマーク・ハミルが出演していないスターウォーズを検索する。

```sh
curl -i -X POST \
   -H "Content-Type:application/json" \
   -d \
'{
  "query": {
    "bool": {
      "must": [
        {"match_phrase": {"primary_title": {"query": "star wars"}}}
      ],
      "must_not": [
        {"match": {"persons": {"query": "Mark Hamill"}}}
      ]
    }
  },
  "sort": [
    {"num_of_votes":{"order":"desc"}}
  ]
}' \
 'http://localhost:9200/movies/_search?pretty'
 ```

 この条件だと、EP3が最上位となる。確かにマークハミルが出ていない。

 `must` と　`should` は併用できない。

 ```json
 {
  "query": {
    "bool": {
      "must": [
        {"match_phrase": {"primary_title": {"query": "star wars"}}}
      ],
      "should": [
        {"match":{"persons":{"query":"Mark Hamill"}}},
        {"match":{"persons":{"query":"Samuel L. Jackson"}}}
      ],
      "filter": [
        {"term": {"genres": "Sci-Fi"}}
      ]
    }
  },
  "sort": [
    {"_score":{"order":"desc"}}
  ]
}
```
このようなクエリを送っても、マーク・ハミルやサミュエル・L・ジャクソンが重視されるわけではない。