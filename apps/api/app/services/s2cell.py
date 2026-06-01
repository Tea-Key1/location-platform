from s2sphere import CellId, LatLng


S2_LEVEL = 12


def latlng_to_s2(lat: float, lng: float, level: int = S2_LEVEL):
    latlng = LatLng.from_degrees(lat, lng)

    cell = CellId.from_lat_lng(latlng).parent(level)

    return str(cell.id())
