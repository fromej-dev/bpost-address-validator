from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, ConfigDict


# General modeling approach:
# - Mirror the top-level envelopes exactly as exposed by the API
# - Keep inner structures flexible (extra = "allow") so the client remains
#   resilient to minor upstream changes without requiring immediate updates.


class _FlexibleModel(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)


# ----
# Request typing additions: AddressBlockLines and PostalAddress structures
# ----

class UnstructuredAddressLineItem(_FlexibleModel):
    body: Optional[str] = Field(default=None, alias="*body")
    locale: Optional[str] = Field(default=None, alias="@locale")


class AddressBlockLines(_FlexibleModel):
    unstructured_address_line: List[UnstructuredAddressLineItem] = Field(
        default_factory=list, alias="UnstructuredAddressLine"
    )


class StructuredDeliveryPointLocation(_FlexibleModel):
    street_name: Optional[str] = Field(default=None, alias="StreetName")
    box_number: Optional[str] = Field(default=None, alias="BoxNumber")
    street_number: Optional[str] = Field(default=None, alias="StreetNumber")
    country_name: Optional[str] = Field(default=None, alias="CountryName")


class DeliveryPointLocation(_FlexibleModel):
    unstructured_delivery_point_location: Optional[str] = Field(
        default=None, alias="UnstructuredDeliveryPointLocation"
    )
    structured_delivery_point_location: Optional[StructuredDeliveryPointLocation] = Field(
        default=None, alias="StructuredDeliveryPointLocation"
    )


class StructuredPostalCodeMunicipality(_FlexibleModel):
    postal_code: Optional[str] = Field(default=None, alias="PostalCode")
    municipality_name: Optional[str] = Field(default=None, alias="MunicipalityName")
    delivery_service_qualifier: Optional[str] = Field(
        default=None, alias="DeliveryServiceQualifier"
    )


class PostalCodeMunicipality(_FlexibleModel):
    unstructured_postal_code_municipality: Optional[str] = Field(
        default=None, alias="UnstructuredPostalCodeMunicipality"
    )
    structured_postal_code_municipality: Optional[StructuredPostalCodeMunicipality] = Field(
        default=None, alias="StructuredPostalCodeMunicipality"
    )


class StructuredOtherDeliveryInformation(_FlexibleModel):
    delivery_service_type: Optional[str] = Field(
        default=None, alias="DeliveryServiceType"
    )
    delivery_service_indicator: Optional[str] = Field(
        default=None, alias="DeliveryServiceIndicator"
    )


class OtherDeliveryInformation(_FlexibleModel):
    unstructured_other_delivery_information: Optional[str] = Field(
        default=None, alias="UnstructuredOtherDeliveryInformation"
    )
    structured_other_delivery_information: Optional[StructuredOtherDeliveryInformation] = Field(
        default=None, alias="StructuredOtherDeliveryInformation"
    )


class PostalAddress(_FlexibleModel):
    # Request-style nested groups
    delivery_point_location: Optional[DeliveryPointLocation] = Field(
        default=None, alias="DeliveryPointLocation"
    )
    postal_code_municipality: Optional[PostalCodeMunicipality] = Field(
        default=None, alias="PostalCodeMunicipality"
    )
    other_delivery_information: Optional[OtherDeliveryInformation] = Field(
        default=None, alias="OtherDeliveryInformation"
    )

    # Response-style direct structured fields (sometimes flattened)
    country_name: Optional[str] = Field(default=None, alias="CountryName")
    structured_delivery_point_location: Optional[StructuredDeliveryPointLocation] = Field(
        default=None, alias="StructuredDeliveryPointLocation"
    )
    structured_postal_code_municipality: Optional[StructuredPostalCodeMunicipality] = Field(
        default=None, alias="StructuredPostalCodeMunicipality"
    )
    structured_other_delivery_information: Optional[StructuredOtherDeliveryInformation] = Field(
        default=None, alias="StructuredOtherDeliveryInformation"
    )


