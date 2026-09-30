from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
import datetime

from app.database.session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relationships
    datasets = relationship("Dataset", back_populates="owner", cascade="all, delete-orphan")

class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    row_count = Column(Integer, default=0)
    col_count = Column(Integer, default=0)
    column_mappings = Column(Text, default="{}") # JSON string of mapped fields
    data_quality_score = Column(Float, default=0.0)
    status = Column(String, default="uploaded") # uploaded, mapped, processed, error
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    owner = relationship("User", back_populates="datasets")
    analysis_runs = relationship("AnalysisRun", back_populates="dataset", cascade="all, delete-orphan")
    customer_segments = relationship("CustomerSegment", back_populates="dataset", cascade="all, delete-orphan")

class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False)
    run_type = Column(String, nullable=False) # rfm, kmeans, forecast, anomalies
    status = Column(String, default="pending") # pending, completed, failed
    results = Column(Text, default="{}") # JSON string containing analytical result sets
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    dataset = relationship("Dataset", back_populates="analysis_runs")

class CustomerSegment(Base):
    __tablename__ = "customer_segments"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False)
    customer_id = Column(String, index=True, nullable=False)
    customer_name = Column(String, nullable=True)
    rfm_score = Column(String, nullable=True) # e.g. "555"
    business_segment = Column(String, nullable=True) # e.g. "Champions"
    kmeans_cluster = Column(Integer, nullable=True)
    recency = Column(Float, nullable=True)
    frequency = Column(Integer, nullable=True)
    monetary = Column(Float, nullable=True)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    dataset = relationship("Dataset", back_populates="customer_segments")
