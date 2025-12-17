--Streamlit Dashboard--
      
Project: Global Water Stress & Drought Index Tracker App 
Author: Thakur Raghwendra Singh Kunjam 
Date: 

--Description-- 
This dashboard provides an interactive interface to explore the "Water Stress & Drought Index" dataset. It integrates satellite-derived water storage anomalies (NASA GRACE) with baseline water risk scores (WRI Aqueduct) to monitor global drought conditions.
Features
1. Data Upload: Users can upload the processed CSV dataset directly.
2. Dynamic Filtering: Sidebar controls allow users to filter data by specific countries and date ranges (Bonus Task).
3. Summary Metrics: Automatically calculates total records, countries tracked, and date coverage.
4. Visualizations:
o Time Series Line Chart: Tracks 'tws_mean_cm' (Water Storage Anomalies) over time to identify trends.
o Scatter Plot: Correlates baseline water stress (Aqueduct Score) with real-time anomalies.
o Bar Chart: Quantifies the number of drought months flagged for selected countries.

--How to Run--
1. Ensure Python and the required libraries are installed: pip install streamlit pandas plotly
2. Navigate to the directory containing 'app.py' in your terminal.
3. Run the application: streamlit run app.py
4. The dashboard will open in your default web browser (usually at http://localhost:8501).

--Dependencies--
* streamlit
* pandas
* plotly
