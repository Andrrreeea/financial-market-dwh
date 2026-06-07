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
* Idempotent ingestion
* Temporal query support

## External Data Ingestion

## Data Provenance

Every record stored in the warehouse contains provenance metadata.

Tracked provenance information includes:

* Source provider
* Data source identifier
* Ingestion timestamp
* API endpoint origin
* Dataset or table code
* Operation type
* Version history

This enables full auditability and traceability of warehouse contents.

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

## Analytics Persistence

Analytical and machine learning results are persisted inside MongoDB.

Collections include:

* analytics_aggregations
* analytics_predictions

This allows analytical workflows to be executed independently from data consumption workflows.

## MCP Integration

The platform exposes warehouse functionality through MCP (Model Context Protocol) tools.

Implemented MCP capabilities include:

* List Financial Assets
* Get Asset Details
* Get Asset History
* Retrieve Time-Series Data
* Retrieve Aggregation Results
* Retrieve Prediction Results
* List Data Sources
* Query Warehouse Metadata

The MCP server acts as an integration layer between the data warehouse and AI agents, enabling grounded responses based on warehouse contents.

# Technology Stack

| API Layer            | FastAPI                 |
| Database             | MongoDB                 |
| Big Data Processing  | Apache Spark            |
| Machine Learning     | Spark MLlib             |
| Programming Language | Python                  |
| Data Model           | Temporal Document Model |
| External Provider    | Nasdaq Data Link        |
| Agent Integration    | MCP                     |
| Data Access Layer    | Repository Pattern      |

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

# Indexing Strategy

To optimize warehouse queries, MongoDB indexes are created for:

* asset_id
* data_source_id
* business_date
* system_time
* is_current
* is_deleted

Indexes improve:

* Asset retrieval
* Historical queries
* Time-series lookups
* Analytics consumption

# Main API Endpoints

## Assets

```http
POST /assets
GET /assets?offset=0&limit=20
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

# Temporal Query Semantics

The warehouse implements bitemporal-inspired concepts using:

* Business Time
* System Time

Business Time represents when an event occurred in the financial domain.

System Time represents when the warehouse recorded the event.

This enables historical reconstruction and auditability of financial market data.

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
* ETL Pipelines
* Financial Time-Series Warehousing
* Apache Spark
* Spark MLlib
* Machine Learning Pipelines
* MCP (Model Context Protocol)
* External Provider Integration
* REST API Architecture

---

# Author

Andreea Longodor

Financial Market Data Warehouse
