import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Use layout="wide" to make better use of screen space
st.set_page_config(
    page_title="Titanic Explorer",
    page_icon="🚢",
    layout="wide"
)

st.title("🚢 Titanic Dataset Explorer")
st.markdown("Explore passenger data from the Titanic disaster")

# Load the data
df = sns.load_dataset('titanic')

# ===== INTERACTIVE FILTERS IN SIDEBAR =====
with st.sidebar:
    st.header("Filters")
    
    selected_class = st.multiselect(
        "Select Passenger Class:",
        options=sorted(df['pclass'].unique()),
        default=sorted(df['pclass'].unique())
    )
    
    age_min, age_max = st.slider(
        "Select age Range:",
        min_value=int(df['age'].min()),
        max_value=int(df['age'].max()),
        value=(int(df['age'].min()), int(df['age'].max()))
    )
    
    selected_sex = st.radio(
        "Select Gender:",
        options=["All", "male", "female"],
        index=0
    )
    
    selected_port = st.selectbox(
        "Embarkation Port:",
        options=["All"] + sorted(df['embarked'].dropna().unique().tolist()),
        index=0
    )
    
    survivors_only = st.checkbox(
        "Show Survivors Only",
        value=False
    )
    
    min_fare = st.number_input(
        "Minimum Fare ($):",
        min_value=0.0,
        max_value=float(df['fare'].max()),
        value=0.0,
        step=10.0
    )
    
    # Text input for searching across text columns
    text_search = st.text_input(
        "Search Text:",
        value="",
        placeholder="Search class, group, port..."
    )

# ===== APPLY FILTERS =====
filtered_df = df[
    (df['pclass'].isin(selected_class)) &
    (df['age'] >= age_min) &
    (df['age'] <= age_max) &
    (df['fare'] >= min_fare)
]

if selected_sex != "All":
    filtered_df = filtered_df[filtered_df['sex'] == selected_sex]

if selected_port != "All":
    filtered_df = filtered_df[filtered_df['embarked'] == selected_port]

if survivors_only:
    filtered_df = filtered_df[filtered_df['survived'] == 1]

if text_search:
    # Search across multiple text columns
    mask = (
        filtered_df['who'].astype(str).str.contains(text_search, case=False, na=False) |
        filtered_df['class'].astype(str).str.contains(text_search, case=False, na=False) |
        filtered_df['embark_town'].astype(str).str.contains(text_search, case=False, na=False) |
        filtered_df['deck'].astype(str).str.contains(text_search, case=False, na=False)
    )
    filtered_df = filtered_df[mask]

# ===== DISPLAY KEY METRICS =====
st.subheader("Key Metrics")
metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

with metric_col1:
    st.metric("Total Passengers", len(filtered_df))

with metric_col2:
    survival_rate = (filtered_df['survived'].sum() / len(filtered_df) * 100)
    st.metric("Survival Rate", f"{survival_rate:.1f}%")

with metric_col3:
    avg_age = filtered_df['age'].mean()
    st.metric("Average age", f"{avg_age:.1f}")

with metric_col4:
    avg_fare = filtered_df['fare'].mean()
    st.metric("Average Fare", f"${avg_fare:.2f}")

# ===== ORGANIZE CONTENT IN TABS =====
tab1, tab2, tab3 = st.tabs(["📊 Data", "📈 Visualizations", "ℹ️ Details"])

# TAB 1: RAW DATA
with tab1:
    st.subheader("Dataset")
    st.write(f"Showing {len(filtered_df)} of {len(df)} passengers")
    st.dataframe(filtered_df, use_container_width=True)

# TAB 2: VISUALIZATIONS
with tab2:
    st.subheader("Visualizations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Survival by Passenger Class**")
        fig, ax = plt.subplots(figsize=(6, 4))
        survival_by_class = filtered_df.groupby('pclass')['survived'].mean()
        survival_by_class.plot(kind='bar', ax=ax, color='steelblue')
        ax.set_ylabel('Survival Rate')
        ax.set_xlabel('Passenger Class')
        plt.xticks(rotation=0)
        st.pyplot(fig)
    
    with col2:
        st.write("**age Distribution**")
        fig, ax = plt.subplots(figsize=(6, 4))
        filtered_df['age'].hist(bins=20, ax=ax, color='coral', edgecolor='black')
        ax.set_xlabel('age')
        ax.set_ylabel('Count')
        st.pyplot(fig)
    
    st.write("**Survival by Gender**")
    fig, ax = plt.subplots(figsize=(8, 4))
    survival_by_sex = filtered_df.groupby('sex')['survived'].value_counts().unstack()
    survival_by_sex.plot(kind='bar', ax=ax)
    ax.set_ylabel('Count')
    ax.set_xlabel('Gender')
    ax.legend(['Did Not Survive', 'Survived'])
    plt.xticks(rotation=0)
    st.pyplot(fig)

# TAB 3: ADDITIONAL DETAILS
with tab3:
    st.subheader("Additional Information")
    
    # Expander 1: Statistics
    with st.expander("📊 View Data Statistics"):
        st.write("**Descriptive Statistics:**")
        st.dataframe(filtered_df.describe())
    
    # Expander 2: Correlation Matrix
    with st.expander("🔗 View Correlation Matrix"):
        st.write("**Correlation Matrix:**")
        numeric_cols = filtered_df.select_dtypes(include=['int64', 'float64']).columns
        correlation_matrix = filtered_df[numeric_cols].corr()
        
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', ax=ax)
        st.pyplot(fig)
    
    # Expander 3: About the dataset
    with st.expander("📖 About This Dataset"):
        st.write("""
        **The Titanic Dataset**
        
        This dataset contains information about passengers on the RMS Titanic, which sank on April 15, 1912.
        
        **Column Descriptions:**
        - **survived**: Whether the passenger survived (0 = No, 1 = Yes)
        - **pclass**: Ticket class (1 = 1st, 2 = 2nd, 3 = 3rd)
        - **sex**: Passenger's gender
        - **age**: Age in years
        - **sibsp**: Number of siblings/spouses aboard
        - **parch**: Number of parents/children aboard
        - **fare**: Ticket fare paid in pounds sterling
        - **embarked**: Port of embarkation (C = Cherbourg, Q = Queenstown, S = Southampton)
        - **class**: Ticket class as a string
        - **who**: Passenger group (man, woman, child)
        - **adult_male**: Whether the passenger is an adult male
        - **deck**: Cabin deck (many missing)
        - **embark_town**: Town of embarkation
        - **alive**: Survival status as text
        - **alone**: Whether the passenger was alone
        """)