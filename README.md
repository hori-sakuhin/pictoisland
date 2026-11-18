# Picto Island（ピクトアイランド）

## 1. アプリケーション概要

Picto Islandは、「あつまれ どうぶつの森」の島づくりをモチーフにした、Instagram風の交流型Webアプリケーションです。

ユーザーはアカウントを作成して、自分の島や家を設定したり、画像を投稿したりできます。また、ユーザー検索、フォロー、プロフィール編集、グループ島の作成、グループ美術館での画像共有などを行えます。

> 本アプリケーションは学習・ポートフォリオ目的で制作した非公式作品です。任天堂株式会社および「あつまれ どうぶつの森」との公式な関係はありません。

## 2. 使用技術・開発環境

| 項目 | バージョン・環境 |
|---|---|
| OS | Windows |
| エディタ | Visual Studio Code |
| Python | 3.13.5 |
| Flask | 3.1.0 |
| MySQL Server | 9.3.0 |
| DB接続 | mysql-connector-python |
| パスワード管理 | Werkzeug |
| SQL管理ツール | A5:SQL Mk-2 |
| フロントエンド | HTML / CSS |

## 3. 主な機能

- アカウント登録・ログイン
- 自分または他のユーザーの島の表示
- 島画像の変更
- 画像の新規投稿
- 家画像の登録・変更
- 美術館での投稿画像表示
- ユーザー名による検索
- ユーザーのフォロー・解除
- プロフィールの表示・編集
- グループ島の作成・表示
- グループメンバーの追加・退会
- グループ美術館への画像投稿・閲覧

## 4. フォルダ構成

```text
pictoisland/
├── ソース/
│   ├── HEW.py
│   ├── templates/
│   │   ├── group.html
│   │   ├── group_create.html
│   │   ├── group_island.html
│   │   ├── group_museum.html
│   │   ├── home.html
│   │   ├── house.html
│   │   ├── index.html
│   │   ├── museum.html
│   │   ├── newpost.html
│   │   ├── prof.html
│   │   ├── prof_edit.html
│   │   ├── search.html
│   │   └── signup.html
│   └── static/
│       ├── css/
│       ├── images/
│       ├── islands/
│       │   ├── Island1.png
│       │   ├── island2.png
│       │   └── island3.png
│       └── uploads/
├── database/
│   ├── schema.sql
│   └── sample_data.sql
├── requirements.txt
└── README.md
```

## 5. セットアップ手順

### 5-1. 必要なソフトウェア

以下を事前にインストールしてください。

- Python 3.13.5
- MySQL Server 9.3.0
- Git
- Visual Studio Code

A5:SQL Mk-2は任意です。SQLファイルはMySQLのコマンドでも実行できます。

### 5-2. ソースコードの取得

GitHubからリポジトリをクローンします。

```bash
git clone <GitHubリポジトリのURL>
cd pictoisland
```

Gitを使用しない場合は、GitHubの「Code」から「Download ZIP」を選択し、ZIPファイルを展開してください。

### 5-3. 仮想環境の作成

プロジェクト直下で次のコマンドを実行します。

```bash
python -m venv .venv
```

Windows PowerShellの場合：

```powershell
.venv\Scripts\Activate.ps1
```

Windows コマンドプロンプトの場合：

```bat
.venv\Scripts\activate.bat
```

ターミナルの先頭に `(.venv)` と表示されれば、仮想環境は有効です。

PowerShellでスクリプトの実行を拒否された場合は、同じターミナルで以下を実行してから、もう一度有効化してください。

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

### 5-4. Pythonライブラリのインストール

仮想環境を有効にした状態で実行します。

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

`requirements.txt` の内容例：

```text
Flask==3.1.0
mysql-connector-python
```

### 5-5. データベース接続情報の設定

`ソース/HEW.py` の `get_db()` を開き、次の2か所を実行環境に合わせて変更します。

```python
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="your database username",
        password="your database password",
        database="pictoisland"
    )
```

- `your database username`：MySQLのユーザー名に変更します。
- `your database password`：そのMySQLユーザーのパスワードに変更します。

例：MySQLユーザー名が `root` の場合

```python
user="root"
```

実際のパスワードをGitHubへコミットしないでください。接続確認後、提出時は上記のプレースホルダーへ戻してください。

### 5-6. データベースとテーブルの作成

プロジェクト直下で以下を実行します。

```bash
mysql -u <MySQLユーザー名> -p < database/schema.sql
```

例：ユーザー名が `root` の場合

```bash
mysql -u root -p < database/schema.sql
```

