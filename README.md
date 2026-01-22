### bpost-address-validator

This is a lightweight Python wrapper for bpost's External Mailing Address Proofing API endpoint `POST /<env>/externalMailingAddressProofingRest/validateAddresses`.

Environments have different base URLs and path prefixes. Presets are provided for convenience:

- prod: `https://api.mailops.bpost.cloud/roa-info/...`
- test (NP): `https://api.mailops-np.bpost.cloud/roa-info-st2/...`
- uat (NP): `https://api.mailops-np.bpost.cloud/roa-info-ac/...`

It provides:
- Synchronous and asynchronous clients powered by `httpx`
- Pydantic v2 models for request/response envelopes (flexible inner structure; extra fields allowed)
- A simple, typed interface and explicit error handling via `ApiError`
- **NEW**: Convenience functions for simple address validation without complex model construction
- **NEW**: Factory functions for easy model creation
- **NEW**: Validation option presets
- **NEW**: Response helper properties for easier result access


#### Features
- Sync client: `BpostClient`
- Async client: `AsyncBpostClient`
- Automatic `x-api-key` header handling
- Default base URL pointing to bpost NP environment (you should usually provide a preset explicitly)
- Uniform error type `ApiError` for transport and non-200 responses
- Connection pool configuration for high-throughput scenarios
- Simple convenience methods: `validate_address_simple()`, `validate_addresses_batch()`
- Factory functions: `create_structured_address()`, `create_simple_request()`, etc.
- Validation presets: `ValidationPresets.FULL`, `ValidationPresets.WITH_SUGGESTIONS`, etc.
- Response helpers: `response.results`, `result.is_valid`, `result.score`, etc.


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


#### Quick start (simple API)

The simplest way to validate an address:

```python
from bpost_address_validator import BpostClient

with BpostClient(api_key="<YOUR_API_KEY>", preset="test") as client:
    # Validate a single address with simple parameters
    response = client.validate_address_simple(
        street_name="Muntstraat",
        street_number="1",
        postal_code="1000",
        municipality_name="Bruxelles"
    )

    # Easy access to results
    if response.first_result and response.first_result.is_valid:
        print(f"Valid! Score: {response.first_result.score}")
    else:
        print(f"Errors: {response.first_result.errors}")
```


#### Quick start (batch validation)

Validate multiple addresses at once:

```python
from bpost_address_validator import BpostClient

addresses = [
    {
        "street_name": "Muntstraat",
        "street_number": "1",
        "postal_code": "1000",
        "municipality_name": "Bruxelles"
    },
    {
        "address_lines": ["Rue de la Loi 16", "1000 Bruxelles"]
    }
]

with BpostClient(api_key="<YOUR_API_KEY>", preset="test") as client:
    response = client.validate_addresses_batch(addresses)

    for result in response.results:
        print(f"ID: {result.id}, Valid: {result.is_valid}, Score: {result.score}")
```


#### Quick start (with validation presets)

Use predefined validation option presets:

```python
from bpost_address_validator import BpostClient, ValidationPresets

with BpostClient(api_key="<YOUR_API_KEY>", preset="test") as client:
    response = client.validate_address_simple(
        street_name="Muntstraat",
        street_number="1",
        postal_code="1000",
        municipality_name="Bruxelles",
        options=ValidationPresets.FULL  # All validation options enabled
    )
    print(response.model_dump())
```

Available presets:
- `ValidationPresets.BASIC` - Minimal validation
- `ValidationPresets.FULL` - All validation options enabled
- `ValidationPresets.WITH_SUGGESTIONS` - Include address suggestions
- `ValidationPresets.WITH_FORMATTING` - Include formatting information
- `ValidationPresets.WITH_GEO` - Include geo-location data


#### Quick start (factory functions)

Use factory functions for easy model creation:

```python
from bpost_address_validator import (
    BpostClient,
    create_structured_address,
    create_address_to_validate,
    create_simple_request,
    ValidationPresets,
)

# Create a structured address
address = create_structured_address(
    street_name="Muntstraat",
    street_number="1",
    postal_code="1000",
    municipality_name="Bruxelles"
)

# Create an address to validate
addr_to_validate = create_address_to_validate(
    id="1",
    street_name="Muntstraat",
    street_number="1",
    postal_code="1000",
    municipality_name="Bruxelles"
)

# Create a complete request
request = create_simple_request([addr_to_validate], ValidationPresets.FULL)

with BpostClient(api_key="<YOUR_API_KEY>", preset="test") as client:
    response = client.validate_addresses(request)
    print(response.model_dump())
```


#### Quick start (traditional sync API)

The traditional way using full model construction:

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

with BpostClient(api_key="<YOUR_API_KEY>", preset="test") as client:
    resp = client.validate_addresses(req)
    print(resp.model_dump())
```


#### Quick start (async)

All convenience methods are also available in async:

```python
import asyncio
from bpost_address_validator import AsyncBpostClient, ValidationPresets

async def main():
    async with AsyncBpostClient(api_key="<YOUR_API_KEY>", preset="test") as client:
        # Simple validation
        response = await client.validate_address_simple(
            street_name="Muntstraat",
            street_number="1",
            postal_code="1000",
            municipality_name="Bruxelles",
            options=ValidationPresets.WITH_SUGGESTIONS
        )

        if response.first_result and response.first_result.is_valid:
            print(f"Valid! Score: {response.first_result.score}")

asyncio.run(main())
```


#### Environment configuration

You can configure the target environment in three ways:

1) Use a preset (recommended):

```python
# prod
BpostClient(api_key="...", preset="prod")

# test (NP, st2)
BpostClient(api_key="...", preset="test")

