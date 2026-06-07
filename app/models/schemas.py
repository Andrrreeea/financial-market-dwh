from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import date


class AssetClass(BaseModel):
    name: str = Field(..., examples=["stock", "crypto", "commodity"])
    description: Optional[str] = None


class FinancialAssetCreate(BaseModel):
    symbol: str = Field(..., examples=["AAPL", "BTC", "GC=F"])
    name: str = Field(..., examples=["Apple Inc.", "Bitcoin", "Gold Futures"])
    asset_class: str = Field(..., examples=["stock", "crypto", "commodity"])
    description: Optional[str] = None
    region: Optional[str] = Field(None, examples=["US", "Global", "Europe"])
    currency: Optional[str] = Field(None, examples=["USD", "EUR"])
    exchange: Optional[str] = Field(None, examples=["NASDAQ", "Crypto", "COMEX"])
    additional_attributes: Dict[str, Any] = Field(default_factory=dict)


class FinancialAssetResponse(FinancialAssetCreate):
    asset_id: str
    version: int
    valid_from: datetime
    valid_to: Optional[datetime]
    is_current: bool
    is_deleted: bool
    created_at: datetime
    provenance: Dict[str, Any]


class DataSourceCreate(BaseModel):
    name: str = Field(..., examples=["Nasdaq Data Link", "Bloomberg", "Mock Provider"])
    provider_type: str = Field(..., examples=["external_api", "mock", "csv"])
    base_url: Optional[str] = None
    description: Optional[str] = None
    license: Optional[str] = None
    additional_attributes: Dict[str, Any] = Field(default_factory=dict)


class DataSourceResponse(DataSourceCreate):
    data_source_id: str
    created_at: datetime
    provenance: Dict[str, Any]


class TimeSeriesCreate(BaseModel):
    asset_id: str
    data_source_id: str
    name: str = Field(..., examples=["Daily OHLCV Prices"])
    frequency: str = Field(..., examples=["daily", "hourly", "monthly"])
    timezone: str = Field(default="UTC")
    indicators: List[str] = Field(default_factory=list)
    additional_attributes: Dict[str, Any] = Field(default_factory=dict)


class TimeSeriesResponse(TimeSeriesCreate):
    time_series_id: str
    created_at: datetime
    provenance: Dict[str, Any]


class TimeSeriesPointCreate(BaseModel):
    time_series_id: str
    timestamp: datetime
    indicators: Dict[str, Any] = Field(
        ...,
        examples=[{
            "open": 190.1,
            "high": 195.3,
            "low": 188.7,
            "close": 193.2,
            "volume": 52000000
        }]
    )


class TimeSeriesPointResponse(TimeSeriesPointCreate):
    point_id: str
    version: int
    valid_from: datetime
    valid_to: Optional[datetime]
    is_current: bool
    is_deleted: bool
    created_at: datetime
    provenance: Dict[str, Any]


class PortfolioCreate(BaseModel):
    owner_name: str
    owner_type: str = Field(..., examples=["person", "company"])
    name: str
    description: Optional[str] = None
    holdings: List[Dict[str, Any]] = Field(default_factory=list)


class PortfolioResponse(PortfolioCreate):
    portfolio_id: str
    created_at: datetime


class TimeSeriesPointIngest(BaseModel):
    asset_id: str
    data_source_id: str
    business_date: date
    values: Dict[str, Any]
    attributes: Dict[str, Any] = Field(default_factory=dict)


class TimeSeriesBatchIngest(BaseModel):
    records: List[TimeSeriesPointIngest]