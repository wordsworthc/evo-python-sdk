# Getting Started

## Basic Usage

Just want to get going? This is the simplest setup for Geoscience Object Service usage.

``` python linenums="1"
--8<-- "docs/examples/code_samples.py:ALL"
```

## What's going on?

### Configure your Transport Layer

The transport layer is used to standardize the way requests are made to our servers. This is where the user agent is
configured.

``` python
--8<-- "docs/examples/code_samples.py:Transport"
```

### Log in to Evo

The Evo service requires users to log in to access their data. This is done using the OAuth 2.0 protocol. The
[`AuthorizationCodeAuthorizer`][evo.oauth.AuthorizationCodeAuthorizer] class is used to authenticate users and obtain an
access token. The access token is used to make requests to the Evo service.

``` python
--8<-- "docs/examples/code_samples.py:OAuth"
```

### Using the Discovery API

The discovery API is used to find the organizations and hubs that a user has access to. This is done using the
[`DiscoveryApiClient`][evo.discovery.DiscoveryApiClient] class. The `list_organizations()` method is used to get a list
of organizations. Each listed organization includes a list of hubs that are used by that organization.

``` python
--8<-- "docs/examples/code_samples.py:Org-Discovery"
```

### Using the Workspace API

The Workspace API is used to find the workspaces that a user has access to. This is done using the
[`WorkspaceClient`][evo.workspaces.WorkspaceServiceClient] class. The `get_workspaces()` method is used to get a list
of workspaces belonging to the specified organization on the specified hub.

``` python
--8<-- "docs/examples/code_samples.py:Workspace-Discovery"
```

### Interacting with the Geoscience Object Service

[`ObjectServiceClient`][evo.object.ObjectServiceClient] requires an [`Environment`][evo.common.Environment] and an
[`ApiConnector`][evo.common.ApiConnector]. Workspace objects have a `get_environment()` method that returns an
environment object, which can be used by one or more service clients to interact with different services using the same
organization and workspace. The hub connector that was used for workspace discovery can be reused for interacting
with services.

``` python
--8<-- "docs/examples/code_samples.py:ServiceClient"
```

## Skip Organization and Workspace Discovery

If you already know the hub URL, organization ID, and workspace ID, you can skip the discovery steps and directly create
connector and environment objects.

``` python
--8<-- "docs/examples/code_samples.py:imports"
--8<-- "docs/examples/code_samples.py:Transport"

--8<-- "docs/examples/code_samples.py:OAuth"

--8<-- "docs/examples/code_samples.py:Skip-Discovery"
```
