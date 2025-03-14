import streamlit as st
import pandas as pd
import plotly.express as px

# Set full-width layout
st.set_page_config(layout="wide", page_title="Price Sensitivity Dashboard")

st.markdown(
    """
    <style>
    /* Change background color */
    body, .stApp {
        background-color: #12123B;
        color: #E8F0FF !important;
    }

    /* Change sidebar color */
    .stSidebar {
        background-color: #3C37FF !important;
    }
    
    /* Sidebar text color */
    .stSidebar div {
        color: white !important;
    }

    /* Change text color for main content */
    .stMarkdown, .stText, .stSubheader, .stMetric, .stTitle, .stHeader, .stTable {
        color: #E8F0FF !important;
    }

    /* Style buttons */
    .stButton>button {
        background-color: #3C37FF !important;
        color: white !important;
        border-radius: 8px;
        border: none;
    }

    /* Style metric boxes */
    .stMetric {
        color: #E8F0FF !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# Load Aggregated Data
@st.cache_data
def load_data():
    revenue_df = pd.read_csv("aggregated_revenue.csv")  
    margin_df = pd.read_csv("aggregated_margin.csv")    
    quantity_df = pd.read_csv("aggregated_quantity.csv")

    # Rename columns for clarity
    rename_cols = {
        "Test 25": "Test 2025", "Control 25": "Control 2025",
        "Test 24": "Test 2024", "Control 24": "Control 2024"
    }

    revenue_df.rename(columns=rename_cols, inplace=True)
    margin_df.rename(columns=rename_cols, inplace=True)
    quantity_df.rename(columns=rename_cols, inplace=True)
    product_df = pd.read_csv("Soprema_results__Feb24_Feb25(Results per product).csv")  # Load the new per-product dataset


    return revenue_df, margin_df, quantity_df, product_df

revenue_df, margin_df, quantity_df, product_df = load_data()

# Correct Test % Change Calculation
def compute_percentage_change(df, column_2025, column_2024):
    return round(((df[column_2025].sum() - df[column_2024].sum()) / df[column_2024].sum()) * 100, 2)

revenue_test_pct = compute_percentage_change(revenue_df, "Test 2025", "Test 2024")
margin_test_pct = compute_percentage_change(margin_df, "Test 2025", "Test 2024")
quantity_test_pct = compute_percentage_change(quantity_df, "Test 2025", "Test 2024")

# Round percentage changes in dataframe
for df in [revenue_df, margin_df, quantity_df]:
    df["%Change Test"] = df["%Change Test"].round(2)
    df["%Change Control"] = df["%Change Control"].round(2)

# Calculate Performance Difference and Round
revenue_perf_diff = round(revenue_test_pct - revenue_df["%Change Control"].mean(), 2)
margin_perf_diff = round(margin_test_pct - margin_df["%Change Control"].mean(), 2)
quantity_perf_diff = round(quantity_test_pct - quantity_df["%Change Control"].mean(), 2)

# Function to display arrows based on performance
def performance_arrow(perf_diff):
    if perf_diff > 0:
        return f"🟢 ▲ {perf_diff:.2f}% better than Control"
    elif perf_diff < 0:
        return f"🔴 ▼ {abs(perf_diff):.2f}% worse than Control"
    else:
        return "⚖️ No difference from Control"

# Sidebar Navigation
st.sidebar.title("🔍 Select a View")
page = st.sidebar.radio("Go to", ["🏠 Home", "💰 Revenue", "📈 Margin", "📦 Quantity", "📊 Per Product Analysis"])

# Function to create bar charts with rounded values
def create_bar_chart(df, column, title):
    df = df.copy()
    df[column] = df[column].round(2)  # Ensure values are rounded before plotting
    fig = px.bar(df, x="Price change", y=column, color="StrategyBoxName", 
                 title=title, text=df[column].astype(str) + '%')
    return fig

# --------------------- HOME PAGE ---------------------
if page == "🏠 Home":
    st.title("📊 Price Sensitivity Dashboard")

    col1, col2, col3 = st.columns([1.5, 1.5, 1])  

    # --- COLUMN 1: REVENUE ---
    with col1:
        st.markdown("### 💰 Total Revenue")
        st.subheader(f"Test 2025: €{revenue_df['Test 2025'].sum():,.2f}")
        st.write(f"Test 2024: **€{revenue_df['Test 2024'].sum():,.2f}**")
        st.subheader(f"Control 2025: €{revenue_df['Control 2025'].sum():,.2f}")
        st.write(f"Control 2024: **€{revenue_df['Control 2024'].sum():,.2f}**")
        st.metric("Test % Change", f"{revenue_test_pct:.2f}%")
        st.metric("Control % Change", f"{revenue_df['%Change Control'].mean():.2f}%")

        # Display Performance Arrow
        st.markdown(f"**{performance_arrow(revenue_perf_diff)}**")

    # --- COLUMN 2: MARGIN ---
    with col2:
        st.markdown("### 📈 Total Margin")
        st.subheader(f"Test 2025: €{margin_df['Test 2025'].sum():,.2f}")
        st.write(f"Test 2024: **€{margin_df['Test 2024'].sum():,.2f}**")
        st.subheader(f"Control 2025: €{margin_df['Control 2025'].sum():,.2f}")
        st.write(f"Control 2024: **€{margin_df['Control 2024'].sum():,.2f}**")
        st.metric("Test % Change", f"{margin_test_pct:.2f}%")
        st.metric("Control % Change", f"{margin_df['%Change Control'].mean():.2f}%")

        # Display Performance Arrow
        st.markdown(f"**{performance_arrow(margin_perf_diff)}**")

    # --- COLUMN 3: QUANTITY ---
    with col3:
        st.markdown("### 📦 Total Quantity")
        st.subheader(f"Test 2025: {quantity_df['Test 2025'].sum():,.0f}")
        st.write(f"Test 2024: **{quantity_df['Test 2024'].sum():,.0f}**")
        st.subheader(f"Control 2025: {quantity_df['Control 2025'].sum():,.0f}")
        st.write(f"Control 2024: **{quantity_df['Control 2024'].sum():,.0f}**")
        st.metric("Test % Change", f"{quantity_test_pct:.2f}%")
        st.metric("Control % Change", f"{quantity_df['%Change Control'].mean():.2f}%")

        # Display Performance Arrow
        st.markdown(f"**{performance_arrow(quantity_perf_diff)}**")

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
    st.image("logo.png", width=150)
    st.markdown("</div>", unsafe_allow_html=True)

# --------------------- INDIVIDUAL PAGES ---------------------
elif page in ["💰 Revenue", "📈 Margin", "📦 Quantity"]:
    measure = page.split()[1]  # Extract 'Revenue', 'Margin', 'Quantity'
    df = revenue_df if measure == "Revenue" else margin_df if measure == "Margin" else quantity_df
    test_pct = revenue_test_pct if measure == "Revenue" else margin_test_pct if measure == "Margin" else quantity_test_pct
    perf_diff = revenue_perf_diff if measure == "Revenue" else margin_perf_diff if measure == "Margin" else quantity_perf_diff

    # Centered Title with Icon
    st.markdown(f"<h1 style='text-align: center;'>📊 Detailed {measure} Analysis</h1>", unsafe_allow_html=True)

    # Formatting based on measure type
    currency_symbol = "€" if measure in ["Revenue", "Margin"] else ""

    # Create space between sections
    st.markdown("<br>", unsafe_allow_html=True)

    # Display Key Values in One Line (Centered)
    col1, col2 = st.columns([1, 1])  # Equal width columns
    with col1:
        st.markdown(f"<h3 style='text-align: center;'>{measure} (Test)</h3>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align: center;'>{currency_symbol}{df['Test 2025'].sum():,.2f}</h2>", unsafe_allow_html=True)
        st.markdown(f"<h4 style='text-align: center;'>2024: {currency_symbol}{df['Test 2024'].sum():,.2f}</h4>", unsafe_allow_html=True)

    with col2:
        st.markdown(f"<h3 style='text-align: center;'>{measure} (Control)</h3>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align: center;'>{currency_symbol}{df['Control 2025'].sum():,.2f}</h2>", unsafe_allow_html=True)
        st.markdown(f"<h4 style='text-align: center;'>2024: {currency_symbol}{df['Control 2024'].sum():,.2f}</h4>", unsafe_allow_html=True)

    # Create space between sections
    st.markdown("<br>", unsafe_allow_html=True)

    # Display % Changes in One Line (Centered)
    col3, col4 = st.columns([1, 1])
    with col3:
        st.markdown(f"<h3 style='text-align: center;'>Test % Change</h3>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align: center;'>{test_pct:.2f}%</h2>", unsafe_allow_html=True)

    with col4:
        st.markdown(f"<h3 style='text-align: center;'>Control % Change</h3>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align: center;'>{df['%Change Control'].mean():.2f}%</h2>", unsafe_allow_html=True)

    # Create space between sections
    st.markdown("<br><br>", unsafe_allow_html=True)

    # Performance Arrow - Make It **Larger & Centered**
    st.markdown(
        f"<h1 style='text-align: center; font-size: 32px; font-weight: bold;'> {performance_arrow(perf_diff)} </h1>",
        unsafe_allow_html=True
    )

    # Create space between performance and charts
    st.markdown("<br><br>", unsafe_allow_html=True)

    # Plots with Rounded Values (Centered)
    st.plotly_chart(create_bar_chart(df, "%Change Test", f"{measure} Test % Change"), use_container_width=True)
    st.plotly_chart(create_bar_chart(df, "%Change Control", f"{measure} Control % Change"), use_container_width=True)

    # Create space before Data Table
    st.markdown("<br><br>", unsafe_allow_html=True)

    # Table
    st.markdown(f"<h3 style='text-align: center;'>📋 {measure} Data Table</h3>", unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
    st.image("logo.png", width=150)
    st.markdown("</div>", unsafe_allow_html=True)

    # --------------------- PER PRODUCT PAGE ---------------------
if page == "📊 Per Product Analysis":
    st.title("📊 Per Product Performance")

    # Display Summary Statistics
    st.subheader("Summary Statistics")
    st.write(product_df.describe())

    # Create Selectbox for Dynamic Visualization
    selected_metric = st.selectbox(
        "Select a metric to visualize:",
        ["Total Revenue", "Total Margin", "Quantity"]
    )

    # Map user selection to correct column in dataset
    column_map = {
        "Total Revenue": "Total Revenue Test 25",
        "Total Margin": "Total Margin Test 25",
        "Quantity": "Quantity Test 25"
    }

    selected_column = column_map[selected_metric]

    # Create Bar Chart
    st.subheader(f"Top 10 Products by {selected_metric}")
    top_10_products = product_df.nlargest(10, selected_column)
    fig = px.bar(
        top_10_products,
        x="ProductId",
        y=selected_column,
        text=selected_column,
        title=f"Top 10 Products by {selected_metric}",
    )
    st.plotly_chart(fig, use_container_width=True)

    # Create Scatter Plot (Revenue vs Margin)
    st.subheader("Revenue vs Margin (Test 25)")
    fig2 = px.scatter(
        product_df,
        x="Total Revenue Test 25",
        y="Total Margin Test 25",
        color="StrategyBoxName",
        title="Revenue vs Margin (Per Product)",
        hover_data=["ProductId"]
    )
    st.plotly_chart(fig2, use_container_width=True)

    # Create space before Data Table
    st.markdown("<br><br>", unsafe_allow_html=True)

    # Display Data Table
    st.subheader("📋 Per Product Data Table")
    st.dataframe(product_df, use_container_width=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
    st.image("logo.png", width=150)
    st.markdown("</div>", unsafe_allow_html=True)
