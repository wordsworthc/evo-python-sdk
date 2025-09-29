from evo.blockmodel.endpoints.models import JobResponse, JobStatus
from evo.common.test_tools import AbstractTestRequestHandler, MockResponse


class JobPollingRequestHandler(AbstractTestRequestHandler):
    def __init__(self, job_response: JobResponse, pending_request: int = 0) -> None:
        self._job_response = job_response
        self._pending_requests = pending_request

    def job_poll(self) -> MockResponse:
        if self._pending_requests > 0:
            self._pending_requests -= 1
            job_response = JobResponse(job_status=JobStatus.PROCESSING)
        else:
            job_response = self._job_response
        return MockResponse(status_code=200, content=job_response.model_dump_json())
