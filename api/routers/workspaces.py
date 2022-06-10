from datetime import datetime
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, status
from pydantic import ValidationError
from api.core.schemas import CreateWorkspace
from api.models import Workspace
from sqlalchemy.orm import Session
from api import database


router = APIRouter(
    tags=['Workspaces']
)


@router.get("/workspaces")
def all_workspaces(q: Optional[str] = None, db: Session = database.session()):
    workspaces = db.query(Workspace).all()
    return workspaces


@router.get("/workspaces/{workspace_id}")
def read_archive(workspace_id: UUID, db: Session = database.session()):
    workspace = (db.query(Workspace)
                 .filter(Workspace.id == workspace_id)
                 .first())

    if not workspace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Workspace {workspace_id} not found')

    return workspace


@router.post('/workspaces')
async def create_workspace(create_workspace: CreateWorkspace, db: Session = database.session()):
    try:
        new_workspace = Workspace(
            name=create_workspace.title,
            description=create_workspace.description,
            created_at=datetime.now(),
        )
        db.add(new_workspace)
        db.commit()
        db.refresh(new_workspace)
        return {"message": f"Workspace created successfully {new_workspace.pk}"}

    except ValidationError as e:
        print(e)
        raise HTTPException(status_code=500, detail='Internal server error')
