# Evo Python SDK
The Evo python SDK  repository is an open-source repository of python SDK’s designed to streamline workflows and application integrations with Evo services.

# Getting Started

All python SDKs in this monorepo are managed with [uv](https://docs.astral.sh/uv/). 
We use [workspaces](https://docs.astral.sh/uv/concepts/projects/workspaces/) in order to manage the different SDKs
published out of this repository. 

With workspaces, `uv lock` operates on the entire workspace at once. `uv run` and `uv sync` operate on the workspace root by default, though both accept a `--package` argument allowing you to run a command in a particular workspace member from any workspace directory.

## Install UV
To install uv on your machine, run one of the following convenience scripts from the root of the repo. These scripts ensure everyone is using the same version.

Windows:

./scripts/install-uv.ps1
UNIX-like:

./scripts/install-uv.sh
You can run the same script again whenever the version in the UV_VERSION file changes. It will replace your existing installation of uv.

## SDKs
- [evo-client-common](evo-client-common/README.md)
	- A shared library that provides common functionality for integrating with Seequent's client SDK's. 

- [evo-object-client](evo-object-client/README.md)
	- A geoscience object service client library designed to help get up and running with geoscience objects. 
