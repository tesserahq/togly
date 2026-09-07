def test_create_feature(client, faker):
    key = faker.slug()
    response = client.post("/features", json={"key": key, "description": "d"})

    assert response.status_code == 201
    body = response.json()
    assert body["key"] == key
    assert body["gates"] == []


def test_create_feature_duplicate_key_returns_409(client, faker):
    key = faker.slug()
    client.post("/features", json={"key": key})

    response = client.post("/features", json={"key": key})

    assert response.status_code == 409


def test_get_feature_not_found_returns_404(client):
    response = client.get("/features/does-not-exist")
    assert response.status_code == 404


def test_get_feature(client, faker):
    key = faker.slug()
    client.post("/features", json={"key": key})

    response = client.get(f"/features/{key}")

    assert response.status_code == 200
    assert response.json()["key"] == key


def test_list_features(client, faker):
    key = faker.slug()
    client.post("/features", json={"key": key})

    response = client.get("/features")

    assert response.status_code == 200
    keys = [f["key"] for f in response.json()["items"]]
    assert key in keys


def test_delete_feature(client, faker):
    key = faker.slug()
    client.post("/features", json={"key": key})

    response = client.delete(f"/features/{key}")
    assert response.status_code == 204

    assert client.get(f"/features/{key}").status_code == 404


def test_delete_unknown_feature_returns_404(client):
    response = client.delete("/features/does-not-exist")
    assert response.status_code == 404


def test_enable_and_disable_boolean_gate(client, faker):
    key = faker.slug()
    client.post("/features", json={"key": key})

    enable = client.post(f"/features/{key}/gates/boolean")
    assert enable.status_code == 200
    assert enable.json()["gate_type"] == "boolean"

    detail = client.get(f"/features/{key}")
    assert len(detail.json()["gates"]) == 1

    disable = client.delete(f"/features/{key}/gates/boolean")
    assert disable.status_code == 204

    detail = client.get(f"/features/{key}")
    assert detail.json()["gates"] == []


def test_enable_and_disable_actor_gate(client, faker):
    key = faker.slug()
    client.post("/features", json={"key": key})

    enable = client.post(f"/features/{key}/gates/actors/actor-1")
    assert enable.status_code == 200
    assert enable.json()["value"] == "actor-1"

    disable = client.delete(f"/features/{key}/gates/actors/actor-1")
    assert disable.status_code == 204

    detail = client.get(f"/features/{key}")
    assert detail.json()["gates"] == []


def test_audit_log_reflects_mutations(client, faker):
    key = faker.slug()
    create_response = client.post("/features", json={"key": key})
    feature_id = create_response.json()["id"]

    client.post(f"/features/{key}/gates/boolean")
    client.delete(f"/features/{key}")

    audit_response = client.get(f"/feature-audit-logs/{feature_id}")
    assert audit_response.status_code == 200
    actions = [entry["action"] for entry in audit_response.json()]
    assert actions == ["deleted", "boolean_enabled", "created"]


def test_audit_log_survives_key_reuse_and_is_scoped_by_feature_id(client, faker):
    key = faker.slug()
    first = client.post("/features", json={"key": key}).json()
    client.delete(f"/features/{key}")

    second = client.post("/features", json={"key": key}).json()

    assert first["id"] != second["id"]

    first_audit = client.get(f"/feature-audit-logs/{first['id']}").json()
    second_audit = client.get(f"/feature-audit-logs/{second['id']}").json()

    assert [e["action"] for e in first_audit] == ["deleted", "created"]
    assert [e["action"] for e in second_audit] == ["created"]
