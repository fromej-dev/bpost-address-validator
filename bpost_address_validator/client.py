from __future__ import annotations

from typing import Any, Dict, List, Optional, Union, Literal

import httpx

from .errors import ApiError
from .models import ValidateAddressesRequest, ValidateAddressesResponse, ValidateAddressOptions


DEFAULT_BASE_URL = "https://api.mailops.bpost.cloud"

# Supported environment prefixes for the path segment
# Note: bpost uses different path segments per environment
# - prod: roa-info
# - test: roa-info-st2
# - uat:  roa-info-ac
Environment = Literal["roa-info", "roa-info-st2", "roa-info-ac"]

# Optional presets that set both base_url (domain) and environment (path prefix)
EnvironmentPreset = Literal["prod", "test", "uat"]

_PRESET_CONFIG: Dict[EnvironmentPreset, Dict[str, str]] = {
    "prod": {
        "base_url": "https://api.mailops.bpost.cloud",
        "environment": "roa-info",
    },
    "test": {
        "base_url": "https://api.mailops-np.bpost.cloud",
        "environment": "roa-info-st2",
    },
    "uat": {
        "base_url": "https://api.mailops-np.bpost.cloud",
        "environment": "roa-info-ac",
    },
}


def _ensure_request_payload(
    payload: Union[ValidateAddressesRequest, Dict[str, Any]],
) -> Dict[str, Any]:
    if isinstance(payload, ValidateAddressesRequest):
        return payload.model_dump(by_alias=True, exclude_none=True)
    if isinstance(payload, dict):
        return payload
    raise TypeError(
        "payload must be ValidateAddressesRequest or dict, got " + type(payload).__name__
    )


def _handle_error_response(res: httpx.Response) -> None:
    """Extract error details from response and raise ApiError."""
    try:
        details: Any = res.json()
    except Exception:
        details = res.text
    raise ApiError(
        f"Unexpected status {res.status_code}",
        status_code=res.status_code,
        details=details,
    )


