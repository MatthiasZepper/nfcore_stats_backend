# nf-core stats backend

The new _nf-core stats backend_ provides simple-to-use REST and GraphQL web services to query/retrieve statistics and metadata about the [nf-core community](https://nf-co.re) and their pipelines. The data is daily aggregated from Github, Twitter, Slack and Youtube. It’s designed with simplicity and performance emphasized.

## Importing existing data into the database

The new backend has dedicated APIs meant to import the existing JSON files scraped by the current website. To import those
to the database, navigate into the folder containing the existing json files and send them as request bodies to the respective endpoints:

```bash
cd /path/to/your/json/files
curl --data-binary "@pipelines.json" -H "Content-Type: application/json" -X PUT http://localhost:8000/json/pipelines
```

Mind the `@` symbol preceding the file name. You can also specify `--data-binary "@/path/to/your/json/files/pipelines.json"` if you are dispatching the request from outside the folder.
