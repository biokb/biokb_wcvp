import os

import click
from sqlalchemy import create_engine

from biokb_wcvp import __version__
from biokb_wcvp.api.main import run_api
from biokb_wcvp.constants import NEO4J_USER, PROJECT_NAME
from biokb_wcvp.db.manager import DbManager
from biokb_wcvp.rdf.neo4j_importer import Neo4jImporter
from biokb_wcvp.rdf.turtle import TurtleCreator


@click.group()
@click.version_option(__version__)
def main():
    """Import in RDBMS, create turtle files and import into Neo4J.

    Please follow the steps:\n
    1. Import data using `import-data` command.\n
    2. Create TTL files using `create-ttls` command.\n
    3. Import TTL files into Neo4j using `import-neo4j` command.\n
    """
    pass


@main.command("import-data")
@click.option(
    "-f",
    "--force-download",
    is_flag=True,
    type=bool,
    default=False,
    help="Force re-download of the source file [default: False]",
)
@click.option(
    "-k",
    "--keep-files",
    is_flag=True,
    type=bool,
    default=False,
    help="Keep downloaded source files after import [default: False]",
)
@click.option(
    "-c",
    "--connection-string",
    type=str,
    default=f"sqlite:///{PROJECT_NAME}.db",
    help=f"SQLAlchemy engine URL [default: sqlite:///{PROJECT_NAME}.db]",
)
def import_data(force_download: bool, connection_string: str):
    """Import data."""
    engine = create_engine(connection_string)
    DbManager(engine=engine).import_data(force_download=force_download)
    click.echo(f"Data imported successfully to {connection_string}")


@main.command("create-ttls")
@click.option(
    "-c",
    "--connection-string",
    type=str,
    default=f"sqlite:///{PROJECT_NAME}.db",
    help=f"SQLAlchemy engine URL [default: sqlite:///{PROJECT_NAME}.db]",
)
def create_ttls(connection_string: str):
    """Create TTL files from local database."""
    path_to_zip = TurtleCreator(create_engine(connection_string)).create_ttls()
    click.echo(
        f"Path to the zip file containing all generated Turtle files. {path_to_zip}"
    )


@main.command("import-neo4j")
@click.option("--uri", "-i", default="bolt://localhost:7687", help="Neo4j database URI")
@click.option("--user", "-u", default=NEO4J_USER, help="Neo4j username")
@click.option("--password", "-p", required=True, help="Neo4j password")
def import_neo4j(uri: str, user: str, password: str):
    """Import TTL files into Neo4j database."""
    Neo4jImporter(neo4j_uri=uri, neo4j_user=user, neo4j_pwd=password).import_ttls()


@main.command("run-server")
@click.option(
    "--host", "-h", default="0.0.0.0", help="API server host [default: 0.0.0.0]"
)
@click.option("--port", "-P", default=8000, help="API server port [default: 8000]")
@click.option("--user", "-u", default="admin", help="API username [default=admin]")
@click.option("--password", "-p", default="admin", help="API password [default: admin]")
def run_server(
    host: str,
    port: int,
    user: str,
    password: str,
) -> None:
    """Run the API server.

    Args:
        host (str): API server host
        port (int): API server port
        user (str): API username
        password (str): API password
    """
    # set env variables for API authentication
    os.environ["API_USER"] = user
    os.environ["API_PASSWORD"] = password
    host_shown = "127.0.0.1" if host == "0.0.0.0" else host
    click.echo(f"API server running at http://{host_shown}:{port}/docs#/")
    run_api(host=host, port=port)


if __name__ == "__main__":
    main()
