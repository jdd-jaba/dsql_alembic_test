import boto3
from sqlalchemy import create_engine, event
from sqlalchemy.engine import URL

ADMIN = "admin"
NON_ADMIN_SCHEMA = "myschema"

dsql_token="REPLACE"

def create_dsql_engine():
    print("Starting to create DSQL Engine")
    
    cluster_user = "admin"
    cluster_endpoint = "riabuiqk5vhhxcaov3ljrdc3qq.dsql.ap-northeast-1.on.aws"
    region = "ap-northeast-1"
    driver = "psycopg2"

    client = boto3.client("dsql", region_name=region)

    # Create the URL, note that the password token is added when connections are created
    url = URL.create(
        f"postgresql+{driver}",
        username=cluster_user,
        host=cluster_endpoint,
        database="postgres",
    )

    connect_args = {
        "sslmode": "verify-full",
        "sslrootcert": "./root.pem",
    }

    if driver == "psycopg2":
        import psycopg2.extensions

        libpq_version = psycopg2.extensions.libpq_version()

    elif driver == "psycopg":
        import psycopg

        libpq_version = psycopg.pq.version()

    # Use the more efficient connection method if it's supported.
    if libpq_version >= 170000:
        connect_args["sslnegotiation"] = "direct"
    # Create the engine
    engine = create_engine(url, connect_args=connect_args, pool_size=5, max_overflow=10)

    # Adds a listener that creates a new token every time a new connection is created
    # in the SQLAlchemy engine
    @event.listens_for(engine, "do_connect")
    def add_token_to_params(dialect, conn_rec, cargs, cparams):
        # Generate a fresh token for this connection
        fresh_token = generate_token(client, cluster_user, cluster_endpoint, region)
        # Update the password in connection parameters
        cparams["password"] = fresh_token

    # If we are using the non-admin user, we need to set the search path to use
    # 'myschema' instead of public whenever a connection is created.
    @event.listens_for(engine, "connect", insert=True)
    def set_search_path(dbapi_connection, connection_record):
        print("Successfully opened connection")
        if cluster_user == ADMIN:
            return
        existing_autocommit = dbapi_connection.autocommit
        dbapi_connection.autocommit = True
        cursor = dbapi_connection.cursor()
        cursor.execute("SET SESSION search_path='%s'" % NON_ADMIN_SCHEMA)
        cursor.close()
        dbapi_connection.autocommit = existing_autocommit

    return engine

def generate_token(client, cluster_user, cluster_endpoint, region):
    if cluster_user == ADMIN:
        return client.generate_db_connect_admin_auth_token(cluster_endpoint, region)
    else:
        return client.generate_db_connect_auth_token(cluster_endpoint, region)
