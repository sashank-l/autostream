import logging
from fastapi import APIRouter

router = APIRouter()
logger = logging.getLogger(__name__)

from app.tools.mock_lead import mock_db_leads

@router.get("/leads")
def get_leads():
    # Return the in-memory leads sorted by newest first
    return list(reversed(mock_db_leads))
