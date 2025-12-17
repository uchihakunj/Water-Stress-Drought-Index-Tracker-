import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. Page Configuration ---
st.set_page_config(
    page_title="Global Water Stress Tracker",
    page_icon="bx-water",
    layout="wide"
)

# --- 2. Load Data Logic ---
@st.cache_data
def load_data(file_path_or_buffer):
    try:
        df = pd.read_csv(file_path_or_buffer)
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        return df
    except Exception as e:
        return None

# --- 3. Sidebar & Data Loading ---
st.sidebar.title("Data & Controls")

# Auto-load paths (Assume app.py is in 'Streamlit_Dashboard/' and OUTPUTS is parallel)
base_dir = os.path.dirname(os.path.abspath(__file__))
default_history_path = os.path.join(base_dir, "drought_water_stress_master_monthly_clean.csv")
default_forecast_path = os.path.join(base_dir, "drought_risk_forecasts.csv")

# Initialize session state for data source
if 'use_sample_data' not in st.session_state:
    st.session_state.use_sample_data = True

data_source = st.sidebar.radio("Data Source", ["Auto-Load (Project Data)", "Upload Custom CSV"], index=0)

df = None
forecast_df = None

if data_source == "Auto-Load (Project Data)":
    if os.path.exists(default_history_path):
        df = load_data(default_history_path)
        st.sidebar.success("Historical Data Loaded")
    else:
        st.sidebar.error(f"Default file not found: {default_history_path}")
    
    if os.path.exists(default_forecast_path):
        forecast_df = load_data(default_forecast_path)
        if forecast_df is not None and 'forecast_date' in forecast_df.columns:
            forecast_df['forecast_date'] = pd.to_datetime(forecast_df['forecast_date'])
        st.sidebar.success("Forecast Data Loaded")
    else:
        st.sidebar.warning("Default forecast file not found.")

else:
    uploaded_file = st.sidebar.file_uploader("Upload Historical CSV", type=["csv"], key="history")
    uploaded_forecast = st.sidebar.file_uploader("Upload Forecast CSV", type=["csv"], key="forecast")
    
    if uploaded_file:
        df = load_data(uploaded_file)
    if uploaded_forecast:
        forecast_df = load_data(uploaded_forecast)
        if forecast_df is not None and 'forecast_date' in forecast_df.columns:
            forecast_df['forecast_date'] = pd.to_datetime(forecast_df['forecast_date'])

