"""Local phone-number parsing and numbering-plan metadata."""

from __future__ import annotations

from dataclasses import dataclass
import unicodedata

import phonenumbers
from phonenumbers import carrier, geocoder, timezone
from phonenumbers.phonenumberutil import NumberParseException


_ALLOWED_INPUT = set("+()-./ ")


@dataclass(frozen=True)
class PhoneDetails:
    valid: bool
    possible: bool
    country_calling_code: str
    region_code: str
    region_name: str
    number_type: str
    time_zones: tuple[str, ...]
    carrier_name: str
    international: str
    national: str
    e164: str


class PhoneInputError(ValueError):
    """A user-facing phone input error."""


def _normalize_digits(value: str) -> str:
    normalized: list[str] = []
    for character in value:
        if character in _ALLOWED_INPUT:
            normalized.append(character)
        elif character.isdecimal():
            normalized.append(str(unicodedata.digit(character)))
        else:
            raise PhoneInputError("لطفاً فقط شماره و نویسه‌های مجاز را وارد کنید.")
    return "".join(normalized).strip()


def _number_type_name(number_type: int) -> str:
    names = {
        phonenumbers.PhoneNumberType.FIXED_LINE: "تلفن ثابت",
        phonenumbers.PhoneNumberType.MOBILE: "تلفن همراه",
        phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE: "ثابت یا همراه",
        phonenumbers.PhoneNumberType.TOLL_FREE: "رایگان",
        phonenumbers.PhoneNumberType.PREMIUM_RATE: "نرخ ویژه",
        phonenumbers.PhoneNumberType.SHARED_COST: "هزینه مشترک",
        phonenumbers.PhoneNumberType.VOIP: "اینترنتی (VoIP)",
        phonenumbers.PhoneNumberType.PERSONAL_NUMBER: "شخصی",
        phonenumbers.PhoneNumberType.PAGER: "پیجر",
        phonenumbers.PhoneNumberType.UAN: "شماره سازمانی",
        phonenumbers.PhoneNumberType.VOICEMAIL: "صندوق صوتی",
        phonenumbers.PhoneNumberType.UNKNOWN: "نامشخص",
    }
    return names.get(number_type, "نامشخص")


def inspect_number(raw_number: str, default_region: str = "IR") -> PhoneDetails:
    """Parse a phone number and return local numbering-plan metadata."""
    normalized = _normalize_digits(raw_number)
    if not normalized:
        raise PhoneInputError("شماره‌ای وارد نشده است.")

    try:
        number = phonenumbers.parse(normalized, default_region.upper())
    except NumberParseException as error:
        if error.error_type == NumberParseException.TOO_SHORT_NSN:
            message = "شماره واردشده کوتاه است."
        elif error.error_type == NumberParseException.NOT_A_NUMBER:
            message = "شماره قابل تشخیص نیست."
        else:
            message = "قالب شماره یا کد کشور را بررسی کنید."
        raise PhoneInputError(message) from error

    possible = phonenumbers.is_possible_number(number)
    valid = phonenumbers.is_valid_number(number)
    region_code = phonenumbers.region_code_for_number(number) or "—"
    region_name = geocoder.description_for_number(number, "fa") or region_code
    carrier_name = carrier.name_for_number(number, "fa") or "در دسترس نیست"

    return PhoneDetails(
        valid=valid,
        possible=possible,
        country_calling_code=f"+{number.country_code}",
        region_code=region_code,
        region_name=region_name,
        number_type=_number_type_name(phonenumbers.number_type(number)),
        time_zones=tuple(timezone.time_zones_for_number(number)),
        carrier_name=carrier_name,
        international=phonenumbers.format_number(
            number, phonenumbers.PhoneNumberFormat.INTERNATIONAL
        ),
        national=phonenumbers.format_number(
            number, phonenumbers.PhoneNumberFormat.NATIONAL
        ),
        e164=phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164),
    )
