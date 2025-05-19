
## Consultar historico de migrações

```sh
alembic history

33c92c97baaa -> 7b3c387d3462 (head), create todos table
2d96d9e3b128 -> 33c92c97baaa, add updated_at field in users table
<base> -> 2d96d9e3b128, create users table
```

## Retornar o banco em uma versão especifica

```sh
alembic downgrade 2d96d9e3b128
or
alembic downgrade -1
```

## Executando uma migração

```sh
alembic revision --autogenerate -m "create todos table"  # Gera um arquivo de migração com base nas mudanças detectadas nos modelos

alembic upgrade head  # Aplica a migração mais recente ao banco de dados (leva até a última versão)
```

## Autenticação

Username + Password(123456)
