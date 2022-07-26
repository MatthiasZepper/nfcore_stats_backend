# Database

## Formerly: QuestDB

Initially, [QuestDB](https://questdb.io) was chosen, a specialized, performant database for time-series data. The [demo instance hosting datasets with billions of entries](https://demo.questdb.io) was impressive and those advantages seemed convincing:

    - Deploy via Docker or binaries
    - Open-source Apache 2.0 licensed
    - Good Python integration and PostgreSQL compatibility.

However, upon a closer look, the [PostgreSQL compatibility proved to be ill-conceived](https://github.com/questdb/questdb/issues/1450). The code examples in Python only ingested data and either [manually constructed the SQL query](https://github.com/questdb/questdb-slack-grafana-alerts/blob/main/python/mock_stock_data_example.py) or harnessed the [InfluxDB line protocol](https://github.com/questdb/demo-data/blob/master/demo_questdb.py). Querying the data is basically restricted to pure SQL e.g. in conunction with e.g. [Grafana](https://grafana.com).

Due to the lack of support of for PostgreSQL metadata, [sqlalchemy](https://www.sqlalchemy.org/) and therefore also [SQLModel](https://sqlmodel.tiangolo.com) could not be used:

```bash
nfcore_stats_api        | sqlalchemy.exc.DatabaseError: (psycopg2.DatabaseError) unknown function name: pg_catalog.version()
nfcore_stats_api        | LINE 1: select pg_catalog.version()
nfcore_stats_api        |                ^
nfcore_stats_api        |
nfcore_stats_api        | [SQL: select pg_catalog.version()]
```

Also other ORMs like [Tortoise](https://tortoise.github.io) are not supported. Due to the risk of SQL-injections and the relatively small size of the data generated and queried by this application, the decision to switch the database was made.

### Now: PostgreSQL

Currently, this application uses PostgreSQL in a separate container. However, switching to MariaDB or a local SQLite database will not be a problem due to the abstraction via SQLModel.
