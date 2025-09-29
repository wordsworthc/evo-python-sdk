from uuid import UUID

from evo.common.exceptions import EvoClientException

from .endpoints.models import JobErrorPayload


class JobFailedException(EvoClientException):
    """Exception raised when a job fails.

    :param job_id: ID of the job that failed.
    :param error_payload: The error payload of the failed job.
    """

    def __init__(self, job_id: UUID, error_payload: JobErrorPayload):
        self.job_id = job_id
        self.error_payload = error_payload
        super().__init__(f"Job {job_id} failed: {self.error_payload.title}")


class UnknownJobPayload(EvoClientException):
    def __init__(self, job_id: UUID, error_message: str):
        self.job_id = job_id
        super().__init__(error_message)


class CacheNotConfiguredException(EvoClientException):
    """Exception raised when the cache is not configured."""


class MissingColumnInTable(EvoClientException):
    """Exception raised when the provided table is missing some columns."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
