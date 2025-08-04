# Aurora DSQL + Alembic テストレポジトリ

このレポジトリは、Aurora DSQL またはローカル PostgreSQL と Alembic マイグレーションをテストするために作成されております。

## セットアップ手順

### 1. 環境構築

```bash
# ローカルでPostgreSQLを起動
docker-compose up -d

# 仮想環境の設定
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. データベースマイグレーション

#### ローカル環境でのマイグレーション

```bash
cd aurora
```

##### ローカル DB に対してマイグレーション

```bash
DB=postgres alembic revision --autogenerate -m "<migration-name>"
DB=postgres alembic upgrade head
```

##### AuroraDSQL に対してマイグレーション

```bash
AWS_PROFILE=aws-kidsroom DB=aurora alembic upgrade head
```

### 3. アプリケーション(DB の CRUD)の実行

```bash
DB=aurora|postgres python3 main.py
```

##### 実際に migrate を行う raw sql を確認したい場合：

```あと
alembic upgrade head --sql
```

## 使用方法

1. まずローカル環境でマイグレーションを作成・テストする
2. 問題がなければ、同じマイグレーションファイルを Aurora DSQL 環境にコピーして適用する
3. 両環境で同じスキーマ変更が正常に動作することを確認する
