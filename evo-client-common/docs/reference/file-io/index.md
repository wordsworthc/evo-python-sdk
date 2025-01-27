# File I/O

Some utility classes for robust file I/O operations have been implemented in the `evo.common.io` module. These classes
are designed to handle large files and provide a simple interface for reading and writing data in chunks.

## Remote Storage

The most common use case for these classes is to transfer large files between local storage and remote storage. [HTTPSource][evo.common.io.HTTPSource] and [BlobStorageDestination][evo.common.io.BlobStorageDestination] each have static methods that make it easy to upload and download files.

## Azure Blob Storage

Evo APIs currently use Azure Blob Storage for remote storage. Downloading large files is very standardized across service providers, but uploading large files is a different story. Azure Blob Storage has a unique way to support chunked file upload, so an Azure-specific implemntation is provided in [BlobStorageDestination][evo.common.io.BlobStorageDestination].

## Interfaces

::: evo.common.io.interfaces.ISource
    options:
        heading_level: 3
        show_category_heading: false

::: evo.common.io.interfaces.IDestination
    options:
        heading_level: 3
        show_category_heading: false

::: evo.common.io.ChunkedIOManager
