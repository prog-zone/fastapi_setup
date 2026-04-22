# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select
# from sqlalchemy.orm import selectinload

# from app.core.database import get_db
# from app.api.deps import get_current_user
# from app.models.user import User, Profile
# from app.schemas.user import UserFullSchema, ProfileSchema, ProfileCreateSchema


# router = APIRouter(prefix="/user", tags=["user"])

# @router.get("/me", response_model=UserFullSchema)
# async def get_user_profile(
#     current_user: User = Depends(get_current_user), 
#     db: AsyncSession = Depends(get_db)
# ):
#     # Eagerly load all relationships to prevent async lazy-loading crashes
#     query = select(User).where(User.id == current_user.id).options(
#         selectinload(User.profile),
#     )
    
#     result = await db.execute(query)
#     user_data = result.scalar_one_or_none()
    
#     if not user_data:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
#     return user_data


# @router.patch("/profile", response_model=ProfileSchema)
# async def upsert_profile(
#     profile_in: ProfileCreateSchema,
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     query = select(Profile).where(Profile.user_id == current_user.id)
#     result = await db.execute(query)
#     profile = result.scalar_one_or_none()

#     if profile:
#         update_data = profile_in.model_dump(exclude_unset=True)
#         for key, value in update_data.items():
#             setattr(profile, key, value)
#     else:
#         profile = Profile(**profile_in.model_dump(), user_id=current_user.id)
#         db.add(profile)

#     await db.commit()
#     await db.refresh(profile)
#     return profile
