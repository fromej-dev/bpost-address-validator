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
    ValidatedAddress,
    ValidatedAddressResult,
    ValidateAddressesResponse,
    ServicePointResultItem,
    NisCodeInfo,
    AddressFields,
    ValidatedAddressFields,
    AddressResultFields,
    GeoLocation,
    LocalizedName,
    NisHierarchyEntry,
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


# ---------------------------------------------------------------------------
# Extraction helpers: validated response → flat address fields
# ---------------------------------------------------------------------------


def extract_address_fields(postal_address: Optional[PostalAddress]) -> AddressFields:
    """Extract flat address fields from a PostalAddress.

    Handles both response-style (flattened) and request-style (nested)
    PostalAddress structures, preferring the flattened fields when available.

    Args:
        postal_address: A PostalAddress from a validated result or request

    Returns:
        AddressFields with attributes matching the ``create_structured_address``
        parameters. Missing values are ``None``.

    Example:
        >>> result = client.validate_address_simple(...)
        >>> addr = result.first_result.first_validated_address
        >>> fields = extract_address_fields(addr.postal_address)
        >>> fields.street_name
        'Muntstraat'
    """
    if postal_address is None:
        return AddressFields()

    street_name = None
    street_number = None
    box_number = None
    country_name = None
    postal_code = None
    municipality_name = None
    delivery_service_qualifier = None

    # Resolve the structured delivery point — prefer the response-style
    # flattened field, fall back to the nested request-style wrapper.
    sdpl = postal_address.structured_delivery_point_location
    if sdpl is None and postal_address.delivery_point_location is not None:
        sdpl = postal_address.delivery_point_location.structured_delivery_point_location

    if sdpl is not None:
        street_name = sdpl.street_name
        street_number = sdpl.street_number
        box_number = sdpl.box_number
        country_name = sdpl.country_name

    # Top-level country_name on PostalAddress takes precedence if set.
    if postal_address.country_name is not None:
        country_name = postal_address.country_name

    # Resolve postal code / municipality.
    spcm = postal_address.structured_postal_code_municipality
    if spcm is None and postal_address.postal_code_municipality is not None:
        spcm = postal_address.postal_code_municipality.structured_postal_code_municipality

    if spcm is not None:
        postal_code = spcm.postal_code
        municipality_name = spcm.municipality_name
        delivery_service_qualifier = spcm.delivery_service_qualifier

    return AddressFields(
        street_name=street_name,
        street_number=street_number,
        box_number=box_number,
        postal_code=postal_code,
        municipality_name=municipality_name,
        country_name=country_name,
        delivery_service_qualifier=delivery_service_qualifier,
    )


def extract_from_validated_address(
    validated_address: Optional[ValidatedAddress],
) -> ValidatedAddressFields:
    """Extract flat address fields from a ValidatedAddress.

    Returns the same attributes as ``AddressFields`` plus ``score`` and
    ``address_language``.

    Args:
        validated_address: A ValidatedAddress from a validation result

    Returns:
        ValidatedAddressFields with address data and validation metadata.

    Example:
        >>> addr = result.first_result.first_validated_address
        >>> info = extract_from_validated_address(addr)
        >>> info.postal_code, info.score
        ('1000', 'perfect')
    """
    if validated_address is None:
        return ValidatedAddressFields()

    base = extract_address_fields(validated_address.postal_address)
    return ValidatedAddressFields(
        street_name=base.street_name,
        street_number=base.street_number,
        box_number=base.box_number,
        postal_code=base.postal_code,
        municipality_name=base.municipality_name,
        country_name=base.country_name,
        delivery_service_qualifier=base.delivery_service_qualifier,
        score=validated_address.score,
        address_language=validated_address.address_language,
    )


