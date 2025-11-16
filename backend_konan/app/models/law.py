from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.database import Base  # ✅ FI9_NAYEK : Source unique

class LawArticle(Base):
    __tablename__ = "law_articles"
    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(200), index=True, nullable=False)   # ex: "Code de commerce"
    article = Column(String(50), index=True, nullable=False)   # ex: "Art. 371"
    texte = Column(Text, nullable=False)
    lang = Column(String(8), default="fr")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