class AddressToValidate(_FlexibleModel):
    id: Optional[str] = Field(default=None, alias="@id")
    dispatching_country_iso_code: Optional[str] = Field(
        default=None, alias="DispatchingCountryISOCode"
    )
    delivering_country_iso_code: Optional[str] = Field(
        default=None, alias="DeliveringCountryISOCode"
    )
    address_block_lines: Optional[AddressBlockLines] = Field(
        default=None, alias="AddressBlockLines"
    )
    postal_address: Optional[PostalAddress] = Field(default=None, alias="PostalAddress")
    mailee_and_addressee: Optional[Dict[str, Any]] = Field(
        default=None, alias="MaileeAndAddressee"
    )


class AddressToValidateList(_FlexibleModel):
    address_to_validate: List[AddressToValidate] = Field(alias="AddressToValidate")


class ValidateAddressOptions(_FlexibleModel):
    include_submitted_address: Optional[bool] = Field(
        default=None, alias="IncludeSubmittedAddress"
    )
    include_default_geo_location: Optional[bool] = Field(
        default=None, alias="IncludeDefaultGeoLocation"
    )
    include_suggestions: Optional[bool] = Field(default=None, alias="IncludeSuggestions")
    include_formatting: Optional[bool] = Field(default=None, alias="IncludeFormatting")
    include_default_geo_location_for_boxes: Optional[bool] = Field(
        default=None, alias="IncludeDefaultGeoLocationForBoxes"
    )
    include_suffix_list: Optional[bool] = Field(default=None, alias="IncludeSuffixList")
    include_number_of_boxes: Optional[bool] = Field(
        default=None, alias="IncludeNumberOfBoxes"
    )
    include_number_of_suffixes: Optional[bool] = Field(
        default=None, alias="IncludeNumberOfSuffixes"
    )
    include_list_of_boxes: Optional[bool] = Field(
        default=None, alias="IncludeListOfBoxes"
    )
    include_nis_code: Optional[bool] = Field(default=None, alias="IncludeNisCode")
    include_nis_hierarchy: Optional[bool] = Field(
        default=None, alias="IncludeNisHierarchy"
    )
    include_desired_address_language: Optional[str] = Field(
        default=None, alias="IncludeDesiredAddressLanguage"
    )


class CallerIdentification(_FlexibleModel):
    caller_name: Optional[str] = Field(default=None, alias="CallerName")


class ValidateAddressesRequestContent(_FlexibleModel):
    address_to_validate_list: AddressToValidateList = Field(
        alias="AddressToValidateList"
    )
    validate_address_options: Optional[ValidateAddressOptions] = Field(
        default=None, alias="ValidateAddressOptions"
    )
    caller_identification: Optional[CallerIdentification] = Field(
        default=None, alias="CallerIdentification"
    )


class ValidateAddressesRequest(_FlexibleModel):
    """Top-level request body wrapper required by the API."""

    validate_addresses_request: ValidateAddressesRequestContent = Field(
        alias="ValidateAddressesRequest"
    )


# Response models (kept flexible, but with helpful typed anchors)


# -- Geo-location models --

class GeoCoordinate(_FlexibleModel):
    value: Optional[str] = Field(default=None, alias="Value")
    coordinate_type: Optional[str] = Field(default=None, alias="CoordinateType")


class GeographicalLocation(_FlexibleModel):
    latitude: Optional[GeoCoordinate] = Field(default=None, alias="Latitude")
    longitude: Optional[GeoCoordinate] = Field(default=None, alias="Longitude")


class GeographicalLocationInfo(_FlexibleModel):
    geographical_location: Optional[GeographicalLocation] = Field(
        default=None, alias="GeographicalLocation"
    )


class ServicePointDetailInfo(_FlexibleModel):
    geographical_location_info: Optional[GeographicalLocationInfo] = Field(
        default=None, alias="GeographicalLocationInfo"
    )


# -- NIS models --

class NisCodeInfo(_FlexibleModel):
    level: Optional[str] = Field(default=None, alias="Level")
    value: Optional[str] = Field(default=None, alias="Value")


class NisNameItem(_FlexibleModel):
    body: Optional[str] = Field(default=None)
    locale: Optional[str] = Field(default=None)


class NisHierarchyResultItem(_FlexibleModel):
    nis_code: Optional[NisCodeInfo] = Field(default=None, alias="NisCode")
    nis_name: List[NisNameItem] = Field(default_factory=list, alias="NisName")


