# 1 はじめに

本資料はハンズオン形式で Elasticsearch に慣れるための資料である。

## 1.1 本資料で解説すること

- docker を利用した簡単な環境構築
- Bulk API を利用したデータ投入
- 効率的なクエリの考え方

## 1.2 本資料で解説しないこと

- 実サービスでのインフラ構成
- データ更新フローの構築

# 2 環境構築

docker compose を利用して環境を構築する。実サービスではないことから、構成を簡単にするためにデフォルト設定から以下の変更を加えている。

1. セキュリティ機能を切り、パスワードを設定せずに HTTP 通信を可能にしている
2. 他のポートと被らないよう、デフォルトの動作ポートから 20000 のオフセットを設けている
   - elasticsearch: 9200 -> 29200
   - kibana: 5601 -> 25601

kibana は主に Dev Tools を利用するために利用する。

まずは docker compose でコンテナを立ち上げよう。

```bash
# バージョンによっては docker-compose で実行
docker compose up -d
```

コンテナが起動したら

- http://localhost:29200/
- http://localhost:25601/app/dev_tools#/console

で Elasticsearch, kibana が起動していることを確認する。

Elasticsearch が起動していれば以下のような表示がされる。

```json
{
  "name": "0bcf88e8a5fe",
  "cluster_name": "docker-cluster",
  "cluster_uuid": "9SFQ80bDTsm9xKHnRlIM3w",
  "version": {
    "number": "8.8.2",
    "build_flavor": "default",
    "build_type": "docker",
    "build_hash": "98e1271edf932a480e4262a471281f1ee295ce6b",
    "build_date": "2023-06-26T05:16:16.196344851Z",
    "build_snapshot": false,
    "lucene_version": "9.6.0",
    "minimum_wire_compatibility_version": "7.17.0",
    "minimum_index_compatibility_version": "7.0.0"
  },
  "tagline": "You Know, for Search"
}
```

Kibana の Dev Tools に以下の内容を記載しよう。元々の内容は削除して良い。

```json
PUT example_index
{
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 0
  }
}

GET _cat/indices
```

正しく起動していれば、 `_cat/indices` は値を返す。

```
green open example_index tsYdEH4VTqq-8QltANSjYw 1 0 0 0 247b 247b
```

/ [next: 用語](./02_words.md)
