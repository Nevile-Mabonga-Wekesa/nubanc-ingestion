from typing import List
from contracts.events.envelope import CanonicalEvent


class VendorTranslator:
    vendor: str

    def translate(self, *, tenant_id: str, vendor_version: str, payload: dict) -> List[CanonicalEvent]:
        raise NotImplementedError


_TRANSLATORS = {}


def register(translator: VendorTranslator):
    _TRANSLATORS[translator.vendor] = translator


def get_translator(vendor: str) -> VendorTranslator:
    if vendor not in _TRANSLATORS:
        raise KeyError(f"Unsupported vendor: {vendor}")
    return _TRANSLATORS[vendor]
