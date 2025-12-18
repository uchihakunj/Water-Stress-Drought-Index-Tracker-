# Global Water Stress & Drought Tracker
## streamlit Cloud:https://water-stress-drought-index-tracker.streamlit.app/#global-water-anomalies-tracker-july-2025-visualizing-gravitational-satellite-data-to-identify-regional-drought-severity

**Monitor historical water anomalies and predict future drought risks.**

This dashboard provides an interactive interface to explore the "Water Stress & Drought Index" dataset. It integrates satellite-derived water storage anomalies (NASA GRACE) with baseline water risk scores (WRI Aqueduct) to monitor global drought conditions.

## Features

1.  **Global Map**: Visualizes terrestrial water storage anomalies on an interactive world map.
2.  **Top Risks**: Automatically highlights the top 15 countries with the lowest water storage.
3.  **Country & Date Filters**: Drill down into specific regions and time periods.
4.  **Deep Dive Analysis**:
    *   **Time Series**: Track water storage changes over decades.
    *   **Heatmaps**: Visualize drought intensity by year.
    *   **Regional Distribution**: Compare water stress across different regions.
5.  **Forecasting**: Uses machine learning to predict drought risks for the next 6 months.

## How to Run Locally

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/uchihakunj/Water-Stress-Drought-Index-Tracker.git
    cd Water-Stress-Drought-Index-Tracker
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the application:**
    ```bash
    streamlit run app.py
    ```

## Deployment

This app is designed to be deployed on **Streamlit Cloud**.

1.  Fork or clone this repository to your GitHub.
2.  Sign in to [Streamlit Cloud](https://share.streamlit.io/).
3.  Click **New app**.
4.  Select this repository and point to `app.py`.
5.  Click **Deploy**.
