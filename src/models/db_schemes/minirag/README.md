## Run Alembic Migrations

### Configurations

```bash
cp alembic.ini alembic.ini.example 
```

- Update the `alembic.ini` with your database credentials (`sqlalchemy.ur`)

### (Optional) Create a new migration

```bash
alembic revision --autogenerate -m "Add ..."
```

### Upgrade the database

```bash
alembic upgrade head
```