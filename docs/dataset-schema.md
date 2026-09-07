# Dataset Schema and Provenance

## Purpose

The fare dataset supports a supervised regression target named `reference_fare`. It is not a claim that every observed fare is official. Source provenance is mandatory on every row.

## Fare observation columns

| Column | Type | Required | Description |
|---|---|---:|---|
| `observation_id` | UUID/string | yes | Stable row identifier. |
| `observed_at` | ISO datetime | yes | When the fare was observed or generated. |
| `city` | string | yes | `Hyderabad` for MVP. |
| `source_location_id` | UUID/string | yes | Internal location reference. |
| `destination_location_id` | UUID/string | yes | Internal location reference. |
| `source_zone` | string | yes | Normalized Hyderabad zone. |
| `destination_zone` | string | yes | Normalized Hyderabad zone. |
| `vehicle_type` | enum | yes | `auto`, `cab`, `bus`, `metro`, or `other`. |
| `distance_km` | float | yes | Route distance; must be greater than 0. |
| `duration_min` | float | yes | Estimated/observed duration; must be greater than 0. |
| `hour` | integer | yes | Local hour from 0 to 23. |
| `day_of_week` | integer | yes | ISO weekday from 1 to 7. |
| `weekend_flag` | boolean | yes | Derived from day of week. |
| `traffic_level` | enum | yes | `low`, `medium`, `high`, or `unknown`. |
| `weather_condition` | enum | no | Normalized context or `unknown`. |
| `passengers` | integer | yes | Positive passenger count. |
| `reference_fare` | decimal | yes | Regression target in INR; must be non-negative. |
| `fare_currency` | string | yes | `INR` for MVP. |
| `source_type` | enum | yes | `official`, `public`, `team_collected`, `synthetic_demo`. |
| `source_reference` | string | no | URL, document ID, collection batch, or generator version. |
| `is_verified` | boolean | yes | Human/data steward verification status. |
| `quality_flags` | array/string | no | Missing, outlier, duplicate, or conflict flags. |
| `collection_method` | string | yes | Import, survey, API, manual entry, or generator. |

## Source rules

- `official`: use only when the team can point to a public official rule or document and record its reference.
- `public`: open data or legally usable public source with attribution.
- `team_collected`: observations collected by the team with date and method.
- `synthetic_demo`: generated values used for UI/demo plumbing; never report them as real-world statistics.

Training reports must include row counts by `source_type`, the date range, missing-value counts, and the train/validation/test split rule.

## Sample CSV contract

The first sample file should use this header and include only clearly labelled demo rows:

```csv
observation_id,observed_at,city,source_location_id,destination_location_id,source_zone,destination_zone,vehicle_type,distance_km,duration_min,hour,day_of_week,weekend_flag,traffic_level,weather_condition,passengers,reference_fare,fare_currency,source_type,source_reference,is_verified,quality_flags,collection_method
```

## Preprocessing and split strategy

1. Validate types, ranges, enums, and foreign location references.
2. Normalize categorical values and derive `weekend_flag` from `day_of_week`.
3. Deduplicate by source reference, observation time, origin, destination, and vehicle where appropriate.
4. Keep a provenance column through preprocessing.
5. Split by time, not random row only: oldest data for training, a later period for validation, and the most recent period for test. If the dataset is too small, document the limitation rather than inventing confidence.
6. Fit preprocessing on training data only.
7. Compare Linear Regression, Random Forest, and XGBoost using MAE, RMSE, and R2. Save the selected model, feature schema, and metrics artifact.

## Quality checks

- No negative distance, duration, passenger count, or fare.
- Source and destination cannot be identical.
- `hour` is 0-23 and `day_of_week` is 1-7.
- `weekend_flag` agrees with day of week.
- Currency is `INR`.
- Unknown categories are counted and reviewed.
- Outliers are flagged, not silently deleted.
- Synthetic records are excluded from claims about real-world performance and are visibly labelled in demos.
