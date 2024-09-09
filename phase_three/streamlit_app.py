import streamlit as st
import pandas as pd
import numpy as np
import joblib
from PIL import Image

# Custom CSS with updated styles
st.markdown("""
    <style>
    .stApp {
        background-color: #2F2F2F;
    }
    .main .block-container {
        color: white;
    }
    .stButton>button {
        color: black;
    }
    .stSelectbox>div>div>div {
        color: black;
    }
    .stSlider label {
        color: white !important;
    }
    h1, h2, h3, h4, h5, h6, .stMarkdown {
        color: white;
    }
    .sidebar .sidebar-content {
        color: white;
    }
    .sidebar .sidebar-content h1,
    .sidebar .sidebar-content h2,
    .sidebar .sidebar-content h3,
    .sidebar .sidebar-content p {
        color: black !important;
    }
    /* Make select boxes for Season, Holiday, and DayType white */
    div[data-baseweb="select"] > div {
        color: white !important;
    }
    /* Style for prediction display */
    .prediction-box {
        background-color: white;
        color: black;
        padding: 10px;
        border-radius: 5px;
        margin-top: 20px;
    }
    .prediction-box .prediction-label {
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# Load the model and related information
model, ref_cols, target = joblib.load("/Users/secret/Desktop/Seoul_bike/MLRegression_SeoulBikeRental/phase_three/exported_model_timo.pkl")

# Load and display the logo in the sidebar
logo = Image.open("bike_icon.png")
st.sidebar.image(logo, width=200)  # Adjust width as needed

st.sidebar.header("About this application")
st.sidebar.info("This app uses a LightGBM model to predict the number of rented bikes in Seoul based on the features listed below")
st.sidebar.header("Features")

# Separate numeric and categorical features
numeric_features = model.named_steps['preprocessor'].transformers_[0][2]
categorical_features = model.named_steps['preprocessor'].transformers_[1][2]

st.sidebar.markdown("**Numeric features:** Hour, Temperature(°C), Humidity(%), Wind speed (m/s), Visibility (10m), Solar Radiation (MJ/m2), Rainfall(mm), Snowfall (cm)")
st.sidebar.markdown("**Categorical features:** Seasons, Holiday, DayType")

# Main content
st.title("Bike Rental Predictor")

# Create input fields for each feature
input_data = {}

# Create sliders for numeric features with appropriate ranges
st.subheader("Numeric Features")
slider_ranges = {
    'Hour': (0, 23, 1),
    'Temperature(°C)': (-20.0, 40.0, 0.1),
    'Humidity(%)': (0, 100, 1),
    'Wind speed (m/s)': (0.0, 20.0, 0.1),
    'Visibility (10m)': (0, 2000, 10),
    'Solar Radiation (MJ/m2)': (0.0, 5.0, 0.01),
    'Rainfall(mm)': (0.0, 100.0, 0.1),
    'Snowfall (cm)': (0.0, 30.0, 0.1)
}

for col in numeric_features:
    min_val, max_val, step = slider_ranges.get(col, (0.0, 100.0, 1.0))  # Default range if not specified
    if isinstance(min_val, int) and isinstance(max_val, int) and isinstance(step, int):
        value = int(min_val)
    else:
        min_val, max_val, step = float(min_val), float(max_val), float(step)
        value = float(min_val)
    input_data[col] = st.slider(f"Select {col}", min_value=min_val, max_value=max_val, value=value, step=step)

# Create input fields for categorical features
st.subheader("Categorical Features")
for col in categorical_features:
    if col == 'Holiday':
        options = ['No Holiday', 'Holiday']
    elif col == 'DayType':
        options = ['Weekend', 'Weekday']
    elif col == 'Seasons':
        options = ['Spring', 'Summer', 'Autumn', 'Winter']
    else:
        # Get the categories from the OneHotEncoder for any other categorical features
        cat_index = list(categorical_features).index(col)
        options = model.named_steps['preprocessor'].named_transformers_['cat'].named_steps['onehot'].categories_[cat_index]
    
    input_data[col] = st.selectbox(f"Select {col}", options=options)

# Create a prediction button
if st.button("Predict Rented Bike Count"):
    # Convert input data to DataFrame
    input_df = pd.DataFrame([input_data])
    
    # Ensure the input DataFrame has the correct dtypes
    for col in categorical_features:
        input_df[col] = input_df[col].astype('category')
    
    # Make prediction
    prediction = model.predict(input_df)[0]
    
    # Ensure prediction is non-negative
    prediction = max(0, prediction)
    
    # Display the prediction
    st.markdown(f"""
    <div class="prediction-box">
        <span class="prediction-label">Predicted {target}:</span> {prediction:.2f}
    </div>
    """, unsafe_allow_html=True)

# Add explanation about negative predictions
st.markdown("""
    **Note on Predictions:**
    The model may occasionally produce negative predictions for certain input combinations. 
    These are automatically adjusted to 0, as negative bike rentals are not possible. 
    If you frequently see 0 predictions, it might indicate unusual or extreme input values.
""")