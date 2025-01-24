from configparser import ConfigParser
import psycopg2
import pandas as pd
import zipfile
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os

class DBClient:

    def __init__(self):
        
        os.system("service postgresql start")
        os.system(
            """
            sudo -i -u postgres psql -c "CREATE USER app_user WITH PASSWORD 'app_pass' SUPERUSER;"
            """
        )

        os.system('sed -i "s/peer/md5/g" /etc/postgresql/16/main/pg_hba.conf')
        os.system("service postgresql restart")

    def create_database_from_archive(self, db_name, db_archive_path, restore_directory):

        print("Creating database from archive")

        print("Unzipping...")
        # Start by unzipping the file
        with zipfile.ZipFile(db_archive_path) as zip_ref:
            zip_ref.extractall(restore_directory + "/")

        print("Creating the database...")
        self.connect("app_user", "app_pass", "postgres", autocommit=True)

        print("Checking for existing database...")
        self.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
        if len(self.cursor.fetchall()) > 0:
            print("Database already exists, dropping")
            self.execute(f"DROP DATABASE {db_name}")

        self.execute(f"CREATE DATABASE {db_name}")
        self.close()

        print("Restoring the database")
        restore_command = "PGPASSWORD=app_pass pg_restore -U app_user -d {} --no-owner -w {}".format(
            db_name,
            f"{restore_directory}/{db_name}"
        )
        print("Restore command: {}".format(restore_command))

        os.system(restore_command)

        print("Database restore complete")

    def connect(self, user, password, database, autocommit=False):

        self.connection = psycopg2.connect(
            user=user,
            password=password,
            database=database
        )

        if autocommit:
            self.connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        self.cursor = self.connection.cursor()

    def execute(self, command):
        self.cursor.execute(command)

    def query(self, query):

        self.cursor.execute(query)
        raw_results = self.cursor.fetchall()

        column_names = [desc[0] for desc in self.cursor.description]

        dataset = pd.DataFrame(raw_results)
        dataset.columns = column_names

        return dataset

    def close(self):

        self.cursor.close()
        self.connection.close()