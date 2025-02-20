# Evo Client Common

`evo-client-common`

The Geoscience Object Service is Seequent's next-generation cloud offering for geoscience
data, empowering our users to build responsive modern workflows. 


## Environment

`uv run` can be used to run arbitrary scripts or commands in your project environment.

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

To make changes to the library or run the examples which will install Jupyter and other development related packages:

`uv run [command]`

There are example Jupyter notebooks in `docs\examples`. To run the examples copy the `docs\examples\.example.env` file to 
`docs\examples\.env` with any changes, if necessary. This file is populated with example host names which should 
generally work.

To use the OAuth2 token generation there is a configuration file in `\evo\common\services\oauth_config.yml` with 
relevant urls.

### Tests

To run the tests:
`uv run --extra dev pytest tests/`

### Building Documentation

You can run `mkdocs` commands ensuring all dependencies are installed with `uv run --extra docs mkdocs [command]`.


`uv run --extra docs mkdocs serve` serves up a webpage with the documentation.

`uv run --extra docs mkdocs build` creates a static copy accessed via `site/index.html`.
