### bpost-address-validator

This is a lightweight Python wrapper for bpost’s External Mailing Address Proofing API endpoint `POST /roa-info-st/externalMailingAddressProofingRest/validateAddresses`.

It provides:
- Synchronous and asynchronous clients powered by `httpx`
- Pydantic v2 models for request/response envelopes (flexible inner structure; extra fields allowed)
- A simple, typed interface and explicit error handling via `ApiError`


#### Features
- Sync client: `BpostClient`
- Async client: `AsyncBpostClient`
- Automatic `x-api-key` header handling
- Default base URL pointing to bpost NP environment
- Uniform error type `ApiError` for transport and non-200 responses


#### Requirements
- Python 3.12+


#### Installation
```bash
pip install bpost-address-validator
```

From source (editable):
```bash
pip install -e .
```


#### Quick start (sync)
```python
from bpost_address_validator import (
    BpostClient,
    ValidateAddressesRequest,
    ValidateAddressesRequestContent,
    AddressToValidateList,
    AddressToValidate,
    ValidateAddressOptions,
    PostalAddress,
    DeliveryPointLocation,
    StructuredDeliveryPointLocation,
    PostalCodeMunicipality,
    StructuredPostalCodeMunicipality,
)

req = ValidateAddressesRequest(
    validate_addresses_request=ValidateAddressesRequestContent(
        address_to_validate_list=AddressToValidateList(
            address_to_validate=[
                AddressToValidate(
                    id="1",
                    dispatching_country_iso_code="BE",
                    delivering_country_iso_code="BE",
                    # Provide either address_block_lines or a structured postal_address
                    postal_address=PostalAddress(
                        delivery_point_location=DeliveryPointLocation(
                            structured_delivery_point_location=StructuredDeliveryPointLocation(
                                street_name="Muntstraat",
                                street_number="1",
                            )
                        ),
                        postal_code_municipality=PostalCodeMunicipality(
                            structured_postal_code_municipality=StructuredPostalCodeMunicipality(
                                postal_code="1000",
                                municipality_name="Bruxelles",
                            )
                        ),
                    ),
                )
            ]
        ),
        validate_address_options=ValidateAddressOptions(
            include_submitted_address=True,
            include_suggestions=True,
            include_formatting=True,
        ),
    )
)

with BpostClient(api_key="<YOUR_API_KEY>") as client:
    resp = client.validate_addresses(req)
    print(resp.model_dump())
```


#### Quick start (async)
```python
import asyncio
from bpost_address_validator import (
    AsyncBpostClient,
    ValidateAddressesRequest,
    ValidateAddressesRequestContent,
    AddressToValidateList,
    AddressToValidate,
)

async def main():
    req = ValidateAddressesRequest(
        validate_addresses_request=ValidateAddressesRequestContent(
            address_to_validate_list=AddressToValidateList(
                address_to_validate=[
                    AddressToValidate(
                        id="1",
                        dispatching_country_iso_code="BE",
                        delivering_country_iso_code="BE",
                    )
                ]
            )
        )
    )
    async with AsyncBpostClient(api_key="<YOUR_API_KEY>") as client:
        resp = await client.validate_addresses(req)
        print(resp.model_dump())

asyncio.run(main())
```


#### Using the typed address models
```python
from bpost_address_validator import (
    BpostClient,
    ValidateAddressesRequest,
    ValidateAddressesRequestContent,
    AddressToValidateList,
    AddressToValidate,
    ValidateAddressOptions,
    AddressBlockLines,
    UnstructuredAddressLineItem,
    PostalAddress,
    DeliveryPointLocation,
    StructuredDeliveryPointLocation,
    PostalCodeMunicipality,
    StructuredPostalCodeMunicipality,
)

req = ValidateAddressesRequest(
    validate_addresses_request=ValidateAddressesRequestContent(
        address_to_validate_list=AddressToValidateList(
            address_to_validate=[
                AddressToValidate(
                    id="1",
                    dispatching_country_iso_code="BE",
                    delivering_country_iso_code="BE",
                    # Option A: unstructured address lines
                    address_block_lines=AddressBlockLines(
                        unstructured_address_line=[
                            UnstructuredAddressLineItem(body="Muntstraat 1", locale="nl")
                        ]
                    ),
                    # Option B: structured postal address (can be used instead of address_block_lines)
                    postal_address=PostalAddress(
                        delivery_point_location=DeliveryPointLocation(
                            structured_delivery_point_location=StructuredDeliveryPointLocation(
                                street_name="Muntstraat", street_number="1"
                            )
                        ),
                        postal_code_municipality=PostalCodeMunicipality(
                            structured_postal_code_municipality=StructuredPostalCodeMunicipality(
                                postal_code="1000", municipality_name="Bruxelles"
                            )
                        ),
                    ),
                )
            ]
        ),
        validate_address_options=ValidateAddressOptions(include_formatting=True),
    )
)

with BpostClient(api_key="<YOUR_API_KEY>") as client:
    resp = client.validate_addresses(req)
    # Access typed response envelope
    print(resp.validate_addresses_response is not None)
```


