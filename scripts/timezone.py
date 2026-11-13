#!/usr/bin/env python3

import argparse
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

TZ_ALIASES = {
    # Asia / Pacific
    "JST": "Asia/Tokyo",
    "KST": "Asia/Seoul",
    "HKT": "Asia/Hong_Kong",
    "SGT": "Asia/Singapore",
    "IST": "Asia/Kolkata",
    "AEST": "Australia/Sydney",
    "AEDT": "Australia/Sydney",
    "NZST": "Pacific/Auckland",
    "NZDT": "Pacific/Auckland",
    # Europe
    "UTC": "UTC",
    "GMT": "Europe/London",
    "BST": "Europe/London",
    "CET": "Europe/Berlin",
    "CEST": "Europe/Berlin",
    "EET": "Europe/Athens",
    "EEST": "Europe/Athens",
    # North America
    "ET": "America/New_York",
    "EST": "America/New_York",
    "EDT": "America/New_York",
    "CT": "America/Chicago",
    "CST": "America/Chicago",
    "CDT": "America/Chicago",
    "MT": "America/Denver",
    "MST": "America/Denver",
    "MDT": "America/Denver",
    "PT": "America/Los_Angeles",
    "PST": "America/Los_Angeles",
    "PDT": "America/Los_Angeles",
}


def resolve_tz(name: str) -> ZoneInfo:
    key = name.strip()
    iana = TZ_ALIASES.get(key.upper(), key)
    try:
        return ZoneInfo(iana)
    except ZoneInfoNotFoundError:
        raise argparse.ArgumentTypeError(
            f"Unknown time zone: {name!r} (use an IANA name like "
            f"'Asia/Tokyo' or an abbreviation like 'JST')"
        )


def parse_args():
    parser = argparse.ArgumentParser(
        description="Convert a datetime between time zones."
    )

    parser.add_argument(
        "datetime",
        help='e.g. "2025-12-13 00:00"'
    )

    parser.add_argument(
        "from_tz",
        type=resolve_tz,
        help='e.g. "Asia/Tokyo" or "JST"'
    )

    parser.add_argument(
        "to_tz",
        type=resolve_tz,
        help='e.g. "Europe/Berlin" or "CT"'
    )

    return parser.parse_args()


def main(args):
    dt = datetime.strptime(args.datetime, "%Y-%m-%d %H:%M")
    dt = dt.replace(tzinfo=args.from_tz)
    converted = dt.astimezone(args.to_tz)
    print(f"{dt:%Y-%m-%d %H:%M %Z} -> {converted:%Y-%m-%d %H:%M %Z}")


if __name__ == "__main__":
    main(parse_args())
