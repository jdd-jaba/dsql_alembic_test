import boto3
from sqlalchemy import create_engine, event
from sqlalchemy.engine import URL

ADMIN = "admin"
NON_ADMIN_SCHEMA = "myschema"

dsql_token="riabuiqk5vhhxcaov3ljrdc3qq.dsql.ap-northeast-1.on.aws/?Action=DbConnectAdmin&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=ASIAQPOP4CKLU3FY4J74%2F20250731%2Fap-northeast-1%2Fdsql%2Faws4_request&X-Amz-Date=20250731T061201Z&X-Amz-Expires=900&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEKb%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaDmFwLW5vcnRoZWFzdC0xIkgwRgIhALaJQctrLwaYXkeJgfDNdPzUBKqMwpYDWrQsWaQB%2BgQdAiEAgx4nhukE4%2F32Cevsxf5v%2Fxwv3y2JZ4R7XXx%2F8HZj7FEq4QMIz%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARADGgwwMzMxODUwNzU4NjMiDNj4wRBrF5h4LdCc0yq1Ay11WoTWpSb%2BmdPkooaRTeaOHFLNxgBD61IhzxKK5FwujpurRnoebJWlRGtC%2BO5gGsOoX3sJqsI%2BoNxyypyBcbBIz6ohGKU6KaVKeEOATZ%2BzuIYXuupc1cPbZMl%2BQThm2NAl6nWUsGs7sDEWcYBjvCgqSgG9JI2pHAzudUw9CFsT3D6LglosBgpA3FINa%2B6xtniVfq3r4ItirwyFev%2FmYHfx4%2B4Dw68SCY4YyZIDRRvHvFjjQc%2FCEz07liJuQG8V7CZeuauZhPmSUKgWa86OTWJ5OwHLdmlRAAZWod0Dtt3oxGW9Sm6CFdPpqfY28yKiZrLhgAaroXw8aouvhn2RaGhYJB9BRwAxeuGCrLNKsJf84Z1ql%2FsTpPD2rhD8L8vRlhDzxuuR1x4yua%2B7Rwn7OvuJYjAIh%2F9VBYTbplkUn1jdAnZpqXCfU09Nd3Se3FaIISlFeTwWcOrBmXS7iynyohvwcPpGfJOx2NC6h8bSCit7GSjzkMKv2%2BO7RlNOuc8Lo0jkNztFBVEnuXaF3TqKFfbXBqaqvYAfRtQBxCWc91ntJk1E7Evqs6A0Mz3FXMZINB%2F8WaIlMNzaq8QGOuwBauPbiQEVUSt9wc1TYSl%2F%2FUwafyIVfjfVSC2DnXnuDANWGxL3%2B9IpMnE%2FRHmzy%2Fk8%2FMP6FuGWyDC4rA%2FKQUh%2B6U%2BUGJ3srM4TIWflrkEaflu%2FUGO6%2F9rE6D3r1P9JzJZD6xyJbuFEcg0f7vrsczxvwwit6tdag5BF1iMH28OK6%2FN1h%2BTxoMJ1j59782qcGx6z8v3kdPH%2F%2FtSDH52vUdVjFkV%2FMdLW2MdSOXKoctOBs0eVUQH8nU27D4GuTAjYwVAkas%2Bq0Wa%2FZJD0GOU6EB5XiqBwcWhZpe4jamCmdYJyVrZG8FeP6F86l3GAz24%3D&X-Amz-Signature=71b4d597fc79b336d4ff0e4d4c227c18cc3a2bb21ae064744dedb8154903286f&X-Amz-SignedHeaders=host"

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
    
    print("engine-url", engine.url)

    # Adds a listener that creates a new token every time a new connection is created
    # in the SQLAlchemy engine
    @event.listens_for(engine, "do_connect")
    def add_token_to_params(dialect, conn_rec, cargs, cparams):
        print("client:", client)
        print("cluster_user:", cluster_user)
        # Generate a fresh token for this connection
        fresh_token = generate_token(client, cluster_user, cluster_endpoint, region)
        print("fresh_token:", fresh_token)
        # Update the password in connection parameters
        cparams["password"] = dsql_token

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
