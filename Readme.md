# nf-core stats backend

The new _nf-core stats backend_ provides simple-to-use REST and GraphQL web services to query/retrieve statistics and metadata about the [nf-core community](https://nf-co.re) and their pipelines. The data is daily aggregated from Github, Twitter, Slack and Youtube. It’s designed with simplicity and performance emphasized.

## Development

### Debugging

To enable debugging code, the container _nfcore_stats_api_ has set `stdin_open` and `tty` true, such that one can attach a terminal to the container. This is most useful in conjunction with `set_trace()`. Put

```python
import pdb; pdb.set_trace()
```

anywhere within the body of a function. If that function is executed, you will be able to step through every command and also interactively explore the variables. To do so, you need to first attach a new terminal to the API container

```bash
docker container attach nfcore_stats_api
```

and then send requests to the API to trigger the function execution.

### Importing existing data into the database

The new backend has dedicated APIs meant to import the existing JSON files scraped by the current website. To import those
to the database, navigate into the folder containing the existing json files and send them as request bodies to the respective endpoints:

```bash
cd /path/to/your/json/files
curl --data-binary "@pipelines.json" -H "Content-Type: application/json" -X PUT http://localhost:8000/json/pipelines
```

Mind the `@` symbol preceding the file name. You can also specify `--data-binary "@/path/to/your/json/files/pipelines.json"` if you are dispatching the request from outside the folder.

## Production deployment
