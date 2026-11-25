"""Farm service for farm management business logic."""

import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from backend.domain.models import Farm, FarmCropCycle, FarmLocation, FarmMember, CropHealthRecord
from backend.domain.schemas import FarmCreate, FarmUpdate, FarmCropCycleCreate, CropHealthRecordCreate


class FarmService:
    """Service handling Farm CRUD and related associations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_farms(self, user_id: uuid.UUID, skip: int = 0, limit: int = 50) -> List[Farm]:
        """List farms owned by or shared with user."""
        stmt = (
            select(Farm)
            .outerjoin(FarmMember, Farm.id == FarmMember.farm_id)
            .where((Farm.owner_id == user_id) | (FarmMember.user_id == user_id))
            .options(selectinload(Farm.location))
            .offset(skip)
            .limit(limit)
            .distinct()
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_farm(self, farm_id: uuid.UUID) -> Optional[Farm]:
        """Get farm by ID with its location."""
        stmt = (
            select(Farm)
            .where(Farm.id == farm_id)
            .options(selectinload(Farm.location))
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def create_farm(self, farm_in: FarmCreate, owner_id: uuid.UUID) -> Farm:
        """Create a new farm with optional location."""
        farm = Farm(
            name=farm_in.name,
            description=farm_in.description,
            area_hectares=farm_in.area_hectares,
            owner_id=owner_id,
        )
        self.db.add(farm)
        await self.db.flush()

        if farm_in.location:
            location = FarmLocation(
                farm_id=farm.id,
                latitude=farm_in.location.latitude,
                longitude=farm_in.location.longitude,
                altitude_m=farm_in.location.altitude_m,
                region=farm_in.location.region,
                country=farm_in.location.country,
                governorate=farm_in.location.governorate,
            )
            self.db.add(location)

        await self.db.commit()
        await self.db.refresh(farm)
        return farm

    async def update_farm(self, farm_id: uuid.UUID, farm_in: FarmUpdate, user_id: uuid.UUID) -> Farm:
        """Update farm details and location."""
        farm = await self.get_farm(farm_id)
        if not farm:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farm not found")
        if farm.owner_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this farm")

        if farm_in.name is not None:
            farm.name = farm_in.name
        if farm_in.description is not None:
            farm.description = farm_in.description
        if farm_in.area_hectares is not None:
            farm.area_hectares = farm_in.area_hectares

        if farm_in.location:
            if farm.location:
                farm.location.latitude = farm_in.location.latitude
                farm.location.longitude = farm_in.location.longitude
                farm.location.altitude_m = farm_in.location.altitude_m
                farm.location.region = farm_in.location.region
                farm.location.country = farm_in.location.country
                farm.location.governorate = farm_in.location.governorate
            else:
                loc = FarmLocation(
                    farm_id=farm.id,
                    latitude=farm_in.location.latitude,
                    longitude=farm_in.location.longitude,
                    altitude_m=farm_in.location.altitude_m,
                    region=farm_in.location.region,
                    country=farm_in.location.country,
                    governorate=farm_in.location.governorate,
                )
                self.db.add(loc)

        await self.db.commit()
        await self.db.refresh(farm)
        return farm

    async def get_farm_crops(self, farm_id: uuid.UUID) -> List[FarmCropCycle]:
        """List active crop cycles for a farm."""
        stmt = (
            select(FarmCropCycle)
            .where(FarmCropCycle.farm_id == farm_id)
            .options(selectinload(FarmCropCycle.crop))
            .order_by(FarmCropCycle.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def add_crop_to_farm(self, farm_id: uuid.UUID, cycle_in: FarmCropCycleCreate) -> FarmCropCycle:
        """Add a crop cycle to a farm."""
        cycle = FarmCropCycle(
            farm_id=farm_id,
            crop_id=cycle_in.crop_id,
            variety_id=cycle_in.variety_id,
            planted_at=cycle_in.planted_at,
            current_stage=cycle_in.current_stage,
            notes=cycle_in.notes,
        )
        self.db.add(cycle)
        await self.db.commit()
        await self.db.refresh(cycle)
        return cycle

    async def get_farm_health_records(
        self, farm_id: uuid.UUID, limit: int = 50
    ) -> List[CropHealthRecord]:
        """List crop health records for a farm."""
        stmt = (
            select(CropHealthRecord)
            .where(CropHealthRecord.farm_id == farm_id)
            .order_by(CropHealthRecord.recorded_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def add_health_record(
        self, farm_id: uuid.UUID, record_in: CropHealthRecordCreate
    ) -> CropHealthRecord:
        """Record crop health event."""
        rec = CropHealthRecord(
            farm_id=farm_id,
            crop_cycle_id=record_in.crop_cycle_id,
            analysis_job_id=record_in.analysis_job_id,
            disease_id=record_in.disease_id,
            severity=record_in.severity,
            confidence_score=record_in.confidence_score,
            notes=record_in.notes,
        )
        self.db.add(rec)
        await self.db.commit()
        await self.db.refresh(rec)
        return rec
