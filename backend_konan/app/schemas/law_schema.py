from pydantic import BaseModel

class LawArticleIn(BaseModel):
    source: str
    article: str
    texte: str
    lang: str = "fr"

class LawArticleOut(LawArticleIn):
    id: int
    class Config:
        from_attributes = True
