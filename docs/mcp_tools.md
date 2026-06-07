# MCP Tools Documentation

The MCP server exposes read-only warehouse capabilities to LLM clients.

## Tools

### list_assets
Returns paginated current financial assets.

Inputs:
- offset
- limit

### get_asset_details
Returns the latest current version of one asset.

Input:
- asset_id

### get_asset_history
Returns all temporal versions of one asset.

Input:
- asset_id

### list_data_sources
Returns paginated data sources.

Inputs:
- offset
- limit

### get_data_source_details
Returns metadata for one data source.

Input:
- data_source_id

### get_time_series_data
Returns time-series records for one asset and data source in a bounded interval.

Inputs:
- asset_id
- data_source_id
- start_business_date
- end_business_date
- include_attributes
- limit

### get_analytics_aggregations
Returns persisted PySpark aggregation results.

Input:
- limit

### get_predictions
Returns persisted Spark ML prediction results.

Input:
- limit