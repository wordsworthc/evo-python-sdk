"""Evo Client Common Test Tools

The contents of this module are utilities that make it easy to test service client libraries. These utilities should
only be used for unit tests.
"""

import warnings

from .consts import ACCESS_TOKEN, BASE_URL, HUB, ORG, WORKSPACE_ID
from .http import (
    AbstractTestRequestHandler,
    MockResponse,
    TestAuthorizer,
    TestHTTPHeaderDict,
    TestTransport,
    TestWithConnector,
)
from .io import (
    StorageDestinationRequestHandler,
    DownloadRequestHandler,
    TestWithDownloadHandler,
    TestWithUploadHandler,
    UrlGenerator,
)
from .storage import TestWithStorage
from .utils import long_test, utc_datetime, utc_time

# Issue a warning whenever this module is imported.
warnings.warn(__doc__)

__all__ = [
    "ACCESS_TOKEN",
    "BASE_URL",
    "HUB",
    "ORG",
    "WORKSPACE_ID",
    "AbstractTestRequestHandler",
    "StorageDestinationRequestHandler",
    "DownloadRequestHandler",
    "MockResponse",
    "TestAuthorizer",
    "TestHTTPHeaderDict",
    "TestTransport",
    "TestWithConnector",
    "TestWithDownloadHandler",
    "TestWithStorage",
    "TestWithUploadHandler",
    "UrlGenerator",
    "long_test",
    "utc_datetime",
    "utc_time",
]
