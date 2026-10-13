from decimal import Decimal
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Wallet
from app.schemas import OperationType

async def get_wallet(
        session: AsyncSession,
        wallet_id: UUID,
) -> Wallet | None:
    result = await session.execute(
        select(Wallet).where(Wallet.id == str(wallet_id))
    )
    return result.scalar_one_or_none()

async def create_wallet(
        session: AsyncSession,
) -> Wallet:
    wallet = Wallet(balance=Decimal("0.00"))
    session.add(wallet)
    await session.commit()
    await session.refresh(wallet)

    return wallet

class WalletNotFoundError(Exception):
    pass

class InsufficientFundsError(Exception):
    pass

async def perform_operation(
    session: AsyncSession,
    wallet_id: UUID,
    operation_type: OperationType,
    amount: Decimal,
) -> Wallet:
    try:
        result = await session.execute(
            select(Wallet)
            .where(Wallet.id == str(wallet_id))
            .with_for_update()
        )

        wallet = result.scalar_one_or_none()

        if wallet is None:
            raise WalletNotFoundError

        if operation_type == OperationType.DEPOSIT:
            wallet.balance += amount

        elif operation_type == OperationType.WITHDRAW:
            if wallet.balance < amount:
                raise InsufficientFundsError

            wallet.balance -= amount

        await session.commit()

        return wallet

    except Exception:
        await session.rollback()
        raise
            
        