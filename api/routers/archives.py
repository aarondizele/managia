from datetime import datetime
from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Body, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session
from api import database
from api.core.oauth2 import get_current_active_user
from api.core.schemas import UserOAuth
from api.models import Archive, User
import base64
import hashlib
import os
from os import path, getcwd

# Local Path for testing
sep = path.sep
current_directory = getcwd() + sep + "uploads" + sep


router = APIRouter(
    tags=['Archives'],
    prefix="/archives",
    # dependencies=[Depends(get_current_active_user)]
)


class CreateArchive(BaseModel):
    title: str
    description: Optional[str]


@router.get("/")
def all_archives(
    q: Optional[str] = "",
    page: int = 1,
    limit: int = 10,
    db: Session = database.session()
):

    offset = (page - 1) * limit

    archives = (db.query(Archive)
                .filter(Archive.title.contains(q))
                .limit(limit)
                .offset(offset)
                .all())
    # archives = [format(pk) for pk in Archive.all_pks()]
    return archives


@router.get("/{archive_id}")
def read_archive(
    archive_id: UUID,
    db: Session = database.session()
):

    archive = (db.query(Archive)
               .join(User)
               .filter(Archive.id == archive_id)
               .first())

    if not archive:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Archive {archive_id} not found')

    return archive


@router.post('/')
async def create_archive(
        create_archive: CreateArchive,
        db: Session = database.session(),
        current_user: UserOAuth = Depends(get_current_active_user)
):
    try:
        new_archive = Archive(
            title=create_archive.title,
            description=create_archive.description,
            author_id=current_user.id,
            created_at=datetime.now(),
        )
        db.add(new_archive)
        db.commit()
        db.refresh(new_archive)

        return {
            "archive_id": new_archive.id,
            "message": f"Archive created successfully",
        }

    except ValidationError as e:
        print(e)
        raise HTTPException(status_code=500, detail='Internal server error')


@router.delete("/{archive_id}")
def read_archive(
    archive_id: UUID,
    db: Session = database.session()
):

    archive_query = db.query(Archive).filter(Archive.id == archive_id)
    archive = archive_query.first()

    if not archive:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Archive {archive_id} not found')

    archive_query.delete()
    db.commit()

    return {"message": f"Archive {archive_id} deleted successfully"}


'''
Should be working with Websocket
'''


@router.post("/upload", status_code=status.HTTP_200_OK)
def upload(name: str, size: str, currentChunkIndex: str, totalChunks: str, file: str = Body(...)):
    try:
        firstChunk = int(currentChunkIndex) == 0
        lastChunk = int(currentChunkIndex) == int(totalChunks) - 1

        ext = name.split('.').pop()
        data = file.split(',')[1]

        buffer = base64.b64decode(data)

        tmpFilename = f"tmp_{hashlib.md5(name.encode('utf-8')).hexdigest()}.{ext}"
        tmpFilePath = current_directory + tmpFilename
        tmpFileExists = path.exists(tmpFilePath)

        if firstChunk and tmpFileExists:
            os.unlink(tmpFilePath)

        with open(tmpFilePath, "ab") as f:
            f.write(buffer)

        if lastChunk:
            finalFilename = f"{hashlib.md5(str(datetime.now()).encode('utf-8')).hexdigest()}.{ext}"
            finalFilePath = path.join(current_directory, finalFilename)
            os.rename(tmpFilePath, finalFilePath)

            return {"finalFilename": finalFilename}

        return JSONResponse(status_code=status.HTTP_201_CREATED)

    except Exception:
        return JSONResponse(content="Server error", status_code=status.HTTP_403_FORBIDDEN)
