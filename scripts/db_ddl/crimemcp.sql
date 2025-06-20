CREATE TABLE crimemcp (
    id SERIAL PRIMARY KEY,  -- Auto-incrementing primary key

    "Month_Year" VARCHAR(10),
    "Area Type" VARCHAR(100),
    "Borough_SNT" VARCHAR(150),
    "Area name" VARCHAR(150),
    "Area code" VARCHAR(30),
    "Offence Group" VARCHAR(150),
    "Offence Subgroup" VARCHAR(150),
    "Measure" VARCHAR(50),
    "Financial Year" VARCHAR(15),
    "FY_FYIndex" VARCHAR(30),
    "Count" INT,
    "Refresh Date" VARCHAR(15)
);

-- Table description
COMMENT ON TABLE crimemcp IS 
'This table stores monthly crime statistics published by the Metropolitan Police, including offence types, area details, counts, and positive outcomes across different boroughs and time periods.';


COMMENT ON COLUMN crimemcp."Month_Year" IS 
'Indicates the month and year the data corresponds to. Example: "01.06.21". Used to track when the reported offences took place.';

COMMENT ON COLUMN crimemcp."Area Type" IS 
'Describes the geographic level of the data. Example: "Borough". Helps identify the scope or granularity of the area.';

COMMENT ON COLUMN crimemcp."Borough_SNT" IS 
'Refers to the Safer Neighbourhood Team (SNT) or borough covering the area. Example: "Barking and Dagenham". Specifies the policing unit or borough responsible.';

COMMENT ON COLUMN crimemcp."Area name" IS 
'The specific name of the area or policing region. Example: "Barking and Dagenham". Used as a geographic identifier for filtering or analysis.';

COMMENT ON COLUMN crimemcp."Area code" IS 
'A unique code assigned to each area for GIS or administrative tracking. Example: "E09000002". Ensures consistency and avoids ambiguity.';

COMMENT ON COLUMN crimemcp."Offence Group" IS 
'The broader category of the reported offence. Example: "BURGLARY". Used for high-level grouping of similar crime types.';

COMMENT ON COLUMN crimemcp."Offence Subgroup" IS 
'A more specific classification under the offence group. Example: "BURGLARY - BUSINESS AND COMMUNITY". Enables detailed crime type analysis.';

COMMENT ON COLUMN crimemcp."Measure" IS 
'Indicates what is being measured. Example: "Positive Outcomes". Clarifies the metric being reported in the dataset.';

COMMENT ON COLUMN crimemcp."Financial Year" IS 
'The fiscal year in which the data is reported. Example: "fy21-22". Allows financial and annual comparisons across crime statistics.';

COMMENT ON COLUMN crimemcp."FY_FYIndex" IS 
'A coded index or identifier for the financial year. Example: "21-22_01". Simplifies chronological sorting and filtering.';

COMMENT ON COLUMN crimemcp."Count" IS 
'The number of offences or outcomes recorded. Example: 1. Provides the raw data for quantitative analysis.';

COMMENT ON COLUMN crimemcp."Refresh Date" IS 
'The date the data was last updated in the system. Example: "05.06.25". Helps determine how current the dataset is.';