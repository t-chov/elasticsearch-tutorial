# 2 用語と基本的なデータ投入

Elasticsearch (以下 Es と表記) は **全文検索** を得意とするソフトウェアである。
その他にも得意なことは多いが、多くのソフトウェアエンジニアにとってなじみ深い RDB とは以下のような違いがある。

これらは初学者に向けて厳密性を欠いた解説になるが、雰囲気を掴むための説明である。
Es に限らず、lucene 系の全文検索エンジンでは似たような傾向を持つ。

| 項目             | Es       | RDB                              |
| ---------------- | -------- | -------------------------------- |
| 入力の正規化     | 簡単     | RDB だけでは基本的には完結しない |
| 全文検索         | 高速     | 基本的には低速                   |
| 値の集計         | 高速     | インデックス次第では低速         |
| 表の結合         | できない | できる                           |
| トランザクション | できない | できる                           |

また、RDB の用語と Es の用語では相違が存在する。大まかな対応は以下の通り。

| Es           | RDB      |
| ------------ | -------- |
| インデックス | テーブル |
| フィールド   | カラム   |
| ドキュメント | レコード |

Es では **インデックス** という単位でデータをまとめて管理する。インデックスをまたいだ検索はできるが、インデックス間の結合はできない。

投入するデータは **ドキュメント** という単位で管理される。ドキュメントは **フィールド** を持ち、フィールドが値を持っている。

早速データを投入してみよう。引き続き Dev Tools を使う。

## 2.1 データを投入して感覚を掴む

Dev Tools に以下の内容を追記し、実行してみよう。もしもフシギダネが嫌いなら、ヒトカゲやゼニガメのデータを送っても良いだろう。

```json
PUT example_index/_doc/1
{
  "id": 1,
  "name": "Bulbasaur",
  "type": ["grass", "poison"]
}
```

id, name, type の 3 フィールドを持つ。色々と試したい人は高さや重さ、特性や種族値を入れても良いだろう。
公式ドキュメントの [Update API](https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-update.html) を参照のこと。

成功すれば、Es からは以下のような応答が返る。

```json
{
  "_index": "example_index",
  "_id": "1",
  "_version": 1,
  "result": "created",
  "_shards": {
    "total": 1,
    "successful": 1,
    "failed": 0
  },
  "_seq_no": 0,
  "_primary_term": 1
}
```

フシギダネが投入されたので、次はフシギソウとフシギバナを投入しよう。

```json
PUT example_index/_doc/2
{
  "id": 2,
  "name": "Ivysaur",
  "type": ["grass", "poison"]
}
PUT example_index/_doc/3
{
  "id": 3,
  "name": "Venusaur",
  "type": ["grass", "poison"]
}
```

これで、 `example_index` インデックスには

- id: 1 の Bulbasaur
- id: 2 の Ivysaur
- id: 3 の Venusaur

の 3 ドキュメントが投入された。

## 2.2 最初の検索

Elasticsearch は全文検索エンジンなので、検索をしてみよう。まずは最も簡単なクエリを発行する。

```json
GET example_index/_search
{
  "query": {
    "match_all": {}
  }
}
```

実行すれば、3 ドキュメントが返却されるはずだ。

このインデックスはもう使わないので、インデックスを削除する。

```json
DELETE example_index
```

[prev: はじめに](./01_introduciton.md) / [next: 実践的なインデックスを作成する](./03_create_practical_index.md)
