"""Peewee migrations -- 001_USER.py.

Some examples (model - class or model name)::

    > Model = migrator.orm['model_name']            # Return model in current state by name

    > migrator.sql(sql)                             # Run custom SQL
    > migrator.python(func, *args, **kwargs)        # Run python code
    > migrator.create_model(Model)                  # Create a model (could be used as decorator)
    > migrator.remove_model(model, cascade=True)    # Remove a model
    > migrator.add_fields(model, **fields)          # Add fields to a model
    > migrator.change_fields(model, **fields)       # Change fields
    > migrator.remove_fields(model, *field_names, cascade=True)
    > migrator.rename_field(model, old_field_name, new_field_name)
    > migrator.rename_table(model, new_table_name)
    > migrator.add_index(model, *col_names, unique=False)
    > migrator.drop_index(model, *col_names)
    > migrator.add_not_null(model, *field_names)
    > migrator.drop_not_null(model, *field_names)
    > migrator.add_default(model, field_name, default)

"""

from peewee import SQL, Model, AutoField, DateTimeField, TextField, BooleanField


def migrate(migrator, database, fake=False, **kwargs):
    @migrator.create_model
    class UserInDB(Model):
        id = AutoField()
        created = DateTimeField(constraints=[SQL('DEFAULT now()')])
        username = TextField(null=False)
        email = TextField(null=True)
        full_name = TextField(null=True)
        role = TextField(null=True, default='restricted_user')
        disabled = BooleanField(default=False)
        hashed_password = TextField(null=False)

        class Meta:
            table_name = 'users'

    migrator.sql(
        "INSERT INTO users(username, full_name, role, disabled, hashed_password) VALUES ('admin', 'admin', 'admin', False, '$2b$12$dnFQuYI6QL/xiR5p1/hKOu30jsAtMqVmxi8gNJTKL6wYmcZK74ELG')"
    )


def rollback(migrator, database, fake=False, **kwargs):
    migrator.remove_model('users')
