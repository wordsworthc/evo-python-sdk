import json

from ..connector import ApiConnector
from ..data import DependencyStatus, HealthCheckType, HTTPResponse, RequestMethod, ServiceHealth, ServiceStatus
from ..exceptions import ClientValueError

__all__ = [
    "get_service_health",
    "get_service_status",
]


async def _check_service_health(
    connector: ApiConnector, service_name: str, full: bool, check_type: HealthCheckType
) -> HTTPResponse:
    """Internal that calls the health check endpoint of a named service.

    :param connector: The API connector.
    :param service_name: The name of the service to check, as used in the Evo service URL.
    :param full: Whether to include full health check information.
    :param check_type: The type of health check to perform.

    :return: The response from the health check endpoint.
    """
    query_params = {}
    if full is True:
        query_params["full"] = True
    if check_type in {HealthCheckType.FULL, HealthCheckType.STRICT}:
        query_params["check_dependencies"] = True
    if check_type is HealthCheckType.STRICT:
        query_params["strict"] = True

    return await connector.call_api(
        RequestMethod.GET,
        f"/{service_name}/health_check",
        query_params=query_params,
        response_types_map={"200": HTTPResponse, "503": HTTPResponse},
    )


def _parse_service_status(status: str) -> ServiceStatus:
    """Parse a service status string into a ServiceStatus object.

    :param status: The status string to parse.

    :return: A ServiceStatus object.
    """
    try:
        return ServiceStatus(status)
    except ValueError as err:
        raise ClientValueError(f"Invalid service status: {status!r}") from err


def _parse_service_health_dict(service_name: str, status_code: int, response: dict) -> ServiceHealth:
    """Parse a service health response into a ServiceHealth object.

    :param service_name: The name of the service that was checked.
    :param status_code: The status code of the health check response.
    :param response: The response from the health check endpoint.

    :return: A ServiceHealth object.
    """
    try:
        status_str = response["status"]
        version = response["version"]
    except KeyError as err:
        raise ClientValueError("Service health response must include a status.") from err

    service_status = _parse_service_status(status_str)

    dependencies = None
    if "dependencies" in response:
        dependencies = {}
        for name, status_str in response["dependencies"].items():
            try:
                dependency_status = DependencyStatus(status_str)
            except ValueError as err:
                raise ClientValueError(f"Invalid status for dependency '{name}': {status_str!r}") from err
            dependencies[name] = dependency_status

    return ServiceHealth(
        service=service_name, status_code=status_code, status=service_status, version=version, dependencies=dependencies
    )


async def get_service_health(
    connector: ApiConnector, service_name: str, check_type: HealthCheckType = HealthCheckType.FULL
) -> ServiceHealth:
    """Check the health of a named service.

    Performs a full service health check and returns the results.

    :param connector: The API connector.
    :param service_name: The name of the service to check, as used in the Evo service URL.
    :param check_type: The type of health check to perform.

    :return: A ServiceHealth object.

    :raises EvoApiException: If the API returns an unexpected status code.
    :raises ClientValueError: If the response is not a valid service health check response.
    """
    response = await _check_service_health(connector, service_name, full=True, check_type=check_type)
    try:
        response_data = json.loads(response.data)
    except ValueError as err:
        raise ClientValueError("Invalid service health check response.") from err
    else:
        return _parse_service_health_dict(service_name, response.status, response_data)


async def get_service_status(
    connector: ApiConnector, service_name: str, check_type: HealthCheckType = HealthCheckType.FULL
) -> ServiceStatus:
    """Get the status of a named service.

    Performs a basic service health check and returns the status.

    :param connector: The API connector.
    :param service_name: The name of the service to check, as used in the Evo service URL.
    :param check_type: The type of health check to perform.

    :return: The status of the service.

    :raises EvoApiException: If the API returns an unexpected status code.
    :raises ClientValueError: If the response is not a valid service health status.
    """
    response = await _check_service_health(connector, service_name, full=False, check_type=check_type)
    try:
        response_str = response.data.decode()
    except ValueError as err:
        raise ClientValueError("Invalid service status response.") from err
    else:
        return _parse_service_status(response_str)
