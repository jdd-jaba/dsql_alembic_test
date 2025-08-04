import os
from sqlalchemy import create_engine

def database_url():
    return "postgresql://%s:%s@%s:%s/%s" % (
        os.getenv("POSTGRES_USER", "postgres"),
        os.getenv("POSTGRES_PASSWORD", "password"),
        os.getenv("POSTGRES_HOST", "localhost"),
        os.getenv("POSTGRES_PORT", "5432"),
        os.getenv("POSTGRES_DB", "postgres")
    )
  
def create_postgres_engine():
    url = database_url()
    
    engine = create_engine(url, pool_size=5, max_overflow=10)
    
    return engine