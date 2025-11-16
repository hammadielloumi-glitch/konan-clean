# app/models.py
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, func
from app.database import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), nullable=False, index=True)
    role = Column(String(50), nullable=False)
    message_user = Column(Text, nullable=True)
    message_konan = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class LawArticle(Base):
    __tablename__ = "law_articles"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), nullable=False, unique=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(100), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class RefLanguage(Base):
    __tablename__ = "ref_language"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), nullable=False, unique=True)
    label = Column(String(100), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class CurrentArticlesV(Base):
    __tablename__ = "current_articles_v"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, nullable=False)
    language_id = Column(Integer, nullable=False)
    version = Column(String(20), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