# uat (NP, ac)
BpostClient(api_key="...", preset="uat")
```

2) Manually set base URL and path prefix:

```python
# Equivalent to preset="prod"
BpostClient(
    api_key="...",
    base_url="https://api.mailops.bpost.cloud",
    environment="roa-info",
)

# Equivalent to preset="test"
BpostClient(
    api_key="...",
    base_url="https://api.mailops-np.bpost.cloud",
    environment="roa-info-st2",
)

# Equivalent to preset="uat"
BpostClient(
    api_key="...",
    base_url="https://api.mailops-np.bpost.cloud",
    environment="roa-info-ac",
)
```

3) Advanced: Provide your own `httpx` client with custom base URL and headers. In that case, pass `client=` to the constructor and omit `api_key` or headers accordingly.


#### Performance tuning (high-throughput scenarios)

Configure connection pool settings for high-volume usage:

```python
from bpost_address_validator import BpostClient

with BpostClient(
    api_key="<YOUR_API_KEY>",
    preset="test",
    max_connections=200,  # Max total connections (default: 100)
    max_keepalive_connections=50,  # Max keep-alive connections (default: 20)
    timeout=60.0,  # Request timeout in seconds (default: 30.0)
) as client:
    # Your high-volume validation code here
    pass
```


#### Using response helper properties

Response and result objects have convenient helper properties:

```python
from bpost_address_validator import BpostClient

with BpostClient(api_key="<YOUR_API_KEY>", preset="test") as client:
    response = client.validate_address_simple(
        street_name="Muntstraat",
        street_number="1",
        postal_code="1000",
        municipality_name="Bruxelles"
    )

    # Access results easily
    print(f"Total results: {len(response.results)}")

    # Get first result
    result = response.first_result
    if result:
        # Check validity
        print(f"Is valid: {result.is_valid}")

        # Get score
        print(f"Score: {result.score}")

        # Get errors
        print(f"Errors: {result.errors}")

        # Get validated addresses
        for addr in result.validated_addresses:
            print(f"Address: {addr.postal_address}")
```


#### Passing a raw dict payload

You can still use raw dict payloads if needed:

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

with BpostClient(api_key="<YOUR_API_KEY>", preset="test") as client:
    resp = client.validate_addresses(payload)
    print(resp.validate_addresses_response is not None)
```


#### API overview

**Clients:**
- `BpostClient(api_key, preset="test", timeout=30.0, max_connections=100, max_keepalive_connections=20)`
  - `validate_addresses(payload)` → ValidateAddressesResponse
  - `validate_address_simple(...)` → ValidateAddressesResponse
  - `validate_addresses_batch(addresses, ...)` → ValidateAddressesResponse
- `AsyncBpostClient(...)` - Same methods but async

**Convenience Functions:**
- `create_structured_address(street_name, street_number, postal_code, municipality_name, ...)`
- `create_unstructured_address(address_lines, locale="nl")`
- `create_address_to_validate(id, street_name, ..., OR address_lines, ...)`
- `create_simple_request(addresses, options=None)`
- `create_batch_request(addresses, dispatching_country="BE", ...)`

**Validation Presets:**
- `ValidationPresets.BASIC` - Minimal validation
- `ValidationPresets.FULL` - All options enabled
- `ValidationPresets.WITH_SUGGESTIONS` - Include suggestions
- `ValidationPresets.WITH_FORMATTING` - Include formatting
- `ValidationPresets.WITH_GEO` - Include geo-location

**Response Helpers:**
- `ValidateAddressesResponse.results` - List of all results
- `ValidateAddressesResponse.first_result` - First result (or None)
- `ValidatedAddressResult.is_valid` - Boolean validity check
- `ValidatedAddressResult.errors` - List of errors
- `ValidatedAddressResult.validated_addresses` - List of validated addresses
- `ValidatedAddressResult.score` - Validation score

**Models (selected):**
- `ValidateAddressesRequest`
- `ValidateAddressesRequestContent`
- `AddressToValidateList`
- `AddressToValidate`
- `AddressBlockLines`, `UnstructuredAddressLineItem`
- `PostalAddress`, `DeliveryPointLocation`, `StructuredDeliveryPointLocation`
- `PostalCodeMunicipality`, `StructuredPostalCodeMunicipality`
- `ValidateAddressOptions`
- `ValidateAddressesResponse`

**Errors:**
- `ApiError` — for transport errors and non-200 responses. Inspect `status_code` and `details` for context.


#### Request/Response envelopes
- Request body root: `{"ValidateAddressesRequest": {...}}`
- Response body root: `{"ValidateAddressesResponse": {...}}`

Models allow extra fields to preserve forward-compatibility with upstream changes. See `externalMailaddressProofingAPI-OpenAPIspec_v3.yaml` for the full schema reference.


#### Error handling
- Transport issues raise `ApiError("HTTP transport error")`.
- Non-200 responses raise `ApiError` with `status_code` and parsed `details` (JSON when available).

Example:
```python
from bpost_address_validator import BpostClient, ApiError

try:
    with BpostClient(api_key="bad-key", preset="test") as client:
        client.validate_addresses({"ValidateAddressesRequest": {}})
except ApiError as e:
    print(e.status_code, e.details)
```


#### Authentication
Provide your API key via the `api_key` parameter. It is sent as `x-api-key` automatically.


#### Typing strategy
- Pydantic v2 models are used for the outer envelopes and key nested structures.
- Public attributes are Pythonic snake_case; JSON aliases match the API (e.g., `dispatching_country_iso_code` → `DispatchingCountryISOCode`).
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
This project is not affiliated with or endorsed by bpost. Use at your own risk and comply with bpost's terms.
