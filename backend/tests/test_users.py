from conftest import register_and_login


def test_users_cannot_access_each_others_expenses(client):
    user_a = register_and_login(client, "a@example.com")
    user_b = register_and_login(client, "b@example.com")
    expense = client.post(
        "/expenses",
        json={
            "amount": "99.99",
            "category": "Bills",
            "description": "Private",
            "payment_method": "Bank",
            "date": "2026-09-10",
        },
        headers=user_a,
    )
    expense_id = expense.json()["id"]

    assert client.get("/expenses", headers=user_b).json()["total"] == 0
    assert client.get(f"/expenses/{expense_id}", headers=user_b).status_code == 404
    assert client.put(
        f"/expenses/{expense_id}",
        json={
            "amount": "1.00",
            "category": "Other",
            "description": "Attempt",
            "payment_method": "Cash",
            "date": "2026-09-10",
        },
        headers=user_b,
    ).status_code == 404
    assert client.delete(f"/expenses/{expense_id}", headers=user_b).status_code == 404


def test_users_cannot_modify_each_others_budget(client):
    user_a = register_and_login(client, "budget-a@example.com")
    user_b = register_and_login(client, "budget-b@example.com")
    budget = client.post(
        "/budgets",
        json={"month": "2026-09-01", "amount": "500.00"},
        headers=user_a,
    )
    budget_id = budget.json()["id"]
    assert client.get("/budgets", headers=user_b).json() == []
    payload = {"month": "2026-09-01", "amount": "1.00"}
    assert client.put(f"/budgets/{budget_id}", json=payload, headers=user_b).status_code == 404
    assert client.delete(f"/budgets/{budget_id}", headers=user_b).status_code == 404
