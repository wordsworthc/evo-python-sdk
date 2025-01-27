# Evo Client Common

`evo-client-common`

The Geoscience Object Service (colloquially known as Goose) is Seequent's next-generation cloud offering for geoscience
data, empowering our users to build responsive modern workflows. The Goose integration with Leapfrog is a key
development milestone that has very little value in isolation - the full benefits will only be realised as third
parties also integrate with Goose.

Phase one of the LF - Goose integration will establish the foundation for more comprehensive Evo library components,
offering common functionality as a shared python package. Python was chosen primarily because it is convenient for
integrating with Leapfrog, however we expect that it would be used to make development of libraries in other
languages/environments faster once the need for those arises.


## Environment

To use the library:

`pip install -e .`

To make changes to the library or run the examples which will install Jupyter and other development related packages:

`pip install -e .[dev]`

There are example Jupyter notebooks in `docs\examples`. To run the examples copy the `docs\examples\.example.env` file to 
`docs\examples\.env` with any changes, if necessary. This file is populated with example host names which should 
generally work.

To use the OAuth2 token generation there is a configuration file in `\evo\common\services\oauth_config.yml` with 
relevant urls.

## Building Documentation

`pip install -r docs\requirements.txt`

Then run `mkdocs serve` which serves up a webpage with the documentation or `mkdocs build` which creates a static copy accessed via `site/index.html`.
