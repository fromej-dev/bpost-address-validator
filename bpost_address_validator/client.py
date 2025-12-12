from __future__ import annotations

from typing import Any, Dict, Optional, Union, Literal

import httpx

from .errors import ApiError
from .models import ValidateAddressesRequest, ValidateAddressesResponse


DEFAULT_BASE_URL = "https://api.mailops-np.bpost.cloud"

# Supported environment prefixes for the path segment
Environment = Literal["roa-info", "roa-info-st", "roa-info-ac"]


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


class BpostClient:
    """Synchronous client for the bpost External Mailing Address Proofing API.

    Example:
        with BpostClient(api_key="...", environment="roa-info") as client:
            resp = client.validate_addresses(request_payload)
    """

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        environment: Environment = "roa-info",
        timeout: Optional[float] = 30.0,
        client: Optional[httpx.Client] = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._environment: Environment = environment
        self._timeout = timeout
        self._external_client = client is not None
        self._client = client or httpx.Client(
            base_url=self._base_url,
            headers={
                "Content-Type": "application/json",
                "x-api-key": api_key
            },
            timeout=self._timeout,
        )
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
        body = _ensure_request_payload(payload)
        try:
            res = self._client.post(self._validate_path, json=body)
        except httpx.HTTPError as e:  # transport-level error
            raise ApiError("HTTP transport error") from e

        if res.status_code != 200:
            details: Any
            try:
                details = res.json()
            except Exception:
                details = res.text
            raise ApiError(
                f"Unexpected status {res.status_code}",
                status_code=res.status_code,
                details=details,
            )

        data = res.json()
        return ValidateAddressesResponse.model_validate(data)


class AsyncBpostClient:
    """Asynchronous client for the bpost External Mailing Address Proofing API."""

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        environment: Environment = "roa-info",
        timeout: Optional[float] = 30.0,
        client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._environment: Environment = environment
        self._timeout = timeout
        self._external_client = client is not None
        self._client = client or httpx.AsyncClient(
            base_url=self._base_url,
            headers={
                "Content-Type": "application/json",
                "x-api-key": api_key
            },
            timeout=self._timeout,
        )
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
        body = _ensure_request_payload(payload)
        try:
            res = await self._client.post(self._validate_path, json=body)
        except httpx.HTTPError as e:
            raise ApiError("HTTP transport error") from e

        if res.status_code != 200:
            try:
                details: Any = res.json()
            except Exception:
                details = await res.aread()
            raise ApiError(
                f"Unexpected status {res.status_code}",
                status_code=res.status_code,
                details=details,
            )

        data = res.json()
        return ValidateAddressesResponse.model_validate(data)
