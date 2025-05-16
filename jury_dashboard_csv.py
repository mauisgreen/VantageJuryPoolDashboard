import streamlit as st
import pandas as pd
import altair as alt

@st.cache_data
def load_data():
    crime_df = pd.read_csv("CrimeCounties.csv")
    demo_df = pd.read_csv("CountyDemographics.csv", skiprows=1)
    demo_df.columns = demo_df.columns.str.strip()  # remove leading/trailing spaces
    demo_df = demo_df.rename(columns={demo_df.columns[0]: "County"})
    pol_df = pd.read_csv("CountyPolitics.csv")
    city_df = pd.read_csv("CityCrimeFinal.csv")
    citypol_df = pd.read_csv("CityPolitics.csv")
    return crime_df, demo_df, pol_df, city_df, citypol_df

col2.metric("Median Earnings (25+)", f"${int(demo_row['Median annual earnings, 25+'].values[0]):,}")

crime_df, demo_df, pol_df, city_df, citypol_df = load_data()

# Sidebar: select county
county_list = sorted(set(demo_df['County'].dropna().unique()))
selected_county = st.sidebar.selectbox("Select a County", county_list)

st.title(f"Jury Dashboard for {selected_county} County")

# --- Demographics ---
st.header("County Demographics")
demo_row = demo_df[demo_df['County'] == selected_county]
if not demo_row.empty:
    col1, col2, col3 = st.columns(3)
    col1.metric("Population", f"{int(demo_row['Population'].values[0]):,}")
    col2.metric("Median Earnings (25+)", f"${int(demo_row['Median annual earnings, 25+ '].values[0]):,}")
    col3.metric("Median Age", demo_row["Median Age"].values[0])

# --- Crime Overview ---
st.header("Crime Statistics")
crime_row = crime_df[crime_df["County"] == selected_county]
if not crime_row.empty:
    crime_chart = pd.DataFrame({
        "Type": ["Violent", "Property"],
        "Rate per 100k": [
            crime_row["ViolentCrimesper100k"].values[0],
            crime_row["PropertyCrimeper100k"].values[0]
        ]
    })
    st.altair_chart(alt.Chart(crime_chart).mark_bar().encode(
        x="Type",
        y="Rate per 100k"
    ), use_container_width=True)

# --- Political Affiliation ---
st.header("County Politics")
pol_row = pol_df[pol_df["County"] == selected_county]
if not pol_row.empty:
    party_chart = pd.DataFrame({
        "Party": ["Democratic", "Republican", "Independent", "Other"],
        "Percent": [
            pol_row["% Democratic"].values[0],
            pol_row["% Republican"].values[0],
            pol_row["% Independent"].values[0],
            pol_row["% Other"].values[0]
        ]
    })
    st.altair_chart(alt.Chart(party_chart).mark_arc().encode(
        theta="Percent",
        color="Party"
    ).properties(title="Political Affiliation"), use_container_width=True)

# --- City Outliers ---
st.header("City Crime Outliers (>100K Population)")
cities = city_df[(city_df["County"] == selected_county) & (city_df["Population"] > 100000)]
if not cities.empty:
    st.dataframe(cities[["City", "Population", "Violent Crime - Rate per 100k", 
                         "VCrimeMed", "VioFlag (+/-1.5 st deviatiations)", 
                         "Property Crime - Rate per 100k", "PropCrimemed", 
                         "PropFlag (+/-1.5 st deviatiations)"]])
else:
    st.info("No major city outliers over 100K in this county.")

# --- Download Summary ---
st.header("Download County Summary")
if not demo_row.empty and not crime_row.empty:
    summary_df = pd.concat([demo_row.reset_index(drop=True), crime_row.reset_index(drop=True)], axis=1)
    st.download_button("Download Summary CSV", summary_df.to_csv(index=False), file_name=f"{selected_county}_summary.csv")