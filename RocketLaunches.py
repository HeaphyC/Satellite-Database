import pandas as pd
import numpy as np
import openpyxl as op
import streamlit as st
import plotly.express as px
import altair as alt
import re

st.set_page_config(page_title="Rocket Launches",
                   page_icon=":satellite:",
                   layout="wide"
)

path = r"https://github.com/HeaphyC/Satellite-Database/blob/master/UCS-Satellite-Database-1-1-2023.xlsx"
@st.cache_data
def get_data_from_spreadsheet():
    df = pd.read_csv(path, na_values=['nan', 'NA', ''])
    df['Power (watts)'] = df['Power (watts)'].astype(str)
    df['Power (watts)'] = df['Power (watts)'].str.replace(',', '')
    df['Power (watts)'] = df['Power (watts)'].apply(lambda x: re.findall(r'\d+', x)[0] if re.findall(r'\d+', x) else x)
    df['Power (watts)'] = pd.to_numeric(df['Power (watts)'], errors='coerce')
    df['Launch Mass (kg.)'] = df['Launch Mass (kg.)'].astype(str)
    df['Launch Mass (kg.)'] = df['Launch Mass (kg.)'].str.replace(',', '')
    df['Launch Mass (kg.)'] = df['Launch Mass (kg.)'].apply(lambda x: re.findall(r'\d+', x)[0] if re.findall(r'\d+', x) else x)
    df['Launch Mass (kg.)'] = pd.to_numeric(df['Launch Mass (kg.)'], errors='coerce')
    df['Purpose'] = df['Purpose'].astype(str)
    df['Purpose'] = df['Purpose'].str.replace(' ', '')
    df['Class of Orbit'] = df['Class of Orbit'].astype(str)
    df['Class of Orbit'] = df['Class of Orbit'].str.replace('o', 'O')
    return df
df = get_data_from_spreadsheet()

## SIDEBAR

st.sidebar.header("Please Filter Here")

## Sidebar range slider widget to select a range for the Mass
min_mass = 0
max_mass = int(df["Launch Mass (kg.)"].max())
mass_placeholder_value = max_mass + 1
df["Launch Mass (kg.)"] = df["Launch Mass (kg.)"].fillna(mass_placeholder_value)
mass_min_range, mass_max_range = st.sidebar.slider(
    "Select a range for the Launch Mass:",
    min_value=min_mass,
    max_value=max_mass,
    value=(min_mass, max_mass),
)

## Sidebar range slider widget to select a range for the Power
min_power = 0
max_power = int(df["Power (watts)"].max())
power_placeholder_value = max_power + 1
df["Power (watts)"] = df["Power (watts)"].fillna(power_placeholder_value)
power_min_range, power_max_range = st.sidebar.slider(
    "Select a range for the Power:",
    min_value=min_power,
    max_value=max_power,
    value=(min_power, max_power),
)

Orbit = st.sidebar.multiselect(
    "Select the Class of Orbit:",
    options=df["Class of Orbit"].unique(),
    default=df["Class of Orbit"].unique(),
)

unique_options=df["Purpose"].unique()

def split_options(option):
    if '/' in option:
        sub_options = [x.strip() for x in option.split('/')]
        splitted_options = []
        for sub_option in sub_options:
            splitted_options.extend(split_options(sub_option))
        return splitted_options
    else:
        return [option]

filtered_options = []
for option in unique_options:
    splitted_options = split_options(option)
    filtered_options.extend(splitted_options)

filtered_df_purpose = df[df['Purpose'].apply(lambda x: any(option in x for option in filtered_options))]
Purpose = st.sidebar.multiselect(
    "Select the Purpose:",
    options=filtered_options,
    default=filtered_options,
)

Country = st.sidebar.multiselect(
    "Select the Country:",
    options=df["Country of Operator/Owner"].unique(),
    default=df["Country of Operator/Owner"].unique(),
)

# df_selection = df.query(
#     "`Country of Operator/Owner` == @Country & `Purpose` == @Purpose & `Class of Orbit` == @Orbit"
# )

# df_selection = df[(df["Launch Mass (kg.)"] >= min_range) & (df["Launch Mass (kg.)"] <= max_range)]
# df_selection = df[(df["Power (watts)"] >= min_range) & (df["Power (watts)"] <= max_range)]

df_selection = df.query(
    "`Country of Operator/Owner` == @Country"
    " and `Purpose` == @Purpose"
    " and `Class of Orbit` in @Orbit"
    " and ((@mass_min_range <= `Launch Mass (kg.)` <= @mass_max_range) or (@mass_min_range == @min_mass and @mass_max_range == @max_mass))"
    " and ((@power_min_range <= `Power (watts)` <= @power_max_range) or (@power_min_range == @min_power and @power_max_range == @max_power))"
)

df_selection["Launch Mass (kg.)"] = df_selection["Launch Mass (kg.)"].replace(mass_placeholder_value, np.nan)
df_selection["Power (watts)"] = df_selection["Power (watts)"].replace(power_placeholder_value, np.nan)

## MAINPAGE

st.title(":satellite: Satellite Info")
st.markdown("##")

## Useful general stats

Average_launch_mass = round(df_selection["Launch Mass (kg.)"].mean(), 1)
Average_power = round(df_selection["Power (watts)"].mean(), 1)

left_column, right_column = st.columns(2)
with left_column:
    st.subheader(":rocket: Average Launch Mass:")
    st.subheader(f"{Average_launch_mass}kg")
with right_column:
    st.subheader(":battery: Average Power:")
    st.subheader(f"{Average_power}Watts")

st.dataframe(df)

st.dataframe(df_selection)

## MASS BY PURPOSE [BAR CHART] (couldn't get it to work)

# mass_by_orbit = (
#     df_selection.groupby(by=["Class of Orbit"]).sum()[["Launch Mass (kg.)"]].sort_values(by="Launch Mass (kg.)")
# )
# fig_orbit_mass = px.bar(
#     mass_by_orbit,
#     x="Launch Mass (kg.)",
#     y=mass_by_orbit.index,
#     orientation="h",
#     title="<b>Orbit Mass</b>",
#     color_discrete_sequence=["#0083B8"] * len(mass_by_orbit),
#     template="plotly_white",
# )

# st.plotly_chart(fig_orbit_mass)

Power_bar = alt.Chart(df_selection).mark_bar().encode(
    alt.X('Power (watts)', bin=True),
    y='count()')
st.altair_chart(Power_bar, use_container_width=True)

Mass_bar = alt.Chart(df_selection).mark_bar().encode(
    alt.X("Launch Mass (kg.)", bin=True),
    y='count()')
st.altair_chart(Mass_bar, width=0.8)

## STYLE ADJUSTMENTS

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
