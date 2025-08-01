# Aurora DSQL + Alembic テストレポジトリ

このレポジトリは、Aurora DSQL と Alembic マイグレーションをテストするために作成されており、以下の 2 つのディレクトリで構成されています：

1. **aurora/** - Aurora DSQL に対する Alembic マイグレーションのテスト
2. **local/** - ローカル PostgreSQL データベースに対する Alembic マイグレーションのテスト

## セットアップ手順

### 前提条件

- Python 3.x
- Docker（ローカルテスト用）
- AWS 認証情報の設定（Aurora DSQL 用）

### 1. 環境構築

```bash
# ローカルでPostgreSQLを起動
cd local
docker-compose up -d

# 仮想環境の設定
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. アプリケーションの実行

```bash
# auroraディレクトリでの実行
cd aurora
python3 main.py

# localディレクトリでの実行
cd ../local
python3 main.py
```

### 3. データベースマイグレーション

#### ローカル環境でのマイグレーション

```bash
cd local

# マイグレーションファイルを作成。local/alembic/versionsにファイルが作成されます。
alembic revision --autogenerate -m "initial migration"

# 作成されたマイグレーションファイルを実際のデータベースに適用
alembic upgrade head
```

#### Aurora DSQL でのマイグレーション

```bash
cd aurora

# localで作成したマイグレーションファイルをaurora/alembic/versionsにコピー

# マイグレーションファイルを実際のデータベースに適用
alembic upgrade head
```

## 使用方法

1. まずローカル環境でマイグレーションを作成・テストする
2. 問題がなければ、同じマイグレーションファイルを Aurora DSQL 環境にコピーして適用する
3. 両環境で同じスキーマ変更が正常に動作することを確認する
