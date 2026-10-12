from typing import Optional

from pydantic import BaseModel, Field


class SendMessageModel(BaseModel):
    """Request body for the Pushover messages endpoint"""

    # repr=False keeps the API token out of logs and tracebacks
    token: str = Field(repr=False)
    user: str
    device: Optional[str] = None
    title: Optional[str] = None
    message: str

    def dump(self) -> dict:
        """dumps the content as dictionary without null values

        Returns:
            dict: dictionary dump
        """
        return self.model_dump(exclude_none=True)
