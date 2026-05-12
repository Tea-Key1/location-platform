from s2sphere import CellId, LatLng

LEVEL = 10


def latlng_to_cell_id(
    lat: float,
    lng: float
) -> int:

    latlng = LatLng.from_degrees(
        lat,
        lng
    )

    cell = CellId.from_lat_lng(
        latlng
    ).parent(LEVEL)

    return cell.id()


def cell_id_to_latlng(cell_id: int):
    cell = CellId(cell_id)
    latlng = cell.to_lat_lng()

    return {
        "lat": latlng.lat().degrees,
        "lng": latlng.lng().degrees,
    }