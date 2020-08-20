# 触りながら学ぶ Elasticsearch 基本クエリ

## インデクシングできたら

以下のAPIで確認してみる

* [インデックス一覧](http://localhost:9200/_cat/indices?v)
* [アイ・アム・サムを出す](http://localhost:9200/movies/_doc/tt0277027)
* [300で検索](http://localhost:9200/movies/_search?q=300)

## 検索APIを追ってみる

text: https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl.html

### match クエリ

match クエリは 

```json
{
  "query": {
    "match": {
      "<field>": {
        "query": "<value>"
      }
    }
  }
}
```

のような形式で検索する。たとえば _The Bourne Identity_ で検索してみよう

```sh
curl -i -X POST \
   -H "Content-Type:application/json" \
   -d \
'{
  "query": {
    "match": {
      "primary_title": {
        "query": "The Bourne Identity"
      }
    }
  }
}' \
 'http://localhost:9200/movies/_search?pretty'
```

10000 件以上がヒットするが、検索条件が `The OR Bourne OR Identity` になっているためである。
AND 検索にするためには以下のようにする。

```sh
curl -i -X POST \
   -H "Content-Type:application/json" \
   -d \
'{
  "query": {
    "match": {
      "primary_title": {
        "query": "The Bourne Identity",
        "operator": "AND"
      }
    }
  }
}' \
 'http://localhost:9200/movies/_search?pretty'
```

こうすることで、ボーン・アイデンティティのみがヒットするようになった、

### match_phrase クエリ

AND 検索では不十分な場合がある。たとえば語順が重要な場合がそれである。

極端な例だが、 `Michael Fox` で AND 検索をすると `Micael J. Fox` などもヒットする。例を見てみよう。

**match query**
```sh
curl -i -X POST \
   -H "Content-Type:application/json" \
   -d \
'{
  "query": {
    "match": {
      "persons": {
        "query": "michael fox",
        "operator": "AND"
      }
    }
  }
}' \
 'http://localhost:9200/movies/_search?pretty'
```

マイケル・フォックス氏のみならず、マイケル・レイ・フォックス氏などもヒットしていることがわかる。
フレーズクエリを利用すると以下のようになる。

**match_phrase query**
```sh
curl -i -X POST \
   -H "Content-Type:application/json" \
   -d \
'{
  "query": {
    "match_phrase": {
      "persons": {
        "query": "michael fox"
      }
    }
  }
}' \
 'http://localhost:9200/movies/_search?pretty'
```

Hard Shoulder というスリラー映画だけヒットした。
この映画にはマイケル・フォックス氏が関わっているようだ。

### term クエリ

term クエリは　solr でいう fq のような使い方ができる。主に `keyword` 型の絞り込みに使う。

```sh
curl -i -X POST \
   -H "Content-Type:application/json" \
   -d \
'{
  "query": {
    "term": {
      "genres": "Sci-Fi"
    }
  }
}' \
 'http://localhost:9200/movies/_search?pretty'
```


```sh
curl -i -X POST \
   -H "Content-Type:application/json" \
   -d \
'{
  "query": {
    "terms": {
      "genres": ["Sci-Fi", "Animation"]
    }
  }
}' \
 'http://localhost:9200/movies/_search?pretty'
```

複数のOR検索する場合は `terms` を使う。

### range クエリ

範囲検索を行う。

```sh
curl -i -X POST \
   -H "Content-Type:application/json" \
   -d \
'{
  "query": {
    "range": {
      "film_year": {
        "gte": 2010,
        "lte": 2015
      }
    }
  }
}' \
 'http://localhost:9200/movies/_search?pretty'
```

* `gte` : 以上
* `lte` : 以下
* `gt` : 〜より大きい
* `lt` : 〜未満

gt系, lt系は必ずしも両方用意する必要はない. 例は以下

```sh
curl -i -X POST \
   -H "Content-Type:application/json" \
   -d \
'{
  "query": {
    "range": {
      "film_year": {
        "gte": 2018
      }
    }
  }
}' \
 'http://localhost:9200/movies/_search?pretty'
```

日付型は相対計算できる ( 例: `now-1w` )