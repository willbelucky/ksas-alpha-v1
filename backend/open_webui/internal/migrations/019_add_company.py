"""Peewee migrations -- 019_add_company.py."""

from contextlib import suppress

import peewee as pw
from peewee_migrate import Migrator


with suppress(ImportError):
    import playhouse.postgres_ext as pw_pext


def migrate(migrator: Migrator, database: pw.Database, *, fake=False):
    """Write your migrations here."""

    @migrator.create_model
    class Company(pw.Model):
        id = pw.TextField(unique=True)
        name = pw.TextField(unique=True)
        nicknames = pw.TextField(null=True)  # JSON 데이터를 저장하기 위해 TextField 사용
        description = pw.TextField()
        created_at = pw.BigIntegerField(null=False)
        updated_at = pw.BigIntegerField(null=False)

        class Meta:
            table_name = "company"


def rollback(migrator: Migrator, database: pw.Database, *, fake=False):
    """Write your rollback migrations here."""

    migrator.remove_model("company")