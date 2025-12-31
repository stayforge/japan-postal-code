# japan-postal-code
JSON / YAML / CSV / XML / Parquet / MessagePack / NDJSON / TOML / Feather / BSON / SQLite | 日本の郵便番号データ、毎月1回更新します | Japan postal code data

## Supported Formats

| Format | 利点 (Advantages) | URL                                                                                |
|--------|------------------|------------------------------------------------------------------------------------|
| **JSON** | **日本語:**<br>人間が読みやすく、理解・編集が容易<br>幅広い言語でサポートされており、ほぼ全てのプログラミング言語にパースライブラリがある<br>軽量で構造がシンプル<br>API のデータ交換や設定ファイルに適している<br>JavaScript でネイティブサポートされており、フロントエンド開発に親和性が高い<br><br>**English:**<br>Human-readable, easy to understand and edit<br>Widely supported, parsing libraries available in almost all programming languages<br>Lightweight with simple structure<br>Suitable for API data exchange and configuration files<br>Native JavaScript support, frontend development friendly | [all_data.json](https://stayforge.github.io/japan-postal-code/datasets/all_data.json)       |
| **YAML** | **日本語:**<br>可読性が非常に高く、構文が簡潔で明確<br>コメントや複数行文字列をサポート<br>設定ファイルやデータのシリアライズに適している<br>複雑なデータ構造（リスト、辞書、多層ネスト）をサポート<br>JSON よりも手動編集の場面に適している<br><br>**English:**<br>Excellent readability with concise and clear syntax<br>Supports comments and multi-line strings<br>Suitable for configuration files and data serialization<br>Supports complex data structures (lists, dictionaries, multi-level nesting)<br>More suitable for manual editing scenarios than JSON | [all_data.yaml](https://stayforge.github.io/japan-postal-code/datasets/all_data.yaml)       |
| **CSV** | **日本語:**<br>フォーマットがシンプルで、理解・使用が容易<br>Excel などのスプレッドシートソフトウェアで直接サポート<br>ファイルサイズが小さく、大量のデータに適している<br>テキスト形式で、任意のテキストエディタで開ける<br>データのインポート・エクスポートシーンで広く使用されている<br><br>**English:**<br>Simple format, easy to understand and use<br>Directly supported by spreadsheet software like Excel<br>Small file size, suitable for large amounts of data<br>Text format, can be opened with any text editor<br>Widely used in data import/export scenarios | [all_data.csv](https://stayforge.github.io/japan-postal-code/datasets/all_data.csv)         |
| **XML** | **日本語:**<br>構造化度が高く、複雑な階層関係をサポート<br>自己記述性があり、カスタムタグを定義可能<br>名前空間と Schema 検証をサポート<br>エンタープライズシステムやデータ交換で広く使用されている<br>豊富な標準とツールサポート<br><br>**English:**<br>Highly structured, supports complex hierarchical relationships<br>Self-descriptive, can define custom tags<br>Supports namespaces and Schema validation<br>Widely used in enterprise systems and data exchange<br>Rich standards and tool support | [all_data.xml](https://stayforge.github.io/japan-postal-code/datasets/all_data.xml)         |
| **Parquet** | **日本語:**<br>列指向ストレージフォーマットで、クエリと圧縮の効率が非常に高い<br>自動圧縮により、ファイルサイズが小さい（通常 CSV より 10-100 倍小さい）<br>フィールドレベルの統計情報とインデックスをサポート<br>ビッグデータ分析やデータウェアハウスシーンに適している<br>言語横断的な互換性（Python, R, Java, Spark など）<br><br>**English:**<br>Columnar storage format with extremely high query and compression efficiency<br>Automatic compression results in small file size (typically 10-100x smaller than CSV)<br>Supports field-level statistics and indexes<br>Suitable for big data analysis and data warehouse scenarios<br>Cross-language compatibility (Python, R, Java, Spark, etc.) | [all_data.parquet](https://stayforge.github.io/japan-postal-code/datasets/all_data.parquet) |
| **MessagePack** | **日本語:**<br>バイナリ形式で、ファイルサイズが JSON より 20-30% 小さい<br>シリアライズ/デシリアライズの速度が非常に速い<br>より多くのデータ型（バイナリ、拡張型など）をサポート<br>言語横断的な互換性<br>ネットワーク転送や高性能シーンに適している<br><br>**English:**<br>Binary format with file size 20-30% smaller than JSON<br>Extremely fast serialization/deserialization<br>Supports more data types (binary, extended types, etc.)<br>Cross-language compatibility<br>Suitable for network transmission and high-performance scenarios | [all_data.msgpack](https://stayforge.github.io/japan-postal-code/datasets/all_data.msgpack) |
| **NDJSON (JSONL)** | **日本語:**<br>1行に1つの JSON オブジェクトで、ストリーミング処理をサポート<br>行単位で読み書きでき、ファイル全体をメモリに読み込む必要がない<br>超大規模データセット（数GB以上）の処理に適している<br>データの追加が容易で、ファイル末尾に行を追加するだけでよい<br>ログ記録やビッグデータ処理でよく使用される<br><br>**English:**<br>One JSON object per line, supports streaming processing<br>Can read/write line by line without loading entire file into memory<br>Suitable for processing very large datasets (several GB or more)<br>Easy to append data, just add lines to the end of the file<br>Commonly used in log recording and big data processing | [all_data.ndjson](https://stayforge.github.io/japan-postal-code/datasets/all_data.ndjson)   |
| **TOML** | **日本語:**<br>YAML よりも構文がシンプルで明確<br>型が明確で、パースの曖昧さを減らす<br>設定ファイル（Rust の Cargo.toml など）に適している<br>人間が読みやすく、機械解析も容易<br>YAML の一部のセキュリティ問題を回避<br><br>**English:**<br>Simpler and clearer syntax than YAML<br>Explicit types reduce parsing ambiguity<br>Suitable for configuration files (e.g., Rust's Cargo.toml)<br>Human-readable and easy for machines to parse<br>Avoids some security issues with YAML | [all_data.toml](https://stayforge.github.io/japan-postal-code/datasets/all_data.toml)       |
| **Feather** | **日本語:**<br>Apache Arrow 形式で、メモリマッピング読み込みにより速度が非常に速い<br>ゼロコピー読み込みで、シリアライズ/デシリアライズが不要<br>言語横断的な相互運用性（Python、R、Julia など）<br>データ型情報を保持<br>データサイエンスや分析ワークフローに適している<br><br>**English:**<br>Apache Arrow format with extremely fast memory-mapped reading<br>Zero-copy reading without serialization/deserialization<br>Cross-language interoperability (Python, R, Julia, etc.)<br>Preserves data type information<br>Suitable for data science and analysis workflows | [all_data.feather](https://stayforge.github.io/japan-postal-code/datasets/all_data.feather) |
| **BSON** | **日本語:**<br>バイナリ JSON で、JSON の全ての利点を保持<br>ファイルサイズが JSON より小さい<br>より多くのデータ型（日付、バイナリ、正規表現など）をサポート<br>MongoDB のネイティブ形式で、クエリとインデックスの効率が高い<br>データベースストレージやネットワーク転送に適している<br><br>**English:**<br>Binary JSON that retains all advantages of JSON<br>Smaller file size than JSON<br>Supports more data types (dates, binary, regular expressions, etc.)<br>MongoDB's native format with efficient queries and indexes<br>Suitable for database storage and network transmission | [all_data.bson](https://stayforge.github.io/japan-postal-code/datasets/all_data.bson)       |
| **SQLite** | **日本語:**<br>ファイルベースのデータベースで、独立したサーバーが不要<br>SQL クエリをサポートし、インデックスを作成してクエリを高速化できる<br>ACID 特性により、データ整合性が保証される<br>軽量（コアライブラリは数百KBのみ）<br>アプリケーション組み込みデータベースやデータ分析に適している<br><br>**English:**<br>File-based database, no separate server required<br>Supports SQL queries, can create indexes to speed up queries<br>ACID properties ensure data integrity<br>Lightweight (core library is only several hundred KB)<br>Suitable for embedded databases in applications and data analysis | [all_data.db](https://stayforge.github.io/japan-postal-code/datasets/all_data.db)           |

## グループ化データ構造 / Grouped Data Structure

### 概要 / Overview

**日本語:**
データは郵便番号の前3桁でグループ化され、階層的なファイル構造で提供されています。これにより、単一ファイルのサイズを削減し、特定の地域のデータを効率的に取得できます。

**English:**
Data is grouped by the first 3 digits of postal codes and provided in a hierarchical file structure. This reduces the size of individual files and allows efficient retrieval of data for specific regions.

### ファイル構造 / File Structure

```
datasets/
├── 176.json          # 176で始まる全ての郵便番号の完全なレコードリスト
├── 176.yaml          # All postal codes starting with 176
├── 176.csv
├── 176/
│   ├── 0005.json     # 郵便番号 1760005 の完全なレコード
│   ├── 0005.yaml     # Complete record for postal code 1760005
│   ├── 0005.csv
│   ├── 0006.json     # 郵便番号 1760006 の完全なレコード
│   └── ...
├── 177.json
├── 177/
│   └── ...
└── ...
```

### データ取得方法 / How to Retrieve Data

#### 方法1: 前3桁でグループ全体を取得 / Method 1: Get All Records by Prefix

**日本語:**
特定の地域（前3桁）の全ての郵便番号データを取得する場合：

**例: 176で始まる全ての郵便番号を取得**
```javascript
// JavaScript の例
fetch('https://stayforge.github.io/japan-postal-code/datasets/176.json')
  .then(response => response.json())
  .then(data => {
    // data は 176 で始まる全ての郵便番号の配列
    console.log(data);
  });
```

```python
# Python の例
import requests
import json

response = requests.get('https://stayforge.github.io/japan-postal-code/datasets/176.json')
data = response.json()
# data は 176 で始まる全ての郵便番号のリスト
```

**English:**
To retrieve all postal code data for a specific region (first 3 digits):

**Example: Get all postal codes starting with 176**
```javascript
// JavaScript example
fetch('https://stayforge.github.io/japan-postal-code/datasets/176.json')
  .then(response => response.json())
  .then(data => {
    // data is an array of all postal codes starting with 176
    console.log(data);
  });
```

```python
# Python example
import requests
import json

response = requests.get('https://stayforge.github.io/japan-postal-code/datasets/176.json')
data = response.json()
# data is a list of all postal codes starting with 176
```

#### 方法2: 特定の郵便番号を直接取得 / Method 2: Get Specific Postal Code

**日本語:**
完全な7桁の郵便番号が分かっている場合、直接そのファイルを取得できます：

**例: 郵便番号 1760005 を取得**
```javascript
// JavaScript の例
fetch('https://stayforge.github.io/japan-postal-code/datasets/176/0005.json')
  .then(response => response.json())
  .then(data => {
    // data は 1760005 の郵便番号データ（単一オブジェクトまたは配列）
    console.log(data);
  });
```

```python
# Python の例
import requests

# 郵便番号を分割
postal_code = "1760005"
prefix = postal_code[:3]  # "176"
suffix = postal_code[3:]  # "0005"

url = f'https://stayforge.github.io/japan-postal-code/datasets/{prefix}/{suffix}.json'
response = requests.get(url)
data = response.json()
# data は 1760005 の郵便番号データ
```

**English:**
If you know the complete 7-digit postal code, you can directly retrieve that file:

**Example: Get postal code 1760005**
```javascript
// JavaScript example
fetch('https://stayforge.github.io/japan-postal-code/datasets/176/0005.json')
  .then(response => response.json())
  .then(data => {
    // data is the postal code data for 1760005 (single object or array)
    console.log(data);
  });
```

```python
# Python example
import requests

# Split postal code
postal_code = "1760005"
prefix = postal_code[:3]  # "176"
suffix = postal_code[3:]  # "0005"

url = f'https://stayforge.github.io/japan-postal-code/datasets/{prefix}/{suffix}.json'
response = requests.get(url)
data = response.json()
# data is the postal code data for 1760005
```

### 利点 / Advantages

**日本語:**
- **ファイルサイズの削減**: 単一の大きなファイルではなく、小さなファイルに分割されるため、必要なデータのみをダウンロードできます
- **高速な取得**: 特定の地域や郵便番号のデータを直接取得できるため、全体を読み込む必要がありません
- **帯域幅の節約**: 必要なデータのみを取得することで、ネットワーク帯域幅を節約できます
- **キャッシュ効率**: 小さなファイルはブラウザやCDNでキャッシュしやすく、再取得が高速です
- **GitHub Pages との互換性**: 静的ファイルホスティングに最適化されており、GitHub Pages で直接提供できます

**English:**
- **Reduced File Size**: Data is split into smaller files instead of one large file, allowing you to download only the data you need
- **Faster Retrieval**: You can directly retrieve data for specific regions or postal codes without loading the entire dataset
- **Bandwidth Savings**: Fetching only the required data saves network bandwidth
- **Cache Efficiency**: Smaller files are easier to cache in browsers or CDNs, enabling faster subsequent retrievals
- **GitHub Pages Compatibility**: Optimized for static file hosting and can be directly served via GitHub Pages

### 対応フォーマット / Supported Formats

全てのフォーマット（JSON, YAML, CSV, XML, Parquet, MessagePack, NDJSON, TOML, Feather, BSON）でグループ化されたデータが提供されています。

All formats (JSON, YAML, CSV, XML, Parquet, MessagePack, NDJSON, TOML, Feather, BSON) are available in grouped structure.

**例 / Examples:**
- `https://stayforge.github.io/japan-postal-code/datasets/176.json`
- `https://stayforge.github.io/japan-postal-code/datasets/176.yaml`
- `https://stayforge.github.io/japan-postal-code/datasets/176/0005.json`
- `https://stayforge.github.io/japan-postal-code/datasets/176/0005.csv`

## 著作権 / Copyright

**日本語:**
本プロジェクトで提供されている郵便番号データの著作権は、日本郵便株式会社（Japan Post）に帰属します。本プロジェクトは、日本郵便が提供する公式データに対して、データの分割とクリーンアップ（整理）のみを行っており、データの内容自体は変更していません。

**English:**
The copyright of the postal code data provided in this project belongs to Japan Post Co., Ltd. This project only performs data splitting and cleaning (organization) on the official data provided by Japan Post, and does not modify the content of the data itself.