def extract_from_result(
    result: Optional[ValidatedAddressResult],
) -> AddressResultFields:
    """Extract flat address fields from a ValidatedAddressResult.

    Uses the first (best-scoring) validated address. Returns the same
    attributes as ``ValidatedAddressFields`` plus ``id``.

    Args:
        result: A ValidatedAddressResult from the API response

    Returns:
        AddressResultFields with address data, validation metadata, and id.

    Example:
        >>> response = client.validate_address_simple(...)
        >>> info = extract_from_result(response.first_result)
        >>> info.street_name, info.id
        ('Muntstraat', '1')
    """
    if result is None:
        return AddressResultFields()

    base = extract_from_validated_address(result.first_validated_address)
    return AddressResultFields(
        street_name=base.street_name,
        street_number=base.street_number,
        box_number=base.box_number,
        postal_code=base.postal_code,
        municipality_name=base.municipality_name,
        country_name=base.country_name,
        delivery_service_qualifier=base.delivery_service_qualifier,
        score=base.score,
        address_language=base.address_language,
        id=result.id,
    )


def extract_label_lines(validated_address: Optional[ValidatedAddress]) -> List[str]:
    """Extract formatted label lines from a ValidatedAddress.

    The label is available when the ``include_formatting`` option was enabled
    during validation.

    Args:
        validated_address: A ValidatedAddress that may contain label data

    Returns:
        List of formatted address line strings, or an empty list if no
        label data is available.

    Example:
        >>> addr = result.first_result.first_validated_address
        >>> for line in extract_label_lines(addr):
        ...     print(line)
        'Muntstraat 1'
        '1000 BRUSSEL'
    """
    if validated_address is None or validated_address.label is None:
        return []

    label = validated_address.label
    line_data = label.get("Line", [])

    # The label Line field can be a single dict or a list of dicts,
    # each containing a "*body" key with the text.
    if isinstance(line_data, dict):
        line_data = [line_data]

    lines: List[str] = []
    for item in line_data:
        if isinstance(item, dict):
            text = item.get("*body", "")
            if text:
                lines.append(text)
        elif isinstance(item, str):
            lines.append(item)

    return lines


def extract_all_results(
    response: Optional[ValidateAddressesResponse],
) -> List[AddressResultFields]:
    """Extract flat address fields from every result in a response.

    Convenience wrapper around ``extract_from_result`` for batch responses.

    Args:
        response: The full ValidateAddressesResponse from the API

    Returns:
        List of AddressResultFields, one per result.

    Example:
        >>> response = client.validate_addresses(batch_request)
        >>> for addr in extract_all_results(response):
        ...     print(addr.postal_code, addr.street_name)
    """
    if response is None:
        return []

    return [extract_from_result(r) for r in response.results]


def extract_geo_location(
    validated_address: Optional[ValidatedAddress],
) -> GeoLocation:
    """Extract geo-location coordinates from a ValidatedAddress.

    Available when ``include_default_geo_location`` was enabled during
    validation.

    Args:
        validated_address: A ValidatedAddress that may contain geo data

    Returns:
        GeoLocation with ``latitude`` and ``longitude`` as strings, or
        ``None`` if unavailable.

    Example:
        >>> addr = result.first_result.first_validated_address
        >>> geo = extract_geo_location(addr)
        >>> geo.latitude, geo.longitude
        ('51.207968', '4.227349')
    """
    if validated_address is None or validated_address.service_point_detail is None:
        return GeoLocation()

    geo_info = validated_address.service_point_detail.geographical_location_info
    if geo_info is None or geo_info.geographical_location is None:
        return GeoLocation()

    geo = geo_info.geographical_location
    return GeoLocation(
        latitude=geo.latitude.value if geo.latitude else None,
        longitude=geo.longitude.value if geo.longitude else None,
    )


def extract_nis_code(
    validated_address: Optional[ValidatedAddress],
) -> NisCodeInfo:
    """Extract the NIS code from a ValidatedAddress.

    Available when ``include_nis_code`` was enabled during validation.

    Args:
        validated_address: A ValidatedAddress that may contain NIS data

    Returns:
        NisCodeInfo with ``level`` and ``value``, or ``None`` values if
        unavailable.

    Example:
        >>> addr = result.first_result.first_validated_address
        >>> nis = extract_nis_code(addr)
        >>> nis.level, nis.value
        ('9', '46003A242')
    """
    if validated_address is None or validated_address.nis_code is None:
        return NisCodeInfo()

    return validated_address.nis_code