# --- 4. Main Dashboard Logic ---
if df is not None:
    # --- Global Title ---
    st.title("Global Water Stress & Drought Tracker")
    st.markdown("### Monitor historical water anomalies and predict future drought risks.")

    # --- Sidebar Filters ---
    st.sidebar.divider()
    st.sidebar.subheader("Filter Options")
    
    # Filter by Country
    all_countries = sorted(df['country'].dropna().unique())
    default_selection = ["Afghanistan", "India", "United States", "Brazil", "Australia"]
    # Filter defaults to valid countries only
    default_selection = [c for c in default_selection if c in all_countries] 
    if not default_selection: 
        default_selection = all_countries[:3]

    selected_countries = st.sidebar.multiselect(
        "Select Countries", 
        all_countries, 
        default=default_selection
    )

    # Filter by Date Range
    min_date = df['date'].min().date()
    max_date = df['date'].max().date()
    # Default to last 5 years for better initial view if data is huge
    initial_start = max(min_date, max_date.replace(year=max_date.year - 5))
    
    date_range = st.sidebar.slider(
        "Select Date Range",
        min_value=min_date,
        max_value=max_date,
        value=(initial_start, max_date)
    )

    # Apply Filters
    # Note: Global map logic often needs the full dataset for a specific date, so we separate filtering logic.
    mask_date = (df['date'].dt.date >= date_range[0]) & (df['date'].dt.date <= date_range[1])
    mask_country = df['country'].isin(selected_countries)
    
    filtered_df = df[mask_date & mask_country]
    full_date_filtered_df = df[mask_date] # For comparison with unselected countries if needed

    # --- TABS ---
    tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Data Explorer", "Deep Dive Analysis", "Forecasts"])

    # === TAB 1: OVERVIEW ===
    with tab1:
        # KPI Section
        latest_date = df['date'].max()
        latest_df = df[df['date'] == latest_date]
        
        col1, col2, col3, col4 = st.columns(4)
        
        # 1. Global Avg TWS
        global_avg_tws = latest_df['tws_mean_cm'].mean()
        col1.metric("Global Avg Water Storage", f"{global_avg_tws:.2f} cm", delta="From Baseline (0)", delta_color="normal" if global_avg_tws > 0 else "inverse")
        
        # 2. Countries in Drought
        drought_threshold = -5
        drought_countries = latest_df[latest_df['tws_mean_cm'] < drought_threshold]
        col2.metric("Countries in High Deficit", f"{len(drought_countries)}", delta=f"< {drought_threshold}cm TWS", delta_color="inverse")
        
        # 3. Worst Hit Country
        if not latest_df.empty:
            worst_hit = latest_df.nsmallest(1, 'tws_mean_cm').iloc[0]
            col3.metric("Worst Hit Country", worst_hit['country'], f"{worst_hit['tws_mean_cm']:.2f} cm", delta_color="inverse")
        else:
            col3.metric("Worst Hit Country", "N/A")

        # 4. Total Tracked
        col4.metric("Total Countries Tracked", df['country'].nunique())

        st.divider()

        # Global Map
        st.subheader(f"Global Water Storage Anomalies ({latest_date.strftime('%B %Y')})")
        
        # Use simple toggle for date
        map_view_date = st.slider("Select Month for Map View", min_value=min_date, max_value=max_date, value=max_date, format="MMM YYYY")
        map_df = df[df['date'].dt.date == map_view_date]
        
        if not map_df.empty:
            fig_map = px.choropleth(
                map_df,
                locations="iso_a3",
                color="tws_mean_cm",
                hover_name="country",
                hover_data=['aqueduct_label'],
                color_continuous_scale="RdBu", 
                range_color=[-15, 15],
                labels={'tws_mean_cm': 'TWS Anomaly (cm)'},
                template="plotly_dark"
            )
            fig_map.update_layout(
                geo=dict(showframe=False, showcoastlines=True, projection_type='natural earth'),
                margin={"r":0,"t":0,"l":0,"b":0},
                height=500
            )
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.warning("No data available for this specific month.")

        # Top Risks Table
        st.subheader("Top 15 Countries with Lowest Water Storage")
        if not map_df.empty:
            risk_table = map_df[['country', 'tws_mean_cm', 'aqueduct_label']].sort_values('tws_mean_cm').head(15).reset_index(drop=True)
            # Add some styling or progress bar
            st.dataframe(
                risk_table.style.bar(subset=['tws_mean_cm'], color=['#d65f5f', '#5fba7d'], align='mid', vmin=-20, vmax=20)
                          .format({'tws_mean_cm': "{:.2f}"}),
                use_container_width=True
            )

    # === TAB 2: DATA EXPLORER (EDA) ===
    with tab2:
        st.subheader("Interactive EDA & Data Health")
        st.markdown("Explore the raw data structure, statistics, and distributions.")
        
        eda_tabs = st.tabs(["Data Structure & Health", "Statistics", "Distributions & Relationships"])
        
        with eda_tabs[0]:
            st.markdown("#### 1. Dataset Preview")
            st.dataframe(df.head())
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("#### 2. Data Info")
                st.write(f"**Rows:** {df.shape[0]}")
                st.write(f"**Columns:** {df.shape[1]}")
                st.write("**Column Types:**")
                st.dataframe(df.dtypes.astype(str), height=200)
            
            with c2:
                st.markdown("#### 3. Missing Values")
                nulls = df.isnull().sum()
                if nulls.sum() > 0:
                    st.bar_chart(nulls)
                    st.write("Columns with missing values:", nulls[nulls > 0])
                else:
                    st.success("No missing values detected in the clean dataset.")
                    
                st.markdown("#### 4. Duplicates")
                dupes = df.duplicated().sum()
                if dupes > 0:
                    st.warning(f"Found {dupes} duplicate rows.")
                else:
                    st.success("No duplicate rows found.")

        with eda_tabs[1]:
            st.markdown("#### Descriptive Statistics")
            st.dataframe(df.describe())
            
            st.markdown("#### Categorical Summary")
            cat_cols = df.select_dtypes(include=['object']).columns
            if len(cat_cols) > 0:
                selected_cat = st.selectbox("Select Categorical Column", cat_cols)
                st.write(df[selected_cat].value_counts())
                fig_cat = px.bar(df[selected_cat].value_counts(), title=f"Count of {selected_cat}", template="plotly_dark")
                st.plotly_chart(fig_cat, use_container_width=True)

        with eda_tabs[2]:
            st.markdown("#### Distributions & Outliers")
            num_cols = df.select_dtypes(include=['float64', 'int64']).columns
            target_col = st.selectbox("Select Feature to Visualize", num_cols, index=list(num_cols).index('tws_mean_cm') if 'tws_mean_cm' in num_cols else 0)
            
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                fig_hist = px.histogram(df, x=target_col, nbins=50, title=f"Histogram of {target_col}", marginal="box", template="plotly_dark")
                st.plotly_chart(fig_hist, use_container_width=True)
            with col_d2:
                fig_box = px.box(df, y=target_col, title=f"Boxplot of {target_col} (Outlier Detection)", template="plotly_dark")
                st.plotly_chart(fig_box, use_container_width=True)
                
            st.divider()
            st.markdown("#### Correlations")
            if len(num_cols) > 1:
                corr_matrix = df[num_cols].corr()
                fig_corr = px.imshow(corr_matrix, text_auto=True, color_continuous_scale='RdBu', title="Correlation Matrix", template="plotly_dark")
                st.plotly_chart(fig_corr, use_container_width=True)
            
            st.divider()
            st.markdown("#### Relationships (Scatter)")
            if len(num_cols) > 1:
                x_axis = st.selectbox("X Axis", num_cols, index=0)
                y_axis = st.selectbox("Y Axis", num_cols, index=1 if len(num_cols) > 1 else 0)
                color_dim = st.selectbox("Color By (Optional)", [None] + list(cat_cols))
                
                fig_scat_eda = px.scatter(df, x=x_axis, y=y_axis, color=color_dim, title=f"{x_axis} vs {y_axis}", opacity=0.6, template="plotly_dark")
                st.plotly_chart(fig_scat_eda, use_container_width=True)


    # === TAB 3: DEEP DIVE ===
    with tab3:
        st.subheader("Time Series Analysis")
        
        if not filtered_df.empty:
            # Line Chart
            fig_line = px.line(
                filtered_df, 
                x='date', 
                y='tws_mean_cm', 
                color='country',
                title="Terrestrial Water Storage Anomalies Over Time",
                labels={'tws_mean_cm': 'TWS Anomaly (cm)', 'date': 'Year'},
                template="plotly_dark"
            )
            fig_line.add_hline(y=0, line_dash="solid", line_color="black", opacity=0.3)
            fig_line.add_hrect(y0=-100, y1=-5, line_width=0, fillcolor="red", opacity=0.05, annotation_text="Drought Zone")
            st.plotly_chart(fig_line, use_container_width=True)
            
            st.divider()
            
            c1, c2 = st.columns(2)
            
            # Heatmap Analysis (Year vs Country)
            with c1:
                st.subheader("Drought Intensity Heatmap")
                # Prepare data for heatmap: average TWS per year per country
                heatmap_df = filtered_df.copy()
                heatmap_df['Year'] = heatmap_df['date'].dt.year
                heatmap_data = heatmap_df.groupby(['country', 'Year'])['tws_mean_cm'].mean().reset_index()
                
                fig_heat = px.density_heatmap(
                    heatmap_data, 
                    x='Year', 
                    y='country', 
                    z='tws_mean_cm',
                    histfunc='avg',
                    color_continuous_scale='RdBu',
                    range_color=[-15, 15],
                    title="Avg TWS Anomaly by Year",
                    template="plotly_dark"
                )
                st.plotly_chart(fig_heat, use_container_width=True)

            # Regional Distribution
            with c2:
                st.subheader("Regional Impact")
                if 'aqueduct_wb_region' in filtered_df.columns:
                    fig_box = px.box(
                        full_date_filtered_df, # Use full dataset for selected dates to show broader context
                        x='aqueduct_wb_region',
                        y='tws_mean_cm',
                        color='aqueduct_wb_region',
                        title=f"Water Storage Distribution by Region ({date_range[0]} - {date_range[1]})",
                        points=False # Too many points can be slow
                    )
                    fig_box.update_layout(showlegend=False)
                    st.plotly_chart(fig_box, use_container_width=True)
                elif 'aqueduct_label' in filtered_df.columns:
                     fig_box = px.box(
                        full_date_filtered_df,
                        x='aqueduct_label',
                        y='tws_mean_cm',
                        color='aqueduct_label',
                         category_orders={"aqueduct_label": ["Low (<10%)", "Low-Medium (10-20%)", "Medium-High (20-40%)", "High (40-80%)", "Extremely High (>80%)"]},
                        title="Water Storage vs Baseline Stress Level"
                    )
                     st.plotly_chart(fig_box, use_container_width=True)

    # === TAB 4: FORECASTS ===
    with tab4:
        if forecast_df is not None:
            st.subheader("6-Month Drought Prediction")
            
            # Prepare Forecast Data
            # Map ISO to Country Name if needed
            if 'country_name' not in forecast_df.columns and 'iso_a3' in df.columns:
                iso_map = df[['iso_a3', 'country']].drop_duplicates().set_index('iso_a3')['country'].to_dict()
                # Simple heuristic: if forecast country code is 3 letters upper, assume ISO
                sample_val = str(forecast_df['country'].iloc[0])
                if len(sample_val) == 3 and sample_val.isupper():
                     forecast_df['country_name'] = forecast_df['country'].map(iso_map).fillna(forecast_df['country'])
                else:
                     forecast_df['country_name'] = forecast_df['country']
            elif 'country_name' not in forecast_df.columns:
                 forecast_df['country_name'] = forecast_df['country']

            # Filter Forecast
            forecast_filtered = forecast_df[forecast_df['country_name'].isin(selected_countries)]
            
            if not forecast_filtered.empty:
                # Combine recent history + forecast for chart
                # Get last 24 months of history for context
                history_end_date = df['date'].max()
                lookback_date = history_end_date - pd.DateOffset(months=24)
                
                recent_history = df[
                    (df['country'].isin(selected_countries)) & 
                    (df['date'] >= lookback_date)
                ][['country', 'date', 'tws_mean_cm']].copy()
                recent_history['Type'] = 'Historical'
                
                forecast_plot = forecast_filtered[['country_name', 'forecast_date', 'predicted_tws']].rename(
                    columns={'country_name': 'country', 'forecast_date': 'date', 'predicted_tws': 'tws_mean_cm'}
                )
                forecast_plot['Type'] = 'Forecast'
                
                combined_df = pd.concat([recent_history, forecast_plot], ignore_index=True)
                
                # Visualization
                fig_forecast = px.line(
                    combined_df,
                    x='date',
                    y='tws_mean_cm',
                    color='country',
                    line_dash='Type',
                    markers=True,
                    title="Projected Water Storage Trends",
                    labels={'tws_mean_cm': 'TWS Anomaly (cm)', 'date': 'Date'},
                    template="plotly_dark"
                )
                
                # Add "Today" Line
                fig_forecast.add_vline(x=history_end_date.timestamp() * 1000, line_dash="dot", annotation_text="Today")
                fig_forecast.add_hrect(y0=-100, y1=-5, line_width=0, fillcolor="red", opacity=0.1, annotation_text="High Risk")

                st.plotly_chart(fig_forecast, use_container_width=True)

                # Forecast Table
                st.subheader("Forecast Summary Table")
                pivot_forecast = forecast_filtered.pivot(index='country_name', columns='forecast_date', values='predicted_tws')
                st.dataframe(pivot_forecast.style.background_gradient(cmap='RdBu', vmin=-10, vmax=10).format("{:.2f}"))
                
            else:
                st.info(f"No forecast data available for: {', '.join(selected_countries)}")
        
        else:
            st.info("No forecast file loaded. Upload one in the sidebar or ensure 'drought_risk_forecasts.csv' is in the OUTPUTS folder.")

else:
    st.info("Please load data to begin.")
    st.image("https://cdn.dribbble.com/users/2069402/screenshots/5696013/media/4e17666ea309192aa62f7902d184eb77.gif", width=300) # Optional aesthetic placeholder