class BpostClient:
    """Synchronous client for the bpost External Mailing Address Proofing API.

    Example:
        with BpostClient(api_key="...", preset="test") as client:
            resp = client.validate_addresses(request_payload)
    """

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        environment: Environment = "roa-info",
        preset: Optional[EnvironmentPreset] = None,
        timeout: Optional[float] = 30.0,
        client: Optional[httpx.Client] = None,
        max_connections: int = 100,
        max_keepalive_connections: int = 20,
    ) -> None:
        """Initialize the BpostClient.

        Args:
            api_key: Your bpost API key
            base_url: Base URL for the API (default: production URL)
            environment: Environment path prefix (default: "roa-info")
            preset: Preset configuration ("prod", "test", or "uat")
            timeout: Request timeout in seconds (default: 30.0)
            client: Optional custom httpx.Client instance
            max_connections: Maximum number of connections in the pool (default: 100)
            max_keepalive_connections: Maximum number of keep-alive connections (default: 20)
        """
        # Apply preset if provided; it sets both base_url and environment
        if preset is not None:
            cfg = _PRESET_CONFIG[preset]
            base_url = cfg["base_url"]
            environment = cfg["environment"]  # type: ignore[assignment]

        self._base_url = base_url.rstrip("/")
        self._environment: Environment = environment
        self._timeout = timeout
        self._external_client = client is not None

        if client is None:
            limits = httpx.Limits(
                max_connections=max_connections,
                max_keepalive_connections=max_keepalive_connections,
            )
            self._client = httpx.Client(
                base_url=self._base_url,
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": api_key
                },
                timeout=self._timeout,
                limits=limits,
            )
        else:
            self._client = client

        self._validate_path = (
            f"/{self._environment}/externalMailingAddressProofingRest/validateAddresses"
        )

    def close(self) -> None:
        if not self._external_client:
            self._client.close()

    def __enter__(self) -> "BpostClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # pragma: no cover - context manager
        self.close()

    def validate_addresses(
        self,
        payload: Union[ValidateAddressesRequest, Dict[str, Any]],
    ) -> ValidateAddressesResponse:
        """Validate one or more addresses.

        Args:
            payload: ValidateAddressesRequest model or raw dict payload

        Returns:
            ValidateAddressesResponse with validation results

        Raises:
            ApiError: On transport errors or non-200 responses
        """
        body = _ensure_request_payload(payload)
        try:
            res = self._client.post(self._validate_path, json=body)
        except httpx.HTTPError as e:  # transport-level error
            raise ApiError("HTTP transport error") from e

        if res.status_code != 200:
            _handle_error_response(res)

        data = res.json()
        return ValidateAddressesResponse.model_validate(data)

    def validate_address_simple(
        self,
        *,
        street_name: Optional[str] = None,
        street_number: Optional[str] = None,
        box_number: Optional[str] = None,
        postal_code: Optional[str] = None,
        municipality_name: Optional[str] = None,
        address_lines: Optional[List[str]] = None,
        dispatching_country: str = "BE",
        delivering_country: str = "BE",
        locale: str = "nl",
        options: Optional[ValidateAddressOptions] = None,
    ) -> ValidateAddressesResponse:
        """Validate a single address with simple parameters.

        Args:
            street_name: Street name (for structured address)
            street_number: Street number (for structured address)
            box_number: Box/apartment number (for structured address)
            postal_code: Postal code (for structured address)
            municipality_name: Municipality/city name (for structured address)
            address_lines: List of address text lines (for unstructured address)
            dispatching_country: Dispatching country ISO code (default: "BE")
            delivering_country: Delivering country ISO code (default: "BE")
            locale: Language locale for unstructured address (default: "nl")
            options: Optional validation options

        Returns:
            ValidateAddressesResponse with validation results

        Example:
            >>> with BpostClient(api_key="...", preset="test") as client:
            ...     result = client.validate_address_simple(
            ...         street_name="Muntstraat",
            ...         street_number="1",
            ...         postal_code="1000",
            ...         municipality_name="Bruxelles"
            ...     )
        """
        from .helpers import create_address_to_validate, create_simple_request

        address = create_address_to_validate(
            id="1",
            dispatching_country=dispatching_country,
            delivering_country=delivering_country,
            street_name=street_name,
            street_number=street_number,
            box_number=box_number,
            postal_code=postal_code,
            municipality_name=municipality_name,
            address_lines=address_lines,
            locale=locale,
        )
        request = create_simple_request([address], options)
        return self.validate_addresses(request)

    def validate_addresses_batch(
        self,
        addresses: List[Dict[str, Any]],
        *,
        dispatching_country: str = "BE",
        delivering_country: str = "BE",
        options: Optional[ValidateAddressOptions] = None,
    ) -> ValidateAddressesResponse:
        """Validate multiple addresses from a list of dictionaries.

        Args:
            addresses: List of address dictionaries with keys like:
                - street_name, street_number, box_number, postal_code, municipality_name
                - OR address_lines (list of strings)
            dispatching_country: Default dispatching country ISO code (default: "BE")
            delivering_country: Default delivering country ISO code (default: "BE")
            options: Optional validation options

        Returns:
            ValidateAddressesResponse with validation results for all addresses

        Example:
            >>> addresses = [
            ...     {
            ...         "street_name": "Muntstraat",
            ...         "street_number": "1",
            ...         "postal_code": "1000",
            ...         "municipality_name": "Bruxelles"
            ...     },
            ...     {
            ...         "address_lines": ["Rue de la Loi 16", "1000 Bruxelles"]
            ...     }
            ... ]
            >>> with BpostClient(api_key="...", preset="test") as client:
            ...     results = client.validate_addresses_batch(addresses)
        """
        from .helpers import create_batch_request

        request = create_batch_request(
            addresses,
            dispatching_country=dispatching_country,
            delivering_country=delivering_country,
            options=options,
        )
        return self.validate_addresses(request)


