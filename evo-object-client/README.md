# Evo Object Service Client

`evo-object-client`

The Geoscience Object Service is Seequent's next-generation cloud offering for geoscience
data, empowering our users to build responsive modern workflows. 

## Environment

`uv run` can be used to run arbitrary scripts or commands in your project environment.

Prior to every `uv run` invocation, `uv` will verify that the lockfile is up-to-date with the pyproject.toml, 
and that the environment is up-to-date with the lockfile, keeping your project in-sync without the need for manual intervention. 
`uv run` guarantees that your command is run in a consistent, locked environment.

To only sync:

`uv sync`

To make changes to the library or run the examples which will install Jupyter and other development related packages:

`uv run --extra dev [command]`


To run the tests:
`uv run --extra dev pytest tests/`