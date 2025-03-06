# Evo Object Service Client

The Geoscience Object Service is Seequent's next-generation cloud offering for geoscience
data, empowering our users to build responsive modern workflows. 

## Using the library

See the [Getting Started](quickstart.md) guide for how to use this library.

## Developing the library

`uv run [command]` can be used to run arbitrary scripts or commands in your project environment.

Prior to every `uv run` invocation, `uv` will verify that the lockfile is up-to-date with the pyproject.toml, 
and that the environment is up-to-date with the lockfile, keeping your project in-sync without the need for manual intervention. 
`uv run` guarantees that your command is run in a consistent, locked environment.

Alternatively, you can use `uv sync` to manually update the environment then activate it before executing a command:

```bash
$ uv sync
$ source .venv/bin/activate
$ flask run -p 3000
$ python example.py
```

### Tests

To run the tests:
`uv run --extra test pytest tests/`

Alternatively, you can use `uv sync --all-groups` to manually update the environment including test dependencies then activate it before executing a command:

```bash
$ uv sync --all-groups
$ source .venv/bin/activate
$ pytest tests/
```
