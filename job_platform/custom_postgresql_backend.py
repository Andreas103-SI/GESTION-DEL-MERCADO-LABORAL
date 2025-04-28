# job_platform/custom_postgresql_backend.py
from django.db.backends.postgresql.creation import DatabaseCreation

class CustomDatabaseCreation(DatabaseCreation):
    def _create_test_db(self, verbosity, autoclobber, keepdb=False):
        # Crear la base de datos de prueba
        super()._create_test_db(verbosity, autoclobber, keepdb)
        # Habilitar la extensión citext
        with self.connection.cursor() as cursor:
            cursor.execute("CREATE EXTENSION IF NOT EXISTS citext;")