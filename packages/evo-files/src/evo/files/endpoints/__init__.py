"""
File API
=============

The File API provides the ability to manage files of any type or size, associated with
your Evo workspace. Enable your product with Evo connected workflows by integrating with the Seequent Evo
File API. Most file formats and sizes are accepted.

Files can be referenced by their UUID, or by a user-defined file path. Files are versioned, so updating or
replacing them will create a new version of the file. The latest version of the file is always returned
unless a specific version is requested.

For more information on using the File API, see [Overview](https://developer.seequent.com/docs/guides/file/), or the API references here.


This code is generated from the OpenAPI specification for File API.
API version: 2.7.3
"""

# Import endpoint apis.
from .api import FileV2Api

__all__ = [
    "FileV2Api",
]
