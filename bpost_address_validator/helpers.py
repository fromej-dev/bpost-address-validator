"""Convenience functions and helpers for easy package usage."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

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
    ValidateAddressesRequest,
    ValidateAddressesRequestContent,
    ValidateAddressOptions,
)


class ValidationPresets:
    """Common validation option presets for convenience."""

    BASIC = ValidateAddressOptions()

    FULL = ValidateAddressOptions(
        include_submitted_address=True,
        include_default_geo_location=True,
        include_suggestions=True,
        include_formatting=True,
        include_default_geo_location_for_boxes=True,
        include_suffix_list=True,
        include_number_of_boxes=True,
        include_number_of_suffixes=True,
        include_list_of_boxes=True,
        include_nis_code=True,
        include_nis_hierarchy=True,
    )

    WITH_SUGGESTIONS = ValidateAddressOptions(
        include_submitted_address=True,
        include_suggestions=True,
        include_formatting=True,
    )

    WITH_FORMATTING = ValidateAddressOptions(
        include_formatting=True,
    )

    WITH_GEO = ValidateAddressOptions(
        include_default_geo_location=True,
        include_default_geo_location_for_boxes=True,
    )


def create_structured_address(
    street_name: Optional[str] = None,
    street_number: Optional[str] = None,
    box_number: Optional[str] = None,
    postal_code: Optional[str] = None,
    municipality_name: Optional[str] = None,
    country_name: Optional[str] = None,
    delivery_service_qualifier: Optional[str] = None,
) -> PostalAddress:
    """Create a structured postal address with common fields.

    Args:
        street_name: The street name
        street_number: The street number
        box_number: The box/apartment number
        postal_code: The postal code
        municipality_name: The municipality/city name
        country_name: The country name
        delivery_service_qualifier: Optional delivery service qualifier

    Returns:
        PostalAddress with structured fields populated

    Example:
        >>> addr = create_structured_address(
        ...     street_name="Muntstraat",
        ...     street_number="1",
        ...     postal_code="1000",
        ...     municipality_name="Bruxelles"
        ... )
    """
    delivery_point_location = None
    if street_name or street_number or box_number or country_name:
        delivery_point_location = DeliveryPointLocation(
            structured_delivery_point_location=StructuredDeliveryPointLocation(
                street_name=street_name,
                street_number=street_number,
                box_number=box_number,
                country_name=country_name,
            )
        )

    postal_code_municipality = None
    if postal_code or municipality_name or delivery_service_qualifier:
        postal_code_municipality = PostalCodeMunicipality(
            structured_postal_code_municipality=StructuredPostalCodeMunicipality(
                postal_code=postal_code,
                municipality_name=municipality_name,
                delivery_service_qualifier=delivery_service_qualifier,
            )
        )

    return PostalAddress(
        delivery_point_location=delivery_point_location,
        postal_code_municipality=postal_code_municipality,
    )


def create_unstructured_address(
    address_lines: List[str],
    locale: str = "nl",
) -> AddressBlockLines:
    """Create an unstructured address from text lines.

    Args:
        address_lines: List of address lines as strings
        locale: Language locale (default: "nl")

    Returns:
        AddressBlockLines with unstructured address lines

    Example:
        >>> addr_lines = create_unstructured_address([
        ...     "Muntstraat 1",
        ...     "1000 Bruxelles"
        ... ])
    """
    return AddressBlockLines(
        unstructured_address_line=[
            UnstructuredAddressLineItem(body=line, locale=locale)
            for line in address_lines
        ]
    )


def create_address_to_validate(
    id: str,
    dispatching_country: str = "BE",
    delivering_country: str = "BE",
    street_name: Optional[str] = None,
    street_number: Optional[str] = None,
    box_number: Optional[str] = None,
    postal_code: Optional[str] = None,
    municipality_name: Optional[str] = None,
    address_lines: Optional[List[str]] = None,
    locale: str = "nl",
) -> AddressToValidate:
    """Create an AddressToValidate with either structured or unstructured address.

    Args:
        id: Unique identifier for this address
        dispatching_country: Dispatching country ISO code (default: "BE")
        delivering_country: Delivering country ISO code (default: "BE")
        street_name: Street name (for structured address)
        street_number: Street number (for structured address)
        box_number: Box/apartment number (for structured address)
        postal_code: Postal code (for structured address)
        municipality_name: Municipality/city name (for structured address)
        address_lines: List of address text lines (for unstructured address)
        locale: Language locale for unstructured address (default: "nl")

    Returns:
        AddressToValidate ready to include in a request

    Example:
        >>> # Structured
        >>> addr = create_address_to_validate(
        ...     id="1",
        ...     street_name="Muntstraat",
        ...     street_number="1",
        ...     postal_code="1000",
        ...     municipality_name="Bruxelles"
        ... )
        >>> # Unstructured
        >>> addr = create_address_to_validate(
        ...     id="1",
        ...     address_lines=["Muntstraat 1", "1000 Bruxelles"]
        ... )
    """
    postal_address = None
    address_block_lines = None

    # Prefer structured address if provided
    if any([street_name, street_number, box_number, postal_code, municipality_name]):
        postal_address = create_structured_address(
            street_name=street_name,
            street_number=street_number,
            box_number=box_number,
            postal_code=postal_code,
            municipality_name=municipality_name,
        )
    elif address_lines:
        address_block_lines = create_unstructured_address(address_lines, locale)

    return AddressToValidate(
        id=id,
        dispatching_country_iso_code=dispatching_country,
        delivering_country_iso_code=delivering_country,
        postal_address=postal_address,
        address_block_lines=address_block_lines,
    )


def create_simple_request(
    addresses: List[AddressToValidate],
    options: Optional[ValidateAddressOptions] = None,
) -> ValidateAddressesRequest:
    """Create a ValidateAddressesRequest from a list of addresses.

    Args:
        addresses: List of AddressToValidate objects
        options: Optional validation options (defaults to None)

    Returns:
        ValidateAddressesRequest ready to send to the API

    Example:
        >>> addresses = [
        ...     create_address_to_validate(
        ...         id="1",
        ...         street_name="Muntstraat",
        ...         street_number="1",
        ...         postal_code="1000",
        ...         municipality_name="Bruxelles"
        ...     )
        ... ]
        >>> req = create_simple_request(addresses, ValidationPresets.FULL)
    """
    return ValidateAddressesRequest(
        validate_addresses_request=ValidateAddressesRequestContent(
            address_to_validate_list=AddressToValidateList(
                address_to_validate=addresses
            ),
            validate_address_options=options,
        )
    )


def create_batch_request(
    addresses: List[Dict[str, Any]],
    dispatching_country: str = "BE",
    delivering_country: str = "BE",
    options: Optional[ValidateAddressOptions] = None,
) -> ValidateAddressesRequest:
    """Create a ValidateAddressesRequest from a list of address dictionaries.

    Args:
        addresses: List of address dictionaries with keys like:
            - street_name, street_number, box_number, postal_code, municipality_name
            - OR address_lines (list of strings)
        dispatching_country: Default dispatching country ISO code (default: "BE")
        delivering_country: Default delivering country ISO code (default: "BE")
        options: Optional validation options

    Returns:
        ValidateAddressesRequest ready to send to the API

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
        >>> req = create_batch_request(addresses)
    """
    address_list = []
    for i, addr_data in enumerate(addresses):
        address_list.append(
            create_address_to_validate(
                id=str(addr_data.get("id", i + 1)),
                dispatching_country=addr_data.get("dispatching_country", dispatching_country),
                delivering_country=addr_data.get("delivering_country", delivering_country),
                street_name=addr_data.get("street_name"),
                street_number=addr_data.get("street_number"),
                box_number=addr_data.get("box_number"),
                postal_code=addr_data.get("postal_code"),
                municipality_name=addr_data.get("municipality_name"),
                address_lines=addr_data.get("address_lines"),
                locale=addr_data.get("locale", "nl"),
            )
        )

    return create_simple_request(address_list, options)