def extract_nis_hierarchy(
    validated_address: Optional[ValidatedAddress],
) -> List[NisHierarchyEntry]:
    """Extract the NIS hierarchy from a ValidatedAddress.

    Available when ``include_nis_hierarchy`` was enabled during validation.
    Returns levels from most specific (e.g. neighborhood) to broadest
    (e.g. region), as ordered by the API.

    Args:
        validated_address: A ValidatedAddress that may contain NIS hierarchy

    Returns:
        List of NisHierarchyEntry, each with ``level``, ``value``, and
        ``names`` (a tuple of LocalizedName).

    Example:
        >>> addr = result.first_result.first_validated_address
        >>> for entry in extract_nis_hierarchy(addr):
        ...     print(entry.level, entry.value, entry.names)
        9 46003A242 (LocalizedName(body='HEIDE', locale='nl'),)
    """
    if (
        validated_address is None
        or validated_address.nis_hierarchy is None
        or not validated_address.nis_hierarchy.nis_hierarchy_result
    ):
        return []

    entries: List[NisHierarchyEntry] = []
    for item in validated_address.nis_hierarchy.nis_hierarchy_result:
        entry = NisHierarchyEntry(
            level=item.nis_code.level if item.nis_code else None,
            value=item.nis_code.value if item.nis_code else None,
            names=tuple(
                LocalizedName(body=n.body, locale=n.locale)
                for n in item.nis_name
            ),
        )
        entries.append(entry)

    return entries


def _extract_service_point_identifiers(
    items: List[ServicePointResultItem],
) -> List[str]:
    """Return box_number or detail_number from a list of result items."""
    result: List[str] = []
    for item in items:
        identifier = item.box_number or item.detail_number
        if identifier is not None:
            result.append(identifier)
    return result


def extract_box_list(
    validated_address: Optional[ValidatedAddress],
) -> List[str]:
    """Extract the list of box numbers from a ValidatedAddress.

    Available when ``include_list_of_boxes`` was enabled during validation.

    Args:
        validated_address: A ValidatedAddress that may contain box data

    Returns:
        List of box number strings, or an empty list if unavailable.

    Example:
        >>> addr = result.first_result.first_validated_address
        >>> extract_box_list(addr)
        ['1', '2', '6', '4', '5', '3']
    """
    if validated_address is None or validated_address.service_point_box_list is None:
        return []

    return _extract_service_point_identifiers(
        validated_address.service_point_box_list.service_point_box_result
    )


def extract_suffix_list(
    validated_address: Optional[ValidatedAddress],
) -> List[str]:
    """Extract the list of suffix numbers from a ValidatedAddress.

    Available when ``include_suffix_list`` was enabled during validation.

    Args:
        validated_address: A ValidatedAddress that may contain suffix data

    Returns:
        List of suffix/detail number strings, or an empty list if unavailable.

    Example:
        >>> addr = result.first_result.first_validated_address
        >>> extract_suffix_list(addr)
        ['21', '27', '33', '37', '39']
    """
    if validated_address is None or validated_address.service_point_suffix_list is None:
        return []

    return _extract_service_point_identifiers(
        validated_address.service_point_suffix_list.service_point_suffix_result
    )


def extract_submitted_address_lines(
    result: Optional[ValidatedAddressResult],
) -> List[str]:
    """Extract formatted submitted address lines from a ValidatedAddressResult.

    Available when ``include_submitted_address`` was enabled during validation.
    This returns the original submitted address as formatted by bpost, which
    may differ from the validated/corrected address.

    Args:
        result: A ValidatedAddressResult from the API response

    Returns:
        List of formatted submitted address line strings, or an empty list
        if unavailable.

    Example:
        >>> info = response.first_result
        >>> extract_submitted_address_lines(info)
        ['BOERENSTRAAT 1', '9120 BEVEREN']
    """
    if result is None or result.formatted_submitted_address is None:
        return []

    return result.formatted_submitted_address.line
