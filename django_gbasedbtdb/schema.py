from django.db.backends.base.schema import BaseDatabaseSchemaEditor
from django.db.utils import ProgrammingError, DatabaseError


class DatabaseSchemaEditor(BaseDatabaseSchemaEditor):

    sql_rename_table = "RENAME TABLE %(old_table)s TO %(new_table)s"
    sql_rename_column = (
        "RENAME COLUMN %(table)s.%(old_column)s TO %(new_column)s"
    )
    sql_create_unique = "ALTER TABLE %(table)s ADD CONSTRAINT UNIQUE (%(columns)s) CONSTRAINT %(name)s "
    sql_create_fk = (
        "ALTER TABLE %(table)s ADD CONSTRAINT FOREIGN KEY (%(column)s) "
        "REFERENCES %(to_table)s (%(to_column)s) ON DELETE CASCADE CONSTRAINT  %(name)s"
    )
    sql_create_pk = (
        "ALTER TABLE %(table)s ADD CONSTRAINT PRIMARY KEY (%(columns)s) CONSTRAINT %(name)s"
    )
    sql_create_column = "ALTER TABLE %(table)s ADD %(column)s %(definition)s"
    sql_alter_column_null = "MODIFY %(column)s %(type)s NULL"
    sql_alter_column_not_null = "MODIFY %(column)s %(type)s NOT NULL"
    sql_alter_column_type = "MODIFY %(column)s %(type)s"
    sql_alter_column_default = "MODIFY %(column)s DEFAULT "
    sql_alter_column_no_default = "MODIFY %(column)s DROP DEFAULT"
    sql_delete_column = "ALTER TABLE %(table)s DROP %(column)s"
    sql_rename_index = "RENAME INDEX %(old_name)s TO %(new_name)s"

    def execute(self, sql, params=[]):
        """
        GBase 8s adds an index to foreign keys automatically

        This silences the error when Django tries to do the same thing independently
        """
        try:
            if "CREATE TABLE" in str(sql) or "ALTER TABLE" in str(sql) :
                sql = str(sql).replace('varchar(None)','varchar(255)')
            super(DatabaseSchemaEditor, self).execute(sql, params)
        except (ProgrammingError, DatabaseError) as e:
            if "CREATE INDEX" not in str(sql) and 'Index already exists' not in str(e):
                # ugh, that feels dirty
                raise e

    def skip_default(self, field):
        """
        It's not easy to handle defaults easily for gbasedbt because of its weird syntax
        An example for this is to add default for some datetime field:

        ALTER TABLE django_admin_log MODIFY ( action_time datetime year to fraction(5)
        NOT NULL DEFAULT DATETIME(2016-05-25 00:26:23.00000) year to fraction(5));
        """
        return True
