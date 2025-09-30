from fastapi.testclient import TestClient

from backend.main import DATASET_ROOT, app


client = TestClient(app)


def test_dataset_exists() -> None:
    assert DATASET_ROOT.exists()


def test_list_classes_returns_items() -> None:
    response = client.get("/api/classes")
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert payload, "Expected at least one class to be returned"
    assert {"id", "name"}.issubset(payload[0].keys())


def test_list_images_contains_sample() -> None:
    response = client.get("/api/images")
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    image_ids = {item["id"] for item in payload}
    assert "0015" in image_ids


def test_fetch_label_for_image() -> None:
    response = client.get("/api/label/0015")
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert payload
    first = payload[0]
    assert {"class_id", "class_name", "bbox"}.issubset(first.keys())
    assert {"cx", "cy", "width", "height"}.issubset(first["bbox"].keys())


def test_missing_label_returns_404() -> None:
    response = client.get("/api/label/non-existent")
    assert response.status_code == 404
