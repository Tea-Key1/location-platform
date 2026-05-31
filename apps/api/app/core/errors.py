# app/core/errors.py

from fastapi import HTTPException


def unauthorized():
    raise HTTPException(
        status_code=401,
        detail="Unauthorized"
    )


def profile_not_found():
    raise HTTPException(
        status_code=404,
        detail="Profile not found"
    )


def conflict(message="Conflict"):
    raise HTTPException(
        status_code=409,
        detail=message
    )


def invalid_apple_token():
    raise HTTPException(
        status_code=401,
        detail="Invalid Apple token"
    )