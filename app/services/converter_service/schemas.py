from pydantic import BaseModel, field_validator


class ParameterInstance(BaseModel):
    id: int
    value: str
    mo_id: int
    tprm_id: int

    @field_validator("value", mode="before")
    @classmethod
    def ensure_string(cls, v):
        if v is None:
            return ""
        return str(v)