class AsyncBpostClient:
    """Asynchronous client for the bpost External Mailing Address Proofing API.

    Example:
        async with AsyncBpostClient(api_key="...", preset="test") as client:
            resp = await client.validate_addresses(request_payload)
    """

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        environment: Environment = "roa-info",
        preset: Optional[EnvironmentPreset] = None,
        timeout: Optional[float] = 30.0,
        client: Optional[httpx.AsyncClient] = None,
        max_connections: int = 100,
        max_keepalive_connections: int = 20,
    ) -> None:
        """Initialize the AsyncBpostClient.

        Args:
            api_key: Your bpost API key
            base_url: Base URL for the API (default: production URL)
            environment: Environment path prefix (default: "roa-info")
            preset: Preset configuration ("prod", "test", or "uat")
            timeout: Request timeout in seconds (default: 30.0)
            client: Optional custom httpx.AsyncClient instance
            max_connections: Maximum number of connections in the pool (default: 100)
            max_keepalive_connections: Maximum number of keep-alive connections (default: 20)
        """
        # Apply preset if provided; it sets both base_url and environment
        if preset is not None:
            cfg = _PRESET_CONFIG[preset]
            base_url = cfg["base_url"]
            environment = cfg["environment"]  # type: ignore[assignment]

        self._base_url = base_url.rstrip("/")
        self._environment: Environment = environment
        self._timeout = timeout
        self._external_client = client is not None

        if client is None:
            limits = httpx.Limits(
                max_connections=max_connections,
                max_keepalive_connections=max_keepalive_connections,
            )
            self._client = httpx.AsyncClient(
                base_url=self._base_url,
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": api_key
                },
                timeout=self._timeout,
                limits=limits,
            )
        else:
            self._client = client

        self._validate_path = (
            f"/{self._environment}/externalMailingAddressProofingRest/validateAddresses"
        )

    async def aclose(self) -> None:
        if not self._external_client:
            await self._client.aclose()

    async def __aenter__(self) -> "AsyncBpostClient":  # pragma: no cover - CM
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:  # pragma: no cover - CM
        await self.aclose()

    async def validate_addresses(
        self,
        payload: Union[ValidateAddressesRequest, Dict[str, Any]],
    ) -> ValidateAddressesResponse:
        """Validate one or more addresses asynchronously.

        Args:
            payload: ValidateAddressesRequest model or raw dict payload

        Returns:
            ValidateAddressesResponse with validation results

        Raises:
            ApiError: On transport errors or non-200 responses
        """
        body = _ensure_request_payload(payload)
        try:
            res = await self._client.post(self._validate_path, json=body)
        except httpx.HTTPError as e:
            raise ApiError("HTTP transport error") from e

        if res.status_code != 200:
            _handle_error_response(res)

        data = res.json()
        return ValidateAddressesResponse.model_validate(data)

    async def validate_address_simple(
        self,
        *,
        street_name: Optional[str] = None,
        street_number: Optional[str] = None,
        box_number: Optional[str] = None,
        postal_code: Optional[str] = None,
        municipality_name: Optional[str] = None,
        address_lines: Optional[List[str]] = None,
        dispatching_country: str = "BE",
        delivering_country: str = "BE",
        locale: str = "nl",
        options: Optional[ValidateAddressOptions] = None,
    ) -> ValidateAddressesResponse:
        """Validate a single address with simple parameters (async).

        Args:
            street_name: Street name (for structured address)
            street_number: Street number (for structured address)
            box_number: Box/apartment number (for structured address)
            postal_code: Postal code (for structured address)
            municipality_name: Municipality/city name (for structured address)
            address_lines: List of address text lines (for unstructured address)
            dispatching_country: Dispatching country ISO code (default: "BE")
            delivering_country: Delivering country ISO code (default: "BE")
            locale: Language locale for unstructured address (default: "nl")
            options: Optional validation options

        Returns:
            ValidateAddressesResponse with validation results

        Example:
            >>> async with AsyncBpostClient(api_key="...", preset="test") as client:
            ...     result = await client.validate_address_simple(
            ...         street_name="Muntstraat",
            ...         street_number="1",
            ...         postal_code="1000",
            ...         municipality_name="Bruxelles"
            ...     )
        """
        from .helpers import create_address_to_validate, create_simple_request

        address = create_address_to_validate(
            id="1",
            dispatching_country=dispatching_country,
            delivering_country=delivering_country,
            street_name=street_name,
            street_number=street_number,
            box_number=box_number,
            postal_code=postal_code,
            municipality_name=municipality_name,
            address_lines=address_lines,
            locale=locale,
        )
        request = create_simple_request([address], options)
        return await self.validate_addresses(request)

    async def validate_addresses_batch(
        self,
        addresses: List[Dict[str, Any]],
        *,
        dispatching_country: str = "BE",
        delivering_country: str = "BE",
        options: Optional[ValidateAddressOptions] = None,
    ) -> ValidateAddressesResponse:
        """Validate multiple addresses from a list of dictionaries (async).

        Args:
            addresses: List of address dictionaries with keys like:
                - street_name, street_number, box_number, postal_code, municipality_name
                - OR address_lines (list of strings)
            dispatching_country: Default dispatching country ISO code (default: "BE")
            delivering_country: Default delivering country ISO code (default: "BE")
            options: Optional validation options

        Returns:
            ValidateAddressesResponse with validation results for all addresses

        Example:
            >>> addresses = [
            ...     {
            ...         "street_name": "Muntstraat",
            ...         "street_number": "1",
            ...         "postal_code": "1000",
            ...         "municipality_name": "Bruxelles"
            ...     },
            ...     {
            ...         "address_lines": ["Rue de la Loi 16", "1000 Bruxelles"]
            ...     }
            ... ]
            >>> async with AsyncBpostClient(api_key="...", preset="test") as client:
            ...     results = await client.validate_addresses_batch(addresses)
        """
        from .helpers import create_batch_request

        request = create_batch_request(
            addresses,
            dispatching_country=dispatching_country,
            delivering_country=delivering_country,
            options=options,
        )
        return await self.validate_addresses(request)
