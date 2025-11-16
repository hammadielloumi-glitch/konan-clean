from pydantic import BaseModel

class LawDiffItem(BaseModel):
    source: str
    article: str
    before: str | None
    after: str
    changed_at: str