#### Passing a raw dict payload
```python
from bpost_address_validator import BpostClient

payload = {
    "ValidateAddressesRequest": {
        "AddressToValidateList": {
            "AddressToValidate": [
                {
                    "@id": "1",
                    "DispatchingCountryISOCode": "BE",
                    "DeliveringCountryISOCode": "BE",
                    "PostalAddress": {
                        "DeliveryPointLocation": {
                            "StructuredDeliveryPointLocation": {
                                "StreetName": "Muntstraat",
                                "StreetNumber": "1",
                            }
                        },
                        "PostalCodeMunicipality": {
                            "StructuredPostalCodeMunicipality": {
                                "PostalCode": "1000",
                                "MunicipalityName": "Bruxelles",
                            }
                        },
                    },
                }
            ]
        },
        "ValidateAddressOptions": {"IncludeFormatting": True},
    }
}

with BpostClient(api_key="<YOUR_API_KEY>") as client:
    resp = client.validate_addresses(payload)
    print(resp.validate_addresses_response is not None)
```


#### API overview
- Clients
  - `BpostClient(api_key: str, base_url: str = DEFAULT, timeout: float | None = 30.0)`
    - `validate_addresses(payload) -> ValidateAddressesResponse`
  - `AsyncBpostClient(api_key: str, base_url: str = DEFAULT, timeout: float | None = 30.0)`
    - `await validate_addresses(payload) -> ValidateAddressesResponse`

- Models (selected)
  - `ValidateAddressesRequest`
  - `ValidateAddressesRequestContent`
  - `AddressToValidateList`
  - `AddressToValidate`
  - `AddressBlockLines`, `UnstructuredAddressLineItem`
  - `PostalAddress`, `DeliveryPointLocation`, `StructuredDeliveryPointLocation`
  - `PostalCodeMunicipality`, `StructuredPostalCodeMunicipality`
  - `ValidateAddressOptions`
  - `ValidateAddressesResponse`

- Errors
  - `ApiError` — for transport errors and non-200 responses. Inspect `status_code` and `details` for context.


#### Request/Response envelopes
- Request body root: `{"ValidateAddressesRequest": {...}}`
- Response body root: `{"ValidateAddressesResponse": {...}}`

Models allow extra fields to preserve forward-compatibility with upstream changes. See `externalMailaddressProofingAPI-OpenAPIspec_v3.yaml` for the full schema reference.


#### Environments and base URL
- Default base URL (NP): `https://api.mailops-np.bpost.cloud`
- Endpoint path: `/roa-info-st/externalMailingAddressProofingRest/validateAddresses`
You can override the base URL in the client constructor.


#### Error handling
- Transport issues raise `ApiError("HTTP transport error")`.
- Non-200 responses raise `ApiError` with `status_code` and parsed `details` (JSON when available).

Example:
```python
from bpost_address_validator import BpostClient, ApiError

try:
    with BpostClient(api_key="bad-key") as client:
        client.validate_addresses({"ValidateAddressesRequest": {}})
except ApiError as e:
    print(e.status_code, e.details)
```


#### Authentication
Provide your API key via the `api_key` parameter. It is sent as `x-api-key` automatically.


#### Typing strategy
- Pydantic v2 models are used for the outer envelopes and key nested structures.
- Public attributes are Pythonic snake_case; JSON aliases match the API (e.g., `dispatching_country_iso_code` -> `DispatchingCountryISOCode`).
- Typed models are provided for `address_block_lines` and `postal_address` structures (including delivery point location and postal code/municipality).
- Extra keys are allowed across models to avoid breakage if bpost adds new fields.
- For attributes like `"@id"`, the models expose proper field aliases (e.g., `Field(alias="@id")`).


#### Development
- Python 3.12+
- Runtime deps: `httpx>=0.27.0`, `pydantic>=2.7.0`
- No tests yet — PRs welcome (tests and deeper typed models).


#### License
MIT — see `LICENSE` if provided, otherwise follow repository policy.


#### Disclaimer
This project is not affiliated with or endorsed by bpost. Use at your own risk and comply with bpost’s terms.