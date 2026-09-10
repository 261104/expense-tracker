from conftest import register_and_login


def expense_payload(amount: str, category: str, day: str = "2026-09-10"):
    return {
        "amount": amount,
        "category": category,
        "description": "Test expense",
        "payment_method": "Card",
        "date": day,
    }


def test_expense_crud_and_pagination(client):
    headers = register_and_login(client, "owner@example.com")
    first = client.post("/expenses", json=expense_payload("125.00", "Food"), headers=headers)
    second = client.post("/expenses", json=expense_payload("250.00", "Transport", "2026-09-09"), headers=headers)
    assert first.status_code == 201
    assert second.status_code == 201

    listing = client.get("/expenses?page=1&limit=1", headers=headers)
    assert listing.status_code == 200
    assert listing.json()["total"] == 2
    assert listing.json()["pages"] == 2
    assert len(listing.json()["items"]) == 1

    expense_id = first.json()["id"]
    assert client.get(f"/expenses/{expense_id}", headers=headers).status_code == 200
    updated = client.put(
        f"/expenses/{expense_id}",
        json=expense_payload("150.00", "Food"),
        headers=headers,
    )
    assert updated.status_code == 200
    assert client.delete(f"/expenses/{expense_id}", headers=headers).status_code == 204
    assert client.get(f"/expenses/{expense_id}", headers=headers).status_code == 404


def test_filters_and_safe_sorting(client):
    headers = register_and_login(client, "filter@example.com")
    client.post("/expenses", json=expense_payload("100.00", "Food"), headers=headers)
    client.post("/expenses", json=expense_payload("500.00", "Food"), headers=headers)
    client.post("/expenses", json=expense_payload("50.00", "Transport"), headers=headers)

    response = client.get(
        "/expenses?category=Food&min_amount=100&max_amount=500&sort_by=amount&order=asc",
        headers=headers,
    )
    assert response.status_code == 200
    assert [item["amount"] for item in response.json()["items"]] == ["100.00", "500.00"]

    invalid_range = client.get("/expenses?min_amount=500&max_amount=100", headers=headers)
    assert invalid_range.status_code == 422


def test_expenses_require_authentication(client):
    assert client.get("/expenses").status_code == 401
    assert client.post("/expenses", json=expense_payload("10.00", "Food")).status_code == 401


def test_expense_stats_are_user_scoped(client):
    headers = register_and_login(client, "stats@example.com")
    client.post("/expenses", json=expense_payload("100.00", "Food"), headers=headers)
    client.post("/expenses", json=expense_payload("50.00", "Transport"), headers=headers)

    response = client.get("/expenses/stats", headers=headers)
    assert response.status_code == 200
    assert response.json()["total_spending"] == "150.00"
    assert response.json()["average_expense"] == "75.00"
    assert response.json()["category_breakdown"][0] == {"category": "Food", "total": "100.00"}


def test_health_and_dashboard(client):
    headers = register_and_login(client, "dashboard@example.com")
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/health/db").status_code == 200
    client.post("/expenses", json=expense_payload("100.00", "Food"), headers=headers)
    budget = client.post(
        "/budgets",
        json={"month": "2026-09-01", "amount": "500.00"},
        headers=headers,
    )
    assert budget.status_code == 201
    assert client.get("/budgets", headers=headers).status_code == 200
    dashboard = client.get("/dashboard", headers=headers)
    assert dashboard.status_code == 200
    assert dashboard.json()["total_spending"] == "100.00"
