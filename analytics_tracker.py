import streamlit as st
import streamlit_analytics

# Initialize the streamlit-analytics tracker
streamlit_analytics.init()

# Track user interactions with the app
st.analytics(name="My App")

# Display a bar chart of the tracking results
st.analytics_plot()
