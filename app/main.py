from fastapi import FastAPI, Depends, HTTPException, status
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db
from app.schemas import WalletResponse, OperationRequest
from app.services.wallet_service import (
    InsufficientFundsError,
    WalletNotFoundError,
    create_wallet,
    get_wallet,
    perform_operation,
)

app = FastAPI(title="Wallet Api")

@app.get("/")
async def home():
    return {"message:" "Wallet API is running"}

@app.post(
    "/api/v1/wallets",
    response_model=WalletResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_wallet_endpoint(
    session: AsyncSession = Depends(get_db),
):
    wallet = await create_wallet(session)

    return WalletResponse(
        wallet_id=UUID(wallet.id),
        balance=wallet.balance,
    )

@app.get(
    "/api/v1/wallets/{wallet_id}",
    response_model=WalletResponse,
)
async def wallet_check(
    wallet_id: UUID,
    session: AsyncSession = Depends(get_db),
):
    wallet = await get_wallet(session, wallet_id)

    if wallet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found"
        )

    return WalletResponse(
        wallet_id=UUID(wallet.id),
        balance=wallet.balance,
    )

@app.post(
    "/api/v1/wallets/{wallet_id}/operation",
    response_model=WalletResponse,
)
async def wallet_operation(
    wallet_id: UUID,
    operation: OperationRequest,
    session: AsyncSession = Depends(get_db),
): 
    try:
        wallet = await perform_operation(
            session=session,
            wallet_id=wallet_id,
            operation_type=operation.operation_type,
            amount=operation.amount,
        )

    except WalletNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found",
        )

    except InsufficientFundsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient funds",
        )

    return WalletResponse(
        wallet_id=UUID(wallet.id),
        balance=wallet.balance,
    )