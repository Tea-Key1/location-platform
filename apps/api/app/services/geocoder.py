import requests


class GeocoderRateLimited(Exception):
    pass


class GeocoderUnavailable(Exception):
    pass


def reverse_geocode(lat, lng):

    url = (
        "https://nominatim.openstreetmap.org/reverse"
    )

    params = {
        "lat": lat,
        "lon": lng,
        "format": "json",
        "addressdetails": 1,
    }

    headers = {
        "User-Agent": "roamie-app"
    }

    try:
        r = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=10
        )
    except requests.RequestException as exc:
        raise GeocoderUnavailable("Geocoder request failed") from exc

    if r.status_code == 429:
        raise GeocoderRateLimited("Geocoder rate limited")

    try:
        r.raise_for_status()
    except requests.HTTPError as exc:
        raise GeocoderUnavailable("Geocoder service unavailable") from exc

    try:
        data = r.json()
    except ValueError as exc:
        raise GeocoderUnavailable("Invalid geocoder response") from exc

    address = data.get("address", {})

    prefecture = (
        address.get("province")
        or address.get("state")
    )

    city = (
        address.get("city")
        or address.get("town")
        or address.get("village")
    )

    district = (
        address.get("suburb")
        or address.get("neighbourhood")
    )

    return {
        "prefecture": prefecture,
        "city": city,
        "district": district,
        "full": data.get("display_name")
    }
