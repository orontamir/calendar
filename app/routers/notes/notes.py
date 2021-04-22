from typing import Any, Dict, List, Sequence

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.param_functions import Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

from app.database.schemas import NoteDB, NoteSchema
from app.dependencies import get_db, templates
from app.internal import utils
from app.internal.notes import notes

router = APIRouter(
    prefix="/notes",
    tags=["notes"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "/edit/{note_id}",
    status_code=status.HTTP_202_ACCEPTED,
    include_in_schema=False,
)
async def redirect_update_note(
    request: Request,
    note_id: int,
    session: Session = Depends(get_db),
) -> RedirectResponse:
    """Update a note using user-interface form."""
    form = await request.form()
    updated_note = NoteSchema(**dict(form))
    await update_note(updated_note, note_id, session)
    return RedirectResponse("/notes", status_code=status.HTTP_302_FOUND)


@router.post(
    "/delete/{note_id}",
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
async def redirect_delete_note(
    note_id: int,
    session: Session = Depends(get_db),
) -> RedirectResponse:
    """Delete a note from the database using user-interface form."""
    await delete_note(note_id, session)
    return RedirectResponse("/notes", status_code=status.HTTP_302_FOUND)


@router.post(
    "/add",
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
async def create_note_by_form(
    request: Request,
    session: Session = Depends(get_db),
) -> RedirectResponse:
    """Add a note using user-interface form."""
    form = await request.form()
    new_note = NoteSchema(**dict(form))
    new_note.creator = utils.get_current_user(session)
    await notes.create_note(note=new_note, session=session)
    return RedirectResponse("/notes", status_code=status.HTTP_302_FOUND)


@router.post("/", response_model=NoteDB, status_code=status.HTTP_201_CREATED)
async def create_new_note(
    request: NoteSchema,
    session: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Create a note in the database."""
    new_note = NoteSchema(**dict(request))
    new_note.creator = utils.get_current_user(session)
    return await notes.create_note(note=new_note, session=session)


@router.delete("/{note_id}/", status_code=status.HTTP_200_OK)
async def delete_note(note_id: int, session: Session = Depends(get_db)) -> str:
    """Delete a note by its identifier."""
    return await notes.delete(session, note_id)


@router.put("/{note_id}/", status_code=status.HTTP_202_ACCEPTED)
async def update_note(
    request: NoteSchema,
    note_id: int,
    session: Session = Depends(get_db),
) -> str:
    """Update a note by providing its identifier and the changed json data."""
    return await notes.update(request, session, note_id)


@router.get("/view/{note_id}", include_in_schema=False)
async def view_note(
    request: Request,
    note_id: int,
    session: Session = Depends(get_db),
) -> Response:
    """View a note for update using user interface."""
    note = await notes.view(session, note_id)
    return templates.TemplateResponse(
        "notes/note_view.html",
        {"request": request, "data": note},
    )


@router.get("/delete/{note_id}", include_in_schema=False)
async def remove_note(
    request: Request,
    note_id: int,
    session: Session = Depends(get_db),
) -> Response:
    """View a note for delete using user interface."""
    note = await notes.view(session, note_id)
    return templates.TemplateResponse(
        "notes/note_delete.html",
        {"request": request, "data": note},
    )


@router.get("/add", include_in_schema=False)
async def create_note_form(request: Request) -> Response:
    """View form for creating a new note."""
    return templates.TemplateResponse("notes/note.html", {"request": request})


@router.get("/all", response_model=List[NoteDB])
async def get_all_notes(
    session: Session = Depends(get_db),
) -> Sequence[NoteDB]:
    """View all notes in the database."""
    return await notes.get_all(session)


@router.get(
    "/{note_id}/",
    status_code=status.HTTP_200_OK,
    response_model=NoteDB,
)
async def read_note(
    note_id: int,
    session: Session = Depends(get_db),
) -> NoteDB:
    """View a note by its identifier."""
    note = await notes.view(session, note_id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with id {note_id} not found",
        )
    return note


@router.get("/", include_in_schema=False)
async def view_notes(
    request: Request,
    session: Session = Depends(get_db),
) -> Response:
    """View all notes in the database using user interface."""
    data = await notes.get_all(session)
    return templates.TemplateResponse(
        "notes/notes.html",
        {"request": request, "data": data},
    )