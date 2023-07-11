# 3 実践的なインデックスを作成する

ここからは実践的なインデックスを作成する。

日本語特有の問題を解説したいため、 [pokemon.csv](https://gist.github.com/leoyuholo/b12f882a92a25d43cf90e29812639eb3) を用いる。

## 3.1 インデックス作成

まずはインデックスを作成する。 Dev Tools で以下の内容を実行する。

```json
PUT pokemon
{
    "settings" : {
        "number_of_shards": 1,
        "number_of_replicas": 0,
        "analysis": {
            "analyzer": {
                "bigram": {
                    "tokenizer": "bigram_tokenizer",
                    "filter": [
                        "cjk_width", "asciifolding", "lowercase"
                    ]
                }
            },
            "tokenizer": {
                "bigram_tokenizer": {
                    "type":     "ngram",
                    "min_gram": 2,
                    "max_gram": 2,
                    "token_chars": []
                }
            }
        }
    },
    "mappings": {
        "properties": {
            "pokedex_number": { "type": "integer" },
            "name_en": { "type": "text", "analyzer": "standard" },
            "name_ja": { "type": "text", "analyzer": "bigram" },
            "base_total": { "type": "integer" },
            "attack": { "type": "integer" },
            "defense": { "type": "integer" },
            "sp_attack": { "type": "integer" },
            "sp_defense": { "type": "integer" },
            "speed": { "type": "integer" },
            "hp": { "type": "integer" },
            "capture_rate": { "type": "integer" },
            "experience_growth": { "type": "integer" },
            "types": { "type": "keyword" },
            "classification": { "type": "text", "analyzer": "standard" },
            "generation": { "type": "integer" },
            "is_legendary": { "type": "boolean" }
        }
    }
}
```

`analysis` という項目が増えたが、これは文章をどのように解析するかを設定するために用いる。
詳細は公式ドキュメント [Text analysis overview](https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis-overview.html) を参照してほしい。

この設定では 2 gram での解析を行うための設定を追加している。
N-gram による検索については [gihyo.jp の検索エンジンを作る 第 5 回](https://gihyo.jp/dev/serial/01/make-findspot/0005) に解説があるので参照してほしい。

`mappings` はデータベースでいうなれば各カラムのスキーマ設定である。
Elasticsearch の場合、特別な設定を加えなくても複数の値をフィールドに投入できる。
このポケモンの例では `types` に複数の値が入りうる。

## 3.2 データ投入

今回は [pokemon.csv](https://gist.github.com/leoyuholo/b12f882a92a25d43cf90e29812639eb3) を利用する。
第 7 世代までのデータしかなく、リージョンフォームも考慮されていないが、リージョンフォームを考慮するとドキュメント ID が複雑になるのでむしろ好都合である。

データ整形を行いたいため、少し手を加える。
[script/pokemon.csv](../../script/pokemon.csv) を実行しよう。
特に外部パッケージは利用していないので、 curl があれば動くはずだ。

```bash
curl -s 'https://gist.githubusercontent.com/leoyuholo/b12f882a92a25d43cf90e29812639eb3/raw/1abee7fb529dfacb374633f3a450b37634f8321a/pokemon.csv' | \
    python script/pokemon.py | \
    curl -H 'Content-Type:application/json' \
    http://localhost:29200/pokemon/_bulk --data-binary @-
```

データ投入には [Bulk API](https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-bulk.html) を用いている。詳細はスクリプトの中身を参照してほしい。

無事にデータが投入されたら、クエリを実行してみよう。無事に 801 匹のポケモンが投入されているはずだ。

```json
GET pokemon/_search
{
  "query": { "match_all": {}}
}
```

[prev: 用語と基本的なデータ投入](./02_words.md) /
