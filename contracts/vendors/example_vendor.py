from typing import List
from contracts.api.events.envelope import CanonicalEvent
from contracts.api.vendors.registry import register, VendorTranslator


class ExampleVendorTranslator(VendorTranslator):
    vendor = "example"

    def translate(self, *, tenant_id: str, vendor_version: str, payload: dict) -> List[CanonicalEvent]:
        # Structural validation only (no domain rules)
        if "records" not in payload or not isinstance(payload["records"], list):
            raise ValueError("Invalid payload: missing 'records' list")

        events = []
        for rec in payload["records"]:
            events.append(
                CanonicalEvent(
                    event_type="vendor.record.received.v1",
                    tenant_id=tenant_id,
                    vendor=self.vendor,
                    vendor_version=vendor_version,
                    payload=rec,
                )
            )
        return events


register(ExampleVendorTranslator())
