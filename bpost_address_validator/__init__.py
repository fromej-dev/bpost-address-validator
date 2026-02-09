"""bpost_address_validator

Python wrapper for bpost External Mailing Address Proofing API.

Sync and async clients using httpx and Pydantic models.
"""

from .client import BpostClient, AsyncBpostClient
from .models import (
    AddressToValidate,
    AddressToValidateList,
    AddressBlockLines,
    UnstructuredAddressLineItem,
    PostalAddress,
    DeliveryPointLocation,
    StructuredDeliveryPointLocation,
    PostalCodeMunicipality,
    StructuredPostalCodeMunicipality,
    OtherDeliveryInformation,
    StructuredOtherDeliveryInformation,
    ValidateAddressesRequestContent,
    ValidateAddressOptions,
    CallerIdentification,
    ValidateAddressesRequest,
    ValidatedAddressResult,
    ValidatedAddressResultList,
    ValidateAddressesResponse,
    ValidationErrorItem,
)
from .errors import ApiError
from .helpers import (
    ValidationPresets,
    create_structured_address,
    create_unstructured_address,
    create_address_to_validate,
    create_simple_request,
    create_batch_request,
    extract_address_fields,
    extract_from_validated_address,
    extract_from_result,
    extract_label_lines,
    extract_all_results,
)

__all__ = [
    # Clients
    "BpostClient",
    "AsyncBpostClient",
    # Models
    "AddressToValidate",
    "AddressToValidateList",
    "AddressBlockLines",
    "UnstructuredAddressLineItem",
    "PostalAddress",
    "DeliveryPointLocation",
    "StructuredDeliveryPointLocation",
    "PostalCodeMunicipality",
    "StructuredPostalCodeMunicipality",
    "OtherDeliveryInformation",
    "StructuredOtherDeliveryInformation",
    "ValidateAddressesRequestContent",
    "ValidateAddressOptions",
    "CallerIdentification",
    "ValidateAddressesRequest",
    "ValidatedAddressResult",
    "ValidatedAddressResultList",
    "ValidateAddressesResponse",
    "ValidationErrorItem",
    # Errors
    "ApiError",
    # Helpers
    "ValidationPresets",
    "create_structured_address",
    "create_unstructured_address",
    "create_address_to_validate",
    "create_simple_request",
    "create_batch_request",
    "extract_address_fields",
    "extract_from_validated_address",
    "extract_from_result",
    "extract_label_lines",
    "extract_all_results",
]
