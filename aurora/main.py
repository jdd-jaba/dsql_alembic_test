import logging
import sys
import os
from datetime import datetime
import subprocess
import time
from sqlalchemy.orm import sessionmaker

# Add current directory to sys.path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'alembic'))
from db_aurora import create_dsql_engine
from db_postgres import create_postgres_engine
from models.job_ocr import JobOcr

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def get_database_engine():
    """Get database engine based on environment variable"""
    db_type = os.getenv("DB", "postgres")
    if db_type == "postgres":
        return create_postgres_engine()
    elif db_type == "aurora":
        return create_dsql_engine()
    else:
        raise ValueError(f"Unsupported DB type: {db_type}")

def insert_dummy_data(session):
    """Insert dummy data using SQLAlchemy ORM"""
    logger.info("Inserting dummy data using SQLAlchemy...")
    
    dummy_records = [
        JobOcr(
            job_id='job123',
            pdf_id='pdf456', 
            ocr_id='ocr789',
            ocr_result='dummy result from SQLAlchemy',
            pdf_page_num=1,
            image_file_path='/path/to/image/file.png',
            created_at=datetime.now()
        ),
        JobOcr(
            job_id='job456',
            pdf_id='pdf789', 
            ocr_id='ocr123',
            ocr_result='another dummy result',
            pdf_page_num=2,
            image_file_path='/path/to/another/image.png',
            created_at=datetime.now()
        )
    ]
    
    for record in dummy_records:
        session.merge(record)
    session.commit()
    logger.info(f"Inserted {len(dummy_records)} dummy records")


def update_data(session):
    """Update data using SQLAlchemy ORM"""
    logger.info("Updating ocr_result using SQLAlchemy...")
    record = session.query(JobOcr).filter_by(job_id='job123', pdf_id='pdf456', ocr_id='ocr789').first()
    if record:
        record.ocr_result = 'updated result from SQLAlchemy'
        session.commit()
        logger.info("Record updated successfully")
        return True
    else:
        logger.info("No record found to update")
        return False

def delete_data(session):
    """Delete data using SQLAlchemy ORM"""
    logger.info("Deleting test data using SQLAlchemy...")
    records_to_delete = session.query(JobOcr).filter_by(job_id='job123', pdf_id='pdf456', ocr_id='ocr789').all()
    if records_to_delete:
        for record in records_to_delete:
            session.delete(record)
        session.commit()
        logger.info(f"Deleted {len(records_to_delete)} record(s) successfully")
        return len(records_to_delete)
    else:
        logger.info("No records found to delete")
        return 0

def select_and_log_all(session, label="job_ocr テーブルの全データ (SQLAlchemy)"):
    """Query and log all data using SQLAlchemy ORM"""
    logger.info(label)
    records = session.query(JobOcr).all()
    logger.info(f"Found {len(records)} records:")
    for record in records:
        logger.info(f"  JobOcr(job_id='{record.job_id}', pdf_id='{record.pdf_id}', ocr_id='{record.ocr_id}', "
                   f"ocr_result='{record.ocr_result}', pdf_page_num={record.pdf_page_num}, "
                   f"image_file_path='{record.image_file_path}', created_at={record.created_at})")

def select_and_log_all(cursor, label="job_ocr テーブルの全データ (Raw SQL)"):
    """Query and log all data using raw SQL"""
    logger.info(label)
    cursor.execute("SELECT * FROM job_ocr")
    rows = cursor.fetchall()
    logger.info(f"Found {len(rows)} records:")
    for row in rows:
        logger.info(f"  {row}")
        
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

def test_database_operations():
    """Test all database operations with SQLAlchemy ORM"""
    try:
        # Get database engine
        engine = get_database_engine()
        Session = sessionmaker(bind=engine)
        
        logger.info("=== Testing SQLAlchemy ORM CRUD operations ===")
        with Session() as session:
            # 1. INSERT - Insert dummy data
            # logger.info("1. INSERT Operation:")
            # insert_dummy_data(session)
            
            # 2. SELECT - Display all data
            # logger.info("2. SELECT Operation (after insert):")
            # select_and_log_all(session)
            
            # 3. UPDATE - Update data
            # logger.info("3. UPDATE Operation:")
            # update_data(session)
            
            # SELECT again to show updated data
            # logger.info("4. SELECT Operation (after update):")
            # select_and_log_all(session, "Updated data verification")
            
            # 5. DELETE - Delete data
            # logger.info("5. DELETE Operation:")
            # delete_data(session)
            
            # SELECT again to show deleted data
            # logger.info("6. SELECT Operation (after delete):")
            # select_and_log_all(session, "After deletion verification")
            
        logger.info("All database operations completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Database operations failed: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def main():
    """
    データベースCRUD操作のテスト
    """
    start_time = datetime.now()
    logger.info(f"バッチジョブ開始: {start_time.isoformat()}")
    
    db_type = os.getenv("DB", "postgres")
    logger.info(f"Using database type: {db_type}")

    try:
        # Run migrations if needed
        if os.getenv("NEED_MIGRATION") == "true":
            migrate_db()
        
        # Test all database operations
        success = test_database_operations()

        end_time = datetime.now()
        duration = end_time - start_time
        
        if success:
            logger.info(f"バッチジョブ正常終了: {end_time.isoformat()}")
        else:
            logger.error(f"バッチジョブでエラー終了: {end_time.isoformat()}")
            
        logger.info(f"実行時間: {duration.total_seconds():.2f}秒")
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        logger.warning("バッチジョブが中断されました")
        return 1
    except Exception as e:
        logger.error(f"バッチジョブでエラーが発生しました: {str(e)}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)