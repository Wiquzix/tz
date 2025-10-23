from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_db
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.schemas import ListVegetable, Vegetable, CreateVegetable, UpdateVegetable, DeleteVegetable
from app.models.models import Vegetable as VegetableDB
from sqlalchemy import select


router = APIRouter()


@router.get('/',response_model=ListVegetable)
async def get_vegetables(   
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    ):
    """
    Получить список всех овощей
    """
    result = await db.execute(select(VegetableDB).offset(skip).limit(limit))
    items = result.scalars().all()
    total = len(items)
    
    vegetable_list = [
        Vegetable(
            uuid=item.uuid,
            title=item.title,
            weight=item.weight,
            price=item.price,
            length=item.length
        ) for item in items
    ]
    
    return ListVegetable(
        items=vegetable_list,
        total=total,
        limit=limit,
        offset=skip
    )

@router.get('/{vegetable_id}',response_model=Vegetable)
async def get_vegetable(
    vegetable_id: str,
    db: AsyncSession = Depends(get_db)
    ):
    """
    Получить овощ по UUID
    """
    result = await db.execute(select(VegetableDB).where(VegetableDB.uuid == vegetable_id))
    vegetable = result.scalar_one_or_none()
    if vegetable is None:
        raise HTTPException(status_code=404, detail="Vegetable not found")
    return vegetable

@router.post('/',response_model=Vegetable)
async def create_vegetable(
    vegetable: CreateVegetable,
    db: AsyncSession = Depends(get_db)
    ):
    """
    Создать новый овощ
    """
    new_vegetable = VegetableDB(
        title=vegetable.title,
        weight=vegetable.weight,
        price=vegetable.price,
        length=vegetable.length
    )
    db.add(new_vegetable)
    await db.commit()
    return new_vegetable

@router.put('/{vegetable_id}',response_model=Vegetable)
async def update_vegetable(
    vegetable_id: str,
    vegetable: UpdateVegetable,
    db: AsyncSession = Depends(get_db)
    ):
    """
    Обновить информацию об овоще
    """
    result = await db.execute(select(VegetableDB).where(VegetableDB.uuid == vegetable_id))
    vegetable_in_db = result.scalar_one_or_none()
    if vegetable_in_db is None:
        raise HTTPException(status_code=404, detail="Vegetable not found")
    vegetable_in_db.title = vegetable.title
    vegetable_in_db.weight = vegetable.weight
    vegetable_in_db.price = vegetable.price
    vegetable_in_db.length = vegetable.length
    await db.commit()
    return vegetable_in_db

@router.delete('/{vegetable_id}',response_model=DeleteVegetable)
async def delete_vegetable(
    vegetable_id: str,
    db: AsyncSession = Depends(get_db)
    ):
    """
    Удалить овощ по UUID
    """
    result = await db.execute(select(VegetableDB).where(VegetableDB.uuid == vegetable_id))
    vegetable_in_db = result.scalar_one_or_none()
    if vegetable_in_db is None:
        raise HTTPException(status_code=404, detail="Vegetable not found")
    
    vegetable_data = Vegetable(
        uuid=vegetable_in_db.uuid,
        title=vegetable_in_db.title,
        weight=vegetable_in_db.weight,
        price=vegetable_in_db.price,
        length=vegetable_in_db.length
    )
    
    await db.delete(vegetable_in_db)
    await db.commit()
    return DeleteVegetable(message="Vegetable deleted successfully", deleted_vegetable=vegetable_data)