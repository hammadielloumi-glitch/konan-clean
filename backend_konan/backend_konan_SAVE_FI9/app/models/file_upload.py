from sqlalchemy import Column, Integer, String, DateTime, text
from app.database import Base  # ✅ FI9_NAYEK : Source unique

class FileUpload(Base):
    __tablename__ = "file_uploads"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    filepath = Column(String(512), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=text("now()"))
