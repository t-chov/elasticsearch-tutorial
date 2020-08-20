# 触りながら学ぶ Elasticsearch

## 本チュートリアルの対象

- Elasticsearch 初心者
- 全文検索エンジンを触ってみたい人
- 既存のチュートリアルだとデータ投入周りが弱くてモヤモヤしてる人

## 投入するデータ

[IMDb Datasets](https://www.imdb.com/interfaces/) を利用する。これにはいくつか理由がある。

1. 全文検索エンジンの多くは英語のために最適化されており、日本語データセットを利用する場合は設定が必要である
2. IMDb は無料かつデータ量が多く、かつ映画というトピックは「検索」という題材に適切であること
3. IMDb Datasets は TSV がダンプされるため、システム構成を単純にできること(RDBを必要としない)

本チュートリアルでは、映画人と2000年以降の映画データを検索対象とする。

## データ投入

`provision.sh` で実施している処理を解説する。

```sh
function download_imdb_dataset {
    # 代表作、役職、生年が確定している者のみを抽出する
    # gz ファイルを標準出力に渡して gzip -d することでファイルを経由せずに解凍を行う
    # 出力されるのは TSV なので awk で処理できる
    curl 'https://datasets.imdbws.com/name.basics.tsv.gz' -o - | \
      gzip -d | \
      awk -F"\t" '{ if ($6 != "\\N" && $5 != "" && $3 != "\\N") { print $0 }}' > ${C}/rawdata/name.basics.tsv
    # 評価数データはそのまま利用
    curl 'https://datasets.imdbws.com/title.ratings.tsv.gz' | gzip -d > ${C}/rawdata/title.ratings.tsv
    # 2000 年以降に制作された映画を抽出する
    # join コマンドを利用して評価数データを結合する
    curl 'https://datasets.imdbws.com/title.basics.tsv.gz' -o - | \
      gzip -d | \
      awk -F"\t" '{ if ($2 == "movie" && $6 != "\\N" && $6 >= 2000) { print $0 } }' | \
      join -t "	" - ${C}/rawdata/title.ratings.tsv > ${C}/rawdata/title.basics.tsv
}
```

出力されたデータは以下のようになっている。

**name.basics.tsv**

```tsv
nconst	primaryName	birthYear	deathYear	primaryProfession	knownForTitles
nm0000001	Fred Astaire	1899	1987	soundtrack,actor,miscellaneous	tt0050419,tt0031983,tt0053137,tt0072308
nm0000002	Lauren Bacall	1924	2014	actress,soundtrack	tt0038355,tt0037382,tt0117057,tt0071877
```

**title.basics.tsv**
```
tt0016906	movie	Frivolinas	Frivolinas	0	2014	\N	80	Comedy,Musical	5.6	15
tt0035423	movie	Kate & Leopold	Kate & Leopold	0	2001	\N	118	Comedy,Fantasy,Romance	6.4	77701
tt0062336	movie	El Tango del Viudo y Su Espejo Deformante	El Tango del Viudo y Su Espejo Deformante	0	2020	\N	70	Drama	6.7	38
```

データがダウンロードできたら、インデックスを作成する。 
( [ドキュメント](https://www.elastic.co/guide/en/elasticsearch/reference/7.8/indices-create-index.html) )
Elasticsearch7 では `type` がなくなったため、 ES6 以前のインデックスを作成APIは無効。
インデックス作成は PUT メソッドで `<ES_HOST>/<INDEX_NAME>` に以下のような json を送る。
参考: [デフォルトで有効なデータタイプ一覧](https://www.elastic.co/guide/en/elasticsearch/reference/7.8/mapping-types.html)



```json
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
```

シャード数は後から変えられないが、レプリカセット数は変更できる。
やり方については [公式](https://www.elastic.co/guide/en/elasticsearch/reference/7.8/indices-update-settings.html) を参照。

上記では　`persons` は複数の値が入るが、ES側でよしなにしてくれる。

## データ投入

`convert_title.py` で実施している。
ここでのポイントは [Bulk API](https://www.elastic.co/guide/en/elasticsearch/reference/7.8/docs-bulk.html) を利用している点。

一括投入の場合は　Bulk API を利用するほうが効率が良い。ただし、

```
{"index":{"_id":"foo"}}
{"name":"bar","category":"baz"}
```

のように、 コマンド行と内容の行を分ける必要がある。
また、 **末尾に `\n` がないとエラーとなる** ので注意が必要。

上記の操作は `PUT /<index>/_doc/<_id>` と等価である。
[Index API](https://www.elastic.co/guide/en/elasticsearch/reference/7.8/docs-index_.html) は個別の操作でのみ用いる。