from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.logger import log
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User, Profile
from app.schemas.user import UserFullSchema, ProfileSchema, ProfileUpdateSchema


router = APIRouter(prefix="/user", tags=["user"])


"""Retrieve the authenticated user's full profile."""
@router.get("/me", response_model=UserFullSchema)
async def get_user_profile(
    request: Request,
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    try:
        await db.refresh(current_user, ["profile"])
        return current_user
    except Exception as e:
        log.error("get_profile_failed", user_id=str(current_user.id), error=str(e), path=request.url.path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Could not retrieve profile"
        )


"""Update specific fields in the user's profile."""
@router.patch("/me", response_model=ProfileSchema)
async def update_profile(
    request: Request,
    profile_in: ProfileUpdateSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        # 1. Fetch the profile
        query = select(Profile).where(Profile.user_id == current_user.id)
        result = await db.execute(query)
        profile = result.scalar_one_or_none()

        if not profile:
            log.warning("profile_not_found_creating_new", user_id=str(current_user.id))
            profile = Profile(**profile_in.model_dump(), user_id=current_user.id)
            db.add(profile)
        else:
            # 2. Update fields
            update_data = profile_in.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(profile, key, value)

        # 3. Commit and refresh
        await db.commit()
        await db.refresh(profile)
        
        log.info("profile_updated_successfully", user_id=str(current_user.id))
        return profile

    except Exception as e:
        await db.rollback()
        log.error("profile_update_db_failed", user_id=str(current_user.id), error=str(e), path=request.url.path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Database error occurred while updating profile"
        )
    

@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_account(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Permanently delete the user account and all associated data.
    """
    try:
        await db.delete(current_user)
        await db.commit()

        # Clear authentication cookies
        response.delete_cookie(key="access_token", httponly=True, secure=True, samesite="lax")
        response.delete_cookie(key="refresh_token", httponly=True, secure=True, samesite="lax")

        log.info("user_account_deleted", user_id=str(current_user.id))
        return None

    except Exception as e:
        await db.rollback()
        log.error("user_deletion_failed", user_id=str(current_user.id), error=str(e), path=request.url.path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting your account"
        )