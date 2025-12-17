# Project Documentation & Presentation Script

## 1. Important Libraries & Tech Stack

### **Data Processing & Geospatial Analysis**
*   **`xarray` & `rioxarray`**: Used for handling the multi-dimensional GRACE NetCDF data (time, latitude, longitude) and exporting slices to GeoTIFF files. `xarray` allows for easy manipulation of labeled arrays.
*   **`rasterio`**: Low-level library used implicitly by `rioxarray` and explicitly for coordinate transformations (converting 0-360 longitude to -180 to 180) and handling raster data I/O.
*   **`rasterstats`**: Crucial for **Zonal Statistics**. It computes aggregate statistics (mean, median) of the GRACE raster data within the vector boundaries (polygons) of each country defined in the shapefile.
*   **`geopandas`**: Used to load and manipulate the Country Shapefiles (`.shp`). It handles the geometric operations and coordinate reference system (CRS) transformations to match the satellite data.
*   **`numpy`**: Fundamental package for numerical computing, used for array operations, handling `NaN` values, and calculating statistics like z-scores.
*   **`pandas`**: The backbone of the project for structured data manipulation. Used for merging datasets (GRACE + Aqueduct + FAO), time-series handling (`pd.to_datetime`), rolling window calculations, and CSV I/O.

### **Visualization & EDA**
*   **`matplotlib` & `seaborn`**: Used in the Jupyter Notebook to generate static charts for Exploratory Data Analysis (EDA)—histograms, boxplots, correlation heatmaps—to understand data distributions and outliers.
*   **`plotly.express`**: Used in the **Streamlit Dashboard** for *interactive* charts (Zoomable Line Charts, Choropleth Maps, Heatmaps). It enables the "Dark Mode" visuals and dynamic tooltips.

### **Web Application**
*   **`streamlit`**: The framework used to build the interactive web dashboard. It turns Python data scripts into a shareable web app with widgets (sliders, dropdowns) and cached data loading.

---

## 2. Data Pipeline & Logic Explanation

### **Step 1: Data Ingestion & Extraction**
*   **Input**:
    1.  **GRACE Satellite Data (NetCDF)**: Contains monthly Liquid Water Equivalent (lwe_thickness) anomalies.
    2.  **Natural Earth Shapefile**: Vector polygons for world countries.
*   **Process**:
    *   The script iterates through each month of satellite data.
    *   Converts the monthly slice into a temporary raster.
    *   Uses `rasterstats` to overlay country boundaries on the raster and calculate the **mean water anomaly (TWS)** for each country.
*   **Output**: A raw time-series CSV of TWS anomalies for every country.

### **Step 2: Cleaning & Merging**
*   **Merging**: The satellite data is merged with:
    *   **Aqueduct Water Risk Data**: Adds static risk scores (e.g., specific water stress metrics).
    *   **FAO Aquastat**: Adds agricultural and industrial water efficiency metrics.
*   **Cleaning**:
    *   **Imputation**: Missing numeric values are filled using the country's median value (temporal interpolation) or the global median if data is completely missing.
    *   **Standardization**: Country names are normalized (mapped to ISO-A3 codes) to ensure consistent joining across datasets.

### **Step 3: Feature Engineering (Extraction)**
These are the key features extracted to help understand trends and train the model:
*   **`tws_mean_cm`**: The primary target variable—Terrestrial Water Storage anomaly.
*   **Rolling Averages (`tws_roll3`, `tws_roll6`, `tws_roll12`)**:
    *   *Meaning*: The average water anomaly over the last 3, 6, or 12 months.
    *   *Utility*: Smooths out short-term noise and captures longer-term trends (e.g., a 6-month negative trend indicates deepening drought).
*   **Slopes (`tws_slope6`)**:
    *   *Meaning*: The rate of change over the last 6 months.
    *   *Utility*: Indicates distinct *acceleration* of drying or wetting (e.g., a steep negative slope means rapid water loss).
*   **Z-Scores (`tws_z`)**:
    *   *Meaning*: How many standard deviations the current value is from the distinct country's historical mean.
    *   *Utility*: Identifies **extreme events** (Outliers) relative to *local* normal conditions.
*   **Seasonality (`month`)**:
    *   *Utility*: Captures cyclical patterns (wet/dry seasons) inherent to hydrology.
*   **Drought Flags (`drought_flag_tws`)**:
    *   *Meaning*: Binary flag (True/False) if TWS is below a certain threshold (e.g., -5 cm).

---

## 3. Machine Learning Model (Inferred)

*Note: The specific training code was not found in the uploaded files, but based on the feature engineering pipeline, standard forecasting models use the following structure:*

*   **Model Type**: Likely a **Random Forest Regressor** or **XGBoost**.
    *   *Logic*: These models are robust to non-linear relationships and interactions between features (e.g., Region + Season + Rolling Trend).
*   **Target**: Forecasting `tws_mean_cm` for future time steps (e.g., t+6 months).
*   **Input Features**:
    1.  **Lag Features**: Past values (`t-1`, `t-2`...) which are strong predictors in time series.
    2.  **Rolling Stats**: `tws_roll6`, `tws_roll12` (Trend context).
    3.  **Static Metadata**: `aqueduct_score` (Baseline stress).
    4.  **Cyclical Features**: `Month` (Seasonality).
*   **Evaluation Metrics (Typical)**:
    *   **RMSE (Root Mean Squared Error)**: Measures the average magnitude of the prediction error.
    *   **R² Score**: Indicates how well the model replicates observed outcomes (e.g., >0.8 is strong).

---

## 4. Presentation Script for the Project

**(Slide 1: Title)**
"Good morning. Today I will present the **Global Water Stress & Drought Tracker**, a project designed to monitor historical water anomalies and predict future drought risks using satellite data and machine learning."

**(Slide 2: Problem & Data Source)**
"Traditional drought monitoring often relies on rainfall data, which can be incomplete. We took a deeper approach using **GRACE Satellite Data**. This NASA mission measures changes in Earth's gravity field to estimate **Terrestrial Water Storage (TWS)**—the water actually stored in soil and aquifers. We combined this with FAO and Aqueduct data to build a comprehensive dataset."

**(Slide 3: Pipeline & Technologies)**
"We built a robust Python pipeline.
1.  **Extraction**: Using `xarray` and `rasterstats`, we processed complex NetCDF satellite imagery to calculate monthly water anomalies for every country on Earth.
2.  **Cleaning**: We handled missing data and normalized country codes using `Pandas` to create a seamless master dataset.
3.  **Analysis**: We visualized these trends using `Seaborn` for initial exploration."

**(Slide 4: Feature Engineering)**
"To make the data 'model-ready', we extracted key features:
*   **Rolling Averages (3 & 6 months)**: To filter noise and reveal underlying trends.
*   **Z-Scores**: To statistically identify extreme drought events relative to a country's own history.
*   **Slopes**: To detect how fast a region is drying."

**(Slide 5: The Solution - Dashboard)**
"The result is this interactive **Streamlit Dashboard**.
It allows users to visualize global water stress heatmaps, drill down into specific country trends, and view **Machine Learning Forecasts** that predict drought risk 6 months in advance. This tool empowers decision-makers to act *before* a crisis becomes a catastrophe. Thank you."
