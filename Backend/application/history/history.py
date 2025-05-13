# Code by AkinoAlice@TyrantRey

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException

from Backend.application.dependency.dependency import (
    require_admin,
    require_root,
    require_user,
)
from Backend.utility.handler.database.history import HistoryOperation
from Backend.utility.model.application.history import LoginHistoryRecord, SearchHistoryRecord

router = APIRouter(prefix="/history", dependencies=[Depends(require_user)])
history_database_client = HistoryOperation()


@router.get("/search/")
async def get_search_history(user_id: int) -> list[SearchHistoryRecord]:
    """
    Retrieve the search history for a specific user.

    Args:
        user_id (int): The unique identifier of the user for whom the search history is to be retrieved.

    Returns:
        list[SearchHistoryRecord]: A list of search history records associated with the given user ID.

    Raises:
        HTTPException:
            - 404: If no search history is found for the specified user.

    """
    result = history_database_client.fetch_search_history(user_id=user_id)

    if result == []:
        raise HTTPException(404, "History not found")
    return result


@router.get("/last-login/")
async def get_last_login(user_id: int) -> LoginHistoryRecord:
    """
    Retrieve the last login record for a specific user.

    Args:
        user_id (int): The unique identifier of the user for whom the last login record is to be retrieved.

    Returns:
        LoginHistoryRecord: The most recent login record associated with the specified user ID.

    Raises:
        HTTPException:
            - 404: If no login record is found for the specified user.

    """
    result = history_database_client.fetch_last_login(user_id=user_id)

    if result is None:
        raise HTTPException(404, "History not found")
    return result