パスワードを求められたら、MySQLのパスワードを入力します。この処理により、`pictoisland` データベースと以下の6テーブルが作成されます。

- `accountdata`
- `posts`
- `follows`
- `usergroups`
- `group_members`
- `group_posts`

### 5-7. サンプルデータの登録

プロジェクト直下で以下を実行します。

```bash
mysql -u <MySQLユーザー名> -p pictoisland < database/sample_data.sql
```

例：

```bash
mysql -u root -p pictoisland < database/sample_data.sql
```

サンプルSQLは、デモアカウント3件、通常投稿6件、相互フォロー、グループ1件、グループ投稿3件を登録します。

### 5-8. アプリケーションの起動

`HEW.py` のあるフォルダへ移動します。

```bash
cd ソース
```

アプリケーションを起動します。

```bash
python HEW.py
```

正常に起動すると、ターミナルにアクセス先が表示されます。

```text
http://127.0.0.1:5000/
```

WebブラウザでこのURLを開いてください。

## 6. デモアカウント

`sample_data.sql` を実行すると、以下のアカウントを利用できます。

| ユーザー名 | メールアドレス | パスワード |
|---|---|---|
| `island_user1` | `island1@example.com` | `sample1234` |
| `island_user2` | `island2@example.com` | `sample1234` |
| `island_user3` | `island3@example.com` | `sample1234` |

ログイン画面では、メールアドレスとパスワードを入力してください。

## 7. 動作確認

以下の順番で確認してください。

1. `island1@example.com` と `sample1234` でログインできる
2. ホーム画面に島が表示される
3. 島の画像を変更して保存できる
4. 新しい画像を投稿できる
5. 投稿画像を美術館で確認できる
6. `island_user2` などを検索できる
7. 他のユーザーをフォロー・解除できる
8. プロフィールを編集できる
9. グループ島とグループ美術館を表示できる
10. グループ美術館へ画像とコメントを投稿できる

## 8. データベース構成

### `accountdata`

ユーザー名、メールアドレス、パスワードハッシュ、公開設定、自己紹介、島名、島テーマ、家画像、島画像、アイコンを管理します。

### `posts`

ユーザーが投稿した画像と投稿日時を管理します。

### `follows`

フォローするユーザーとフォローされるユーザーの組み合わせを管理します。

### `usergroups`

グループ名、グループ島の画像、作成者を管理します。

### `group_members`

各グループに所属するユーザーを管理します。

### `group_posts`

グループ美術館へ投稿された画像、コメント、投稿者、投稿日時を管理します。

## 9. アプリケーションの終了

アプリケーションを実行しているターミナルで、次のキーを押します。

```text
Ctrl + C
```

仮想環境を終了する場合：

```bash
deactivate
```

## 10. トラブルシューティング

### `ModuleNotFoundError: No module named 'flask'`

仮想環境を有効にし、ライブラリを再度インストールしてください。

```bash
python -m pip install -r requirements.txt
```

### `ModuleNotFoundError: No module named 'mysql'`

以下を実行してください。

```bash
python -m pip install mysql-connector-python
```

### `Access denied for user` と表示される

`HEW.py` の `user` と `password` が、ご自身のMySQLのユーザー名・パスワードと一致しているか確認してください。

### `Unknown database 'pictoisland'`

`schema.sql` を実行してください。

```bash
mysql -u <MySQLユーザー名> -p < database/schema.sql
```

### `Table doesn't exist` と表示される

`pictoisland` データベースに6テーブルが作成されているか確認してください。

```sql
USE pictoisland;
SHOW TABLES;
```

### 画像が表示されない

以下を確認してください。

- `ソース/static/islands` に `Island1.png`、`island2.png`、`island3.png` がある
- `ソース/static/uploads` にサンプルSQLが参照する画像がある
- ファイル名の大文字・小文字と拡張子が一致している
- GitHubへ画像ファイルが登録されている

## 11. 注意事項

- MySQLの実際のユーザー名・パスワードを公開リポジトリへ登録しないでください。
- `app.secret_key` は開発用の固定値ではなく、提出後に環境変数で設定する方式が望まれます。
- Flaskのデバッグモードは開発時だけ使用してください。
- サンプルアカウントとパスワードは動作確認専用です。
- 使用する画像について、公開・再配布が認められていることを確認してください。

## 12. 権利表記

本アプリケーションは、ポートフォリオおよび学習成果の確認を目的として公開しています。

「あつまれ どうぶつの森」および関連する名称・画像・キャラクター等の権利は、それぞれの権利者に帰属します。本アプリケーションは任天堂株式会社の公式サービスではありません。
