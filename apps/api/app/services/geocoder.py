import requests


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

    r = requests.get(
        url,
        params=params,
        headers=headers,
        timeout=10
    )

    data = r.json()

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

    suburb = (
        address.get("suburb")
        or address.get("neighbourhood")
    )

    return {
        "prefecture": prefecture,
        "city": city,
        "suburb": suburb,
        "full": data.get("display_name")
    }