Wallet API
Тестовое Посашков Станислав TG: @Werxiq

## Запуск
docker compose up --build


API: http://localhost:8000  
Swagger: http://localhost:8000/docs

## Эндпоинты

POST /api/v1/wallets  Создать кошелёк
GET /api/v1/wallets/{wallet_id} Получить баланс
POST /api/v1/wallets/{wallet_id}/operation Операции с балансом DEPOSIT / WITHDRAW

## Тесты
Автотесты через pytest

python -m pytest -v

tests/test_wallet.py::test_create_wallet 
tests/test_wallet.py::test_deposit_and_withdraw 
tests/test_wallet.py::test_withdraw_insufficient_funds 
tests/test_wallet.py::test_wallet_not_found 
tests/test_wallet.py::test_negative_amount_rejected 
tests/test_wallet.py::test_concurrent_withdrawals_cannot_overdraw 
tests/test_wallet.py::test_concurrent_deposits_preserve_balance 