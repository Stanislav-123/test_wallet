from decimal import Decimal
import pytest
import asyncio

@pytest.mark.asyncio
async def test_create_wallet(client):
    response = await client.post("/api/v1/wallets")

    assert response.status_code == 201

    data = response.json()

    assert "wallet_id" in data
    assert data["balance"] == "0.00"


@pytest.mark.asyncio
async def test_deposit_and_withdraw(client):
    create_response = await client.post("/api/v1/wallets")
    wallet_id = create_response.json()["wallet_id"]

    deposit_response = await client.post(
        f"/api/v1/wallets/{wallet_id}/operation",
        json={
            "operation_type": "DEPOSIT",
            "amount": "150.50",
        },
    )

    assert deposit_response.status_code == 200
    assert deposit_response.json()["balance"] == "150.50"

    withdraw_response = await client.post(
        f"/api/v1/wallets/{wallet_id}/operation",
        json={
            "operation_type": "WITHDRAW",
            "amount": "50.25",
        },
    )

    assert withdraw_response.status_code == 200
    assert withdraw_response.json()["balance"] == "100.25"


@pytest.mark.asyncio
async def test_withdraw_insufficient_funds(client):
    create_response = await client.post("/api/v1/wallets")
    wallet_id = create_response.json()["wallet_id"]

    response = await client.post(
        f"/api/v1/wallets/{wallet_id}/operation",
        json={
            "operation_type": "WITHDRAW",
            "amount": "10.00",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Insufficient funds"


@pytest.mark.asyncio
async def test_wallet_not_found(client):
    response = await client.get(
        "/api/v1/wallets/00000000-0000-0000-0000-000000000000"
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_negative_amount_rejected(client):
    create_response = await client.post("/api/v1/wallets")
    wallet_id = create_response.json()["wallet_id"]

    response = await client.post(
        f"/api/v1/wallets/{wallet_id}/operation",
        json={
            "operation_type": "DEPOSIT",
            "amount": "-10.00",
        },
    )

    assert response.status_code == 422



@pytest.mark.asyncio
async def test_concurrent_withdrawals_cannot_overdraw(client):
    create_response = await client.post("/api/v1/wallets")
    wallet_id = create_response.json()["wallet_id"]

    deposit_response = await client.post(
        f"/api/v1/wallets/{wallet_id}/operation",
        json={
            "operation_type": "DEPOSIT",
            "amount": "100.00",
        },
    )
    assert deposit_response.status_code == 200

    async def withdraw():
        return await client.post(
            f"/api/v1/wallets/{wallet_id}/operation",
            json={
                "operation_type": "WITHDRAW",
                "amount": "80.00",
            },
        )

    responses = await asyncio.gather(
        withdraw(),
        withdraw(),
    )

    statuses = [response.status_code for response in responses]
    assert statuses.count(200) == 1
    assert statuses.count(400) == 1

    balance_response = await client.get(
        f"/api/v1/wallets/{wallet_id}"
    )
    assert balance_response.status_code == 200
    assert balance_response.json()["balance"] == "20.00"


@pytest.mark.asyncio
async def test_concurrent_deposits_preserve_balance(client):
    create_response = await client.post("/api/v1/wallets")
    wallet_id = create_response.json()["wallet_id"]

    async def deposit():
        return await client.post(
            f"/api/v1/wallets/{wallet_id}/operation",
            json={
                "operation_type": "DEPOSIT",
                "amount": "10.00",
            },
        )

    responses = await asyncio.gather(
        *(deposit() for _ in range(10))
    )

    assert all(response.status_code == 200 for response in responses)

    balance_response = await client.get(
        f"/api/v1/wallets/{wallet_id}"
    )
    assert balance_response.status_code == 200
    assert balance_response.json()["balance"] == "100.00"
