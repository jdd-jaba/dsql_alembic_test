import logging
import sys
from datetime import datetime
import subprocess
import time

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def insert_dummy_data(cursor):
    logger.info("Inserting dummy data...")
    cursor.execute("""
        INSERT INTO job_ocr (job_id, pdf_id, ocr_id, ocr_result, pdf_page_num, image_file_path, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        'job123', 'pdf456', 'ocr789', 'dummy result', 1,
        '/path/to/image/file.png', datetime.now()
    ))


def update_data(cursor):
    logger.info("Updating ocr_result...")
    cursor.execute("""
        UPDATE job_ocr
        SET ocr_result = %s
        WHERE job_id = %s AND pdf_id = %s AND ocr_id = %s
    """, ('updated result', 'job123', 'pdf456', 'ocr789'))


def delete_data(cursor):
    logger.info("Deleting test data...")
    cursor.execute("""
        DELETE FROM job_ocr
        WHERE job_id = %s AND pdf_id = %s AND ocr_id = %s
    """, ('job123', 'pdf456', 'ocr789'))


def select_and_log_all(cursor, label="job_ocr テーブルの全データ"):
    logger.info(label)
    cursor.execute("SELECT * FROM job_ocr")
    for row in cursor.fetchall():
        logger.info(row)
        
def migrate_db():
    logger.info("データベースのマイグレーションを実行します")
    # subprocess.run([
    #     "alembic", "revision", "--autogenerate", "-m", "initial migration"
    # ], check=True)

    subprocess.run(
        "alembic upgrade head",
        shell=True,
        check=True
    )

def main():
    """
    テスト用バッチジョブ
    30秒間待機して終了する
    """
    start_time = datetime.now()
    logger.info(f"バッチジョブ開始: {start_time.isoformat()}")
    
    logger.info("5秒間待機中...")
    # 30秒間の待機
    time.sleep(5)

    try:
        # if os.getenv("NEED_MIGRATION") == "true":
        migrate_db()

        logger.info(f"db connect")
        
        # conn = psycopg2.connect(
        #     host=os.getenv("POSTGRES_HOST", "aurorapostgres"),
        #     port=os.getenv("POSTGRES_PORT", 5432),
        #     database=os.getenv("POSTGRES_DB", "postgres"),
        #     user=os.getenv("POSTGRES_USER", "postgres"),
        #     password=os.getenv("POSTGRES_PASSWORD", "password")
        # )
        
        # cur = conn.cursor()
        
        # insert_dummy_data(cur)
        # conn.commit()
        # select_and_log_all(cur)
        
        # update_data(cur)
        # conn.commit()
        # select_and_log_all(cur)
        
        # delete_data(cur)
        # conn.commit()
        # select_and_log_all(cur)

        end_time = datetime.now()
        duration = end_time - start_time
        logger.info(f"バッチジョブ正常終了: {end_time.isoformat()}")
        logger.info(f"実行時間: {duration.total_seconds():.2f}秒")
        
        return 0
        
    except KeyboardInterrupt:
        logger.warning("バッチジョブが中断されました")
        return 1
    except Exception as e:
        logger.error(f"バッチジョブでエラーが発生しました: {str(e)}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)