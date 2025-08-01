from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text, Integer, DateTime

from .config import Base

class TestOcr(Base):
    __tablename__ = "test_ocr"

    job_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    pdf_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    ocr_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    ocr_result: Mapped[str] = mapped_column(Text, nullable=False)
    pdf_page_num: Mapped[int] = mapped_column(Integer, nullable=False)
    image_file_path: Mapped[str] = mapped_column(String(256), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
