# Financial Market Data Warehouse

A Financial Market Data Warehouse built using FastAPI, MongoDB, PySpark, Spark MLlib, and MCP (Model Context Protocol).

The platform supports temporal data management, provenance tracking, financial market data ingestion from external providers, analytical processing with Apache Spark, machine learning workflows, and AI-ready integration through MCP tools.

---

# Overview

The project implements a Financial Market Data Warehouse capable of:

* Managing financial assets using temporal versioning
* Registering and managing financial data providers
* Ingesting financial market data from external APIs
* Storing heterogeneous financial time-series observations
* Preserving historical data and provenance information
* Running analytical workflows using PySpark
* Running predictive models using Spark MLlib
* Exposing warehouse capabilities through MCP tools

---

# Key Features

## Temporal Asset Management

* Create financial assets
* Temporal updates (new version created on update)
* Soft deletion using temporal records
* Historical version tracking
* Full provenance metadata

## Data Source Management

* Register external data providers
* Store provider metadata
* Support multiple source systems
* Provenance tracking

## Financial Time-Series Storage

* Business Time support
* System Time support
* Historical preservation
* Heterogeneous attributes
* Provenance metadata

## External Data Ingestion

### Manual Data Ingestion

```http
POST /data/ingest
```

### Nasdaq Data Link Dataset Ingestion

```http
POST /ingestion/nasdaq-dataset
```

### Nasdaq Data Link Datatable Ingestion

```http
POST /ingestion/nasdaq-datatable
```

The platform supports ingestion from Nasdaq Data Link using authenticated REST APIs while preserving source provenance.

## PySpark Analytics

Implemented analytical workflows:

* Record count aggregation
* Average close price
* Minimum close price
* Maximum close price
* Yearly financial aggregations

Workflow:

```http
POST /analytics/yearly-aggregation
```

## Spark ML Prediction

Machine learning workflow implemented using Spark MLlib:

* Linear Regression
* Close price prediction

Input features:

* Open
* High
* Low
* Volume

Workflow:

```http
POST /analytics/predict-close
```

## MCP Integration

The platform exposes warehouse capabilities through MCP tools.

Available MCP capabilities include:

* Asset discovery
* Asset history retrieval
* Time-series retrieval
* Analytics retrieval
* Prediction retrieval

This enables integration with AI agents and LLM-powered assistants.

---

# Technology Stack

| Component            | Technology              |
| -------------------- | ----------------------- |
| API Layer            | FastAPI                 |
| Database             | MongoDB                 |
| Big Data Processing  | Apache Spark            |
| Machine Learning     | Spark MLlib             |
| Programming Language | Python                  |
| Data Model           | Temporal Document Model |
| External Provider    | Nasdaq Data Link        |
| Agent Integration    | MCP                     |

---

# Project Structure

```text
financial-market-dwh/
│
├── app/
│   ├── ingestion/
│   ├── models/
│   ├── repositories/
│   ├── routers/
│   ├── services/
│   ├── workflows/
│   ├── database.py
│   └── main.py
│
├── docs/
│
├── mcp_server/
│   └── server.py
│
├── scripts/
│   └── load_demo_data.py
│
├── requirements.txt
├── README.md
└── .env
```

---

# Installation

## Create Virtual Environment

```bash
python -m venv venv
```

## Activate Environment

Windows:

```bash
venv\Scripts\activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Verify Java

```bash
java -version
```

## Start MongoDB

```bash
net start MongoDB
```

## Start FastAPI

```bash
uvicorn app.main:app --reload
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

---

# Main API Endpoints

## Assets

```http
POST /assets
GET /assets
GET /assets/{asset_id}
PUT /assets/{asset_id}
DELETE /assets/{asset_id}
GET /assets/{asset_id}/history
```

## Data Sources

```http
POST /data-sources
GET /data-sources
GET /data-sources/{data_source_id}
```

## Market Data

```http
POST /data/ingest
GET /data/query
```

## External Provider Ingestion

```http
POST /ingestion/nasdaq-dataset
POST /ingestion/nasdaq-datatable
```

## Analytics

```http
POST /analytics/yearly-aggregation
POST /analytics/predict-close

GET /analytics/aggregations
GET /analytics/predictions
```

---

# Temporal Data Model

The warehouse implements temporal versioning.

Each update generates a new version while preserving historical records.

Example:

Version 1 → Asset Created

Version 2 → Asset Updated

Version 3 → Asset Updated Again

Historical versions remain accessible through:

```http
GET /assets/{asset_id}/history
```

This approach preserves complete auditability and historical traceability.

---

# Example Workflow

### Step 1

Create Financial Asset

```http
POST /assets
```

### Step 2

Register Data Source

```http
POST /data-sources
```

### Step 3

Ingest Financial Data

```http
POST /data/ingest
```

or

```http
POST /ingestion/nasdaq-datatable
```

### Step 4

Run Analytics

```http
POST /analytics/yearly-aggregation
```

### Step 5

Run Prediction Workflow

```http
POST /analytics/predict-close
```

### Step 6

Retrieve Results

```http
GET /analytics/aggregations
GET /analytics/predictions
```

---

# Example Aggregation Result

```json
{
  "business_year": 2025,
  "record_count": 368,
  "min_close": 189.11,
  "max_close": 225.70,
  "avg_close": 204.73
}
```

---

# Example Prediction Result

```json
{
  "actual_close": 203.93,
  "predicted_close": 201.39
}
```

---

# Educational Concepts Demonstrated

* Data Warehousing
* Temporal Databases
* Data Provenance
* Financial Market Data Management
* Big Data Processing
* Apache Spark
* Spark MLlib
* REST API Design
* External Data Integration
* MCP Integration
* Financial Analytics

---

# Author

Andreea Longodor

Bachelor of Engineering

Financial Market Data Warehouse