class NisHierarchyInfo(_FlexibleModel):
    nis_hierarchy_result: List[NisHierarchyResultItem] = Field(
        default_factory=list, alias="NisHierarchyResult"
    )


# -- Service point result models --

class ServicePointResultItem(_FlexibleModel):
    box_number: Optional[str] = Field(default=None, alias="BoxNumber")
    detail_number: Optional[str] = Field(default=None, alias="DetailNumber")


class ServicePointBoxListInfo(_FlexibleModel):
    service_point_box_result: List[ServicePointResultItem] = Field(
        default_factory=list, alias="ServicePointBoxResult"
    )


class ServicePointSuffixListInfo(_FlexibleModel):
    service_point_suffix_result: List[ServicePointResultItem] = Field(
        default_factory=list, alias="ServicePointSuffixResult"
    )


# -- Formatted address (label / submitted address) --

class FormattedAddress(_FlexibleModel):
    line: List[str] = Field(default_factory=list, alias="Line")


class ValidatedAddress(_FlexibleModel):
    postal_address: Optional[PostalAddress] = Field(default=None, alias="PostalAddress")
    address_language: Optional[str] = Field(default=None, alias="AddressLanguage")
    score: Optional[str] = Field(default=None, alias="Score")
    number_of_suffix: Optional[str] = Field(default=None, alias="NumberOfSuffix")
    number_of_boxes: Optional[str] = Field(default=None, alias="NumberOfBoxes")
    label: Optional[Dict[str, Any]] = Field(default=None, alias="Label")
    service_point_box_list: Optional[ServicePointBoxListInfo] = Field(
        default=None, alias="ServicePointBoxList"
    )
    service_point_detail: Optional[ServicePointDetailInfo] = Field(
        default=None, alias="ServicePointDetail"
    )
    service_point_suffix_list: Optional[ServicePointSuffixListInfo] = Field(
        default=None, alias="ServicePointSuffixList"
    )
    nis_code: Optional[NisCodeInfo] = Field(default=None, alias="NisCode")
    nis_hierarchy: Optional[NisHierarchyInfo] = Field(default=None, alias="NisHierarchy")


class ValidatedAddressList(_FlexibleModel):
    validated_address: List[ValidatedAddress] = Field(
        default_factory=list, alias="ValidatedAddress"
    )


class ValidatedAddressResult(_FlexibleModel):
    validated_address_list: Optional[ValidatedAddressList] = Field(
        default=None, alias="ValidatedAddressList"
    )
    mailee_and_addressee: Optional[Dict[str, Any]] = Field(
        default=None, alias="MaileeAndAddressee"
    )
    id: Optional[str] = Field(default=None, alias="@id")
    error: Optional[List[ValidationErrorItem]] = Field(default_factory=list, alias="Error")
    detected_input_address_language: Optional[str] = Field(
        default=None, alias="DetectedInputAddressLanguage"
    )
    transaction_id: Optional[str] = Field(default=None, alias="TransactionID")
    formatted_submitted_address: Optional[FormattedAddress] = Field(
        default=None, alias="FormattedSubmittedAddress"
    )

    @property
    def is_valid(self) -> bool:
        """Check if the address validation was successful.

        Returns:
            True if there are validated addresses and no errors, False otherwise
        """
        has_results = bool(
            self.validated_address_list
            and self.validated_address_list.validated_address
        )
        has_errors = bool(self.error)
        return has_results and not has_errors

    @property
    def errors(self) -> List[ValidationErrorItem]:
        """Get the list of validation errors.

        Returns:
            List of ValidationErrorItem objects (empty list if no errors)
        """
        return self.error if self.error else []

    @property
    def validated_addresses(self) -> List[ValidatedAddress]:
        """Get the list of validated addresses.

        Returns:
            List of ValidatedAddress objects (empty list if none)
        """
        if self.validated_address_list:
            return self.validated_address_list.validated_address
        return []

    @property
    def first_validated_address(self) -> Optional[ValidatedAddress]:
        """Get the first validated address.

        Returns:
            First ValidatedAddress or None if no addresses
        """
        addresses = self.validated_addresses
        return addresses[0] if addresses else None

    @property
    def score(self) -> Optional[str]:
        """Get the validation score of the first validated address.

        Returns:
            Score string or None if no addresses
        """
        addr = self.first_validated_address
        return addr.score if addr else None


# ----
# Validation messages (Errors and Warnings)
# The official manual indicates both functional warnings and errors are returned
# and tied to impacted components. Because the exact upstream field names can
# vary, we keep models flexible while providing helpful, typed anchors.
# ----


class ValidationErrorItem(_FlexibleModel):
    component_ref: str = Field(alias="ComponentRef")
    error_code: Optional[str] = Field(default=None, alias="ErrorCode")
    error_severity: Optional[str] = Field(default=None, alias="ErrorSeverity")


# Rebuild to resolve forward refs for Pydantic v2
ValidatedAddressResult.model_rebuild()


class ValidatedAddressResultList(_FlexibleModel):
    validated_address_result: List[ValidatedAddressResult] = Field(
        default_factory=list, alias="ValidatedAddressResult"
    )


class ValidateAddressesResponseContent(_FlexibleModel):
    validated_address_result_list: Optional[ValidatedAddressResultList] = Field(
        default=None, alias="ValidatedAddressResultList"
    )


class ValidateAddressesResponse(_FlexibleModel):
    """Top-level response body wrapper returned by the API."""

    validate_addresses_response: Optional[ValidateAddressesResponseContent] = Field(
        default=None, alias="ValidateAddressesResponse"
    )

    @property
    def results(self) -> List[ValidatedAddressResult]:
        """Convenience property to access validated address results.

        Returns:
            List of ValidatedAddressResult objects (empty list if none)
        """
        if (
            self.validate_addresses_response
            and self.validate_addresses_response.validated_address_result_list
        ):
            return self.validate_addresses_response.validated_address_result_list.validated_address_result
        return []

    @property
    def first_result(self) -> Optional[ValidatedAddressResult]:
        """Convenience property to access the first validated address result.

        Returns:
            First ValidatedAddressResult or None if no results
        """
        results = self.results
        return results[0] if results else None


# ----
# Extraction result types
# Frozen dataclasses used as typed return values from extraction helpers.
# These provide attribute access and IDE autocompletion for extracted data.
# ----


@dataclass(frozen=True)
class AddressFields:
    """Flat address fields extracted from a PostalAddress."""

    street_name: Optional[str] = None
    street_number: Optional[str] = None
    box_number: Optional[str] = None
    postal_code: Optional[str] = None
    municipality_name: Optional[str] = None
    country_name: Optional[str] = None
    delivery_service_qualifier: Optional[str] = None


@dataclass(frozen=True)
class ValidatedAddressFields(AddressFields):
    """Address fields with validation metadata from a ValidatedAddress."""

    score: Optional[str] = None
    address_language: Optional[str] = None
    number_of_boxes: Optional[str] = None
    number_of_suffix: Optional[str] = None


@dataclass(frozen=True)
class AddressResultFields(ValidatedAddressFields):
    """Address fields from a ValidatedAddressResult (includes id)."""

    id: Optional[str] = None
    is_valid: bool = False
    errors: tuple[ValidationErrorItem, ...] = ()
    transaction_id: Optional[str] = None
    detected_input_address_language: Optional[str] = None
    label_lines: tuple[str, ...] = ()
    submitted_address_lines: tuple[str, ...] = ()


@dataclass(frozen=True)
class GeoLocation:
    """Geographic coordinates extracted from a ValidatedAddress."""

    latitude: Optional[str] = None
    longitude: Optional[str] = None


@dataclass(frozen=True)
class LocalizedName:
    """A name with its locale."""

    body: Optional[str] = None
    locale: Optional[str] = None


@dataclass(frozen=True)
class NisHierarchyEntry:
    """A single entry in the NIS administrative hierarchy."""

    level: Optional[str] = None
    value: Optional[str] = None
    names: tuple[LocalizedName, ...] = ()


@dataclass(frozen=True)
class ServicePointNumbers:
    """Box numbers and detail numbers extracted from a service point list."""

    box_numbers: tuple[str, ...] = ()
    detail_numbers: tuple[str, ...] = ()
