# smart_stock_prediction.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import io
from dateutil import parser

# Set page configuration
st.set_page_config(
    page_title="Smart Stock Prediction Tool",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# App title and description
st.title("📦 Smart Stock Prediction & Restock Reminder Tool")
st.markdown("""
This tool helps businesses predict when products will run out of stock and sends proactive reminders.
Upload your sales data, and the system will calculate stockout predictions using sales velocity analysis.
""")

# Initialize session state for data persistence
if 'df' not in st.session_state:
    st.session_state.df = None
if 'notifications_sent' not in st.session_state:
    st.session_state.notifications_sent = []
if 'product_col' not in st.session_state:
    st.session_state.product_col = None
if 'stock_col' not in st.session_state:
    st.session_state.stock_col = None
if 'receipts_col' not in st.session_state:
    st.session_state.receipts_col = None
if 'user_email' not in st.session_state:
    st.session_state.user_email = ""

# Function to parse dates with multiple format support
def parse_date_column(date_series):
    parsed_dates = []
    for date_str in date_series.astype(str):
        try:
            # Try to parse with dateutil parser (handles most formats)
            parsed_date = parser.parse(date_str)
            parsed_dates.append(parsed_date)
        except (ValueError, TypeError):
            # If parsing fails, keep the original value (will be handled later)
            parsed_dates.append(pd.NaT)
    
    return pd.Series(parsed_dates, index=date_series.index)

# Sidebar for navigation and settings
with st.sidebar:
    st.header("User Profile")
    
    # Simple user registration
    st.subheader("Get Notifications")
    user_email = st.text_input("Your Email Address", placeholder="your.email@example.com")
    
    if user_email:
        st.session_state.user_email = user_email
        st.success(f"Notifications will be sent to: {user_email}")
    
    # Notification settings
    st.subheader("Notification Settings")
    alert_threshold = st.slider(
        "Days before stockout to send alert", 
        min_value=1, 
        max_value=14, 
        value=7
    )
    
    # Data management
    st.subheader("Data Management")
    if st.button("Clear All Data"):
        st.session_state.df = None
        st.session_state.notifications_sent = []
        st.session_state.product_col = None
        st.session_state.stock_col = None
        st.session_state.receipts_col = None
        st.success("Data cleared successfully!")

# File upload section
st.header("📤 Upload Sales Data")
uploaded_file = st.file_uploader(
    "Choose a CSV or Excel file with your sales data", 
    type=['csv', 'xlsx']
)

if uploaded_file is not None:
    try:
        # Read the file based on its extension
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        # Display basic info about the uploaded data
        st.success(f"Successfully uploaded the file!!")
        
        # Show column names and let user map them
        st.subheader("Column Mapping")
        st.write("Please identify which columns in your data correspond to the required fields:")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            date_col = st.selectbox("Date Column", options=df.columns)
        with col2:
            product_col = st.selectbox("Product Column", options=df.columns)
            st.session_state.product_col = product_col
        with col3:
            quantity_col = st.selectbox("Quantity/Sales Column", options=df.columns)
        with col4:
            # Check if there's a stock column
            stock_options = ["None (Assume 100 units)"] + list(df.columns)
            stock_col = st.selectbox("Current Stock Column (optional)", options=stock_options)
            if stock_col != "None (Assume 100 units)":
                st.session_state.stock_col = stock_col
        with col5:
            # Check if there's a stock receipts column
            receipts_options = ["None (Assume 0 units)"] + list(df.columns)
            receipts_col = st.selectbox("Stock Receipts Column (optional)", options=receipts_options)
            if receipts_col != "None (Assume 0 units)":
                st.session_state.receipts_col = receipts_col
        
        # Check if we need to process the data
        if st.button("Process Data"):
            # Basic data processing
            df_processed = df.copy()
            
            # Parse date column with flexible format handling
            df_processed['date'] = parse_date_column(df_processed[date_col])
            
            # Check if date parsing was successful
            if df_processed['date'].isna().any():
                invalid_dates = df_processed[df_processed['date'].isna()][date_col].unique()
                st.warning(f"Could not parse some date values: {', '.join(map(str, invalid_dates[:5]))}...")
                # Remove rows with invalid dates
                df_processed = df_processed.dropna(subset=['date'])
            
            df_processed['product'] = df_processed[product_col].astype(str)
            df_processed['quantity'] = pd.to_numeric(df_processed[quantity_col], errors='coerce')
            
            # Handle stock data
            if stock_col != "None (Assume 100 units)":
                df_processed['current_stock'] = pd.to_numeric(df_processed[stock_col], errors='coerce')
            else:
                # If no stock column, assume 100 units for all products
                df_processed['current_stock'] = 100
            
            # Handle stock receipts data
            if receipts_col != "None (Assume 0 units)":
                df_processed['stock_receipts'] = pd.to_numeric(df_processed[receipts_col], errors='coerce')
                # Fill NaN values with 0 (no receipts)
                df_processed['stock_receipts'] = df_processed['stock_receipts'].fillna(0)
            else:
                # If no receipts column, assume 0 units for all products
                df_processed['stock_receipts'] = 0
            
            # Remove rows with invalid quantities
            df_processed = df_processed.dropna(subset=['quantity'])
            
            # Store in session state
            st.session_state.df = df_processed
            st.success("Data processed successfully!")
    
    except Exception as e:
        st.error(f"Error reading file: {str(e)}")

# If we have processed data, show the dashboard
if st.session_state.df is not None:
    df = st.session_state.df
    
    # Calculate sales velocity and predictions
    st.header("📊 Stock Prediction Dashboard")
    
    # Get unique products
    products = df['product'].unique()
    
    # Let user select a product to focus on or show all
    selected_product = st.selectbox("Select Product", options=["All Products"] + list(products))
    
    if selected_product == "All Products":
        product_df = df
    else:
        product_df = df[df['product'] == selected_product]
    
    # Calculate daily sales and receipts
    daily_data = product_df.groupby(['date', 'product']).agg({
        'quantity': 'sum',
        'stock_receipts': 'sum'
    }).reset_index()
    
    # Calculate sales velocity (average daily sales)
    sales_velocity = daily_data.groupby('product').agg({
        'quantity': 'mean',
        'stock_receipts': 'sum'
    }).reset_index()
    sales_velocity.columns = ['product', 'avg_daily_sales', 'total_receipts']
    
    # Get current stock for each product (use the latest available stock data)
    current_stock = df.groupby('product')['current_stock'].last().reset_index()
    sales_velocity = sales_velocity.merge(current_stock, on='product')
    
    # Adjust current stock with receipts (if any)
    sales_velocity['adjusted_stock'] = sales_velocity['current_stock'] + sales_velocity['total_receipts']
    
    # Calculate days until stockout
    sales_velocity['days_until_stockout'] = sales_velocity['adjusted_stock'] / sales_velocity['avg_daily_sales']
    sales_velocity['stockout_date'] = datetime.now() + pd.to_timedelta(
        sales_velocity['days_until_stockout'], unit='D'
    )
    
    # Determine status with traffic light system
    def get_status(days):
        if days > 14:
            return "🟢 Safe"
        elif days > 7:
            return "🟡 Low"
        else:
            return "🔴 Critical"
    
    sales_velocity['status'] = sales_velocity['days_until_stockout'].apply(get_status)
    
    # Display the predictions
    st.subheader("Stockout Predictions")
    st.dataframe(sales_velocity)
    
    # Visualizations
    st.subheader("Sales Trends & Predictions")
    
    # Create tabs for different visualizations
    tab1, tab2, tab3 = st.tabs(["Stockout Timeline", "Sales Trends", "Inventory Health"])
    
    with tab1:
        # Stockout timeline visualization using matplotlib
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Sort by days until stockout for better visualization
        sorted_data = sales_velocity.sort_values('days_until_stockout', ascending=True)
        
        # Create color mapping
        colors = []
        for days in sorted_data['days_until_stockout']:
            if days > 14:
                colors.append('green')
            elif days > 7:
                colors.append('orange')
            else:
                colors.append('red')
        
        # Create the bar chart
        bars = ax.bar(range(len(sorted_data)), sorted_data['days_until_stockout'], color=colors)
        
        # Add value labels on bars
        for i, bar in enumerate(bars):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}',
                    ha='center', va='bottom', fontweight='bold')
        
        # Add threshold lines
        ax.axhline(y=7, color='orange', linestyle='--', alpha=0.7, label='Low Stock Threshold')
        ax.axhline(y=14, color='green', linestyle='--', alpha=0.7, label='Safe Stock Threshold')
        
        # Customize the chart
        ax.set_title('Days Until Stockout by Product', fontsize=16, fontweight='bold')
        ax.set_xlabel('Product')
        ax.set_ylabel('Days Until Stockout')
        ax.set_xticks(range(len(sorted_data)))
        ax.set_xticklabels(sorted_data['product'], rotation=45, ha='right')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        st.pyplot(fig)
    
    with tab2:
        # Sales trends visualization
        if selected_product == "All Products":
            # Create a line chart for all products using Streamlit's native line_chart
            pivot_sales = daily_data.pivot(index='date', columns='product', values='quantity').fillna(0)
            st.line_chart(pivot_sales)
            st.caption("Sales Trends for All Products")
            
            # Also show receipts if available
            if (daily_data['stock_receipts'] > 0).any():
                pivot_receipts = daily_data.pivot(index='date', columns='product', values='stock_receipts').fillna(0)
                st.line_chart(pivot_receipts)
                st.caption("Stock Receipts for All Products")
        else:
            # For a single product, show more detailed analysis
            product_data = daily_data[daily_data['product'] == selected_product]
            
            # Create a line chart with area
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Plot the sales data
            ax.plot(product_data['date'], product_data['quantity'], 
                   marker='o', linewidth=2, markersize=4, label='Daily Sales')
            
            # Plot stock receipts if available
            if (product_data['stock_receipts'] > 0).any():
                ax.bar(product_data['date'], product_data['stock_receipts'], 
                      alpha=0.5, label='Stock Receipts', color='green')
            
            # Add a 7-day moving average
            moving_avg = product_data['quantity'].rolling(window=7, min_periods=1).mean()
            ax.plot(product_data['date'], moving_avg, 
                   color='red', linewidth=2, label='7-Day Moving Average')
            
            # Fill area under the curve
            ax.fill_between(product_data['date'], product_data['quantity'], alpha=0.3)
            
            # Customize the chart
            ax.set_title(f'Sales Trend for {selected_product}', fontsize=16, fontweight='bold')
            ax.set_xlabel('Date')
            ax.set_ylabel('Quantity')
            ax.legend()
            ax.grid(True, alpha=0.3)
            plt.xticks(rotation=45)
            
            plt.tight_layout()
            st.pyplot(fig)
            
            # Show sales statistics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Average Daily Sales", f"{product_data['quantity'].mean():.2f}")
            with col2:
                st.metric("Max Daily Sales", f"{product_data['quantity'].max():.2f}")
            with col3:
                st.metric("Total Receipts", f"{product_data['stock_receipts'].sum():.0f}")
            with col4:
                st.metric("Sales Volatility", f"{product_data['quantity'].std():.2f}")
    
    with tab3:
        # Inventory health dashboard
        st.subheader("Inventory Health Status")
        
        # Create a summary of inventory status
        status_counts = sales_velocity['status'].value_counts()
        
        # Create a pie chart for inventory status
        fig, ax = plt.subplots(figsize=(8, 8))
        
        # Define colors for each status
        colors = {'🟢 Safe': 'green', '🟡 Low': 'orange', '🔴 Critical': 'red'}
        pie_colors = [colors[status] for status in status_counts.index]
        
        # Create the pie chart
        wedges, texts, autotexts = ax.pie(
            status_counts.values, 
            labels=status_counts.index, 
            autopct='%1.1f%%',
            colors=pie_colors,
            startangle=90
        )
        
        # Style the text
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax.set_title('Inventory Health Distribution', fontsize=16, fontweight='bold')
        
        st.pyplot(fig)
        
        # Show inventory metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Products at Risk", f"{len(sales_velocity[sales_velocity['status'] != '🟢 Safe'])}")
        with col2:
            st.metric("Critical Products", f"{len(sales_velocity[sales_velocity['status'] == '🔴 Critical'])}")
        with col3:
            avg_days = sales_velocity['days_until_stockout'].mean()
            status = "🟢" if avg_days > 14 else "🟡" if avg_days > 7 else "🔴"
            st.metric("Avg Days Until Stockout", f"{status} {avg_days:.1f}")
        with col4:
            total_receipts = sales_velocity['total_receipts'].sum()
            st.metric("Total Stock Receipts", f"{total_receipts:.0f}")
    
    # Restock suggestions
    st.subheader("🔄 Restock Suggestions")
    
    # Check for products that need restocking
    products_needing_restock = sales_velocity[sales_velocity['days_until_stockout'] < 14]
    
    if products_needing_restock.empty:
        st.success("🎉 All products have sufficient stock! No immediate restocking needed.")
    else:
        for _, row in products_needing_restock.iterrows():
            # Calculate suggested restock quantity (30 days of inventory)
            suggested_restock = max(50, row['avg_daily_sales'] * 30)
            
            # Adjust for any recent receipts
            if row['total_receipts'] > 0:
                st.warning(
                    f"**{row['product']}**: Restock suggested. "
                    f"Current stock (including {row['total_receipts']:.0f} units received) "
                    f"will last {row['days_until_stockout']:.1f} days. "
                    f"Suggested quantity: {suggested_restock:.0f} units."
                )
            else:
                st.warning(
                    f"**{row['product']}**: Restock suggested. "
                    f"Current stock will last {row['days_until_stockout']:.1f} days. "
                    f"Suggested quantity: {suggested_restock:.0f} units."
                )
    
    # Notification system
    st.header("🔔 Restock Alerts")
    
    # Check for critical products that need immediate attention
    critical_products = sales_velocity[sales_velocity['days_until_stockout'] <= alert_threshold]
    
    if not critical_products.empty:
        st.error("🚨 **IMMEDIATE ATTENTION NEEDED**")
        
        for _, row in critical_products.iterrows():
            st.error(
                f"**{row['product']}** is critical! "
                f"Only {row['days_until_stockout']:.1f} days of stock remaining. "
                f"Urgent restocking required!"
            )
        
        # Show notification option
        if st.session_state.user_email:
            if st.button("Send Me These Alerts"):
                # Create a simple message
                alert_message = f"Stock Alerts for {st.session_state.user_email}:\n\n"
                for _, row in critical_products.iterrows():
                    alert_message += f"- {row['product']}: {row['days_until_stockout']:.1f} days until stockout\n"
                
                # In a real app, you would send this via email
                # For this demo, we'll just show a success message
                st.success(f"Alerts would be sent to {st.session_state.user_email}")
                
                # Record the notification
                notification_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                products_notified = ", ".join(critical_products['product'].tolist())
                st.session_state.notifications_sent.append({
                    'time': notification_time,
                    'products': products_notified,
                    'email': st.session_state.user_email
                })
        else:
            st.info("💡 Enter your email address in the sidebar to receive these alerts")
    
    # Simulate future notifications
    st.subheader("📅 Simulated Future Alerts")

    if not critical_products.empty:
        simulated_alerts = []
        today = datetime.now()
        for _, row in critical_products.iterrows():
            # Calculate the alert date (days before stockout)
            alert_date = row['stockout_date'] - timedelta(days=alert_threshold)
            if alert_date < today:
                alert_date = today  # If alert date already passed, show today
            simulated_alerts.append({
                'Product': row['product'],
                'Current Stock': int(row['adjusted_stock']),
                'Avg Daily Sales': round(row['avg_daily_sales'], 2),
                'Stockout Date': row['stockout_date'].strftime("%Y-%m-%d"),
                f"Alert {alert_threshold} Days Before": alert_date.strftime("%Y-%m-%d")
            })
    
        sim_alert_df = pd.DataFrame(simulated_alerts)
        st.dataframe(sim_alert_df)
        st.info("💡 This table shows when alerts would be sent based on the stockout prediction. In a production system, emails would be automatically scheduled for these dates.")
    else:
        st.success("No products require alerts within the selected threshold.")

    # Show notification history
    if st.session_state.notifications_sent:
        st.subheader("Notification History")
        for notification in st.session_state.notifications_sent:
            st.write(f"⏰ {notification['time']}: Alert sent for {notification['products']}")
    
    # Data export
    st.header("💾 Export Data")
    
    # Convert predictions to CSV
    csv = sales_velocity.to_csv(index=False)
    st.download_button(
        label="Download Predictions as CSV",
        data=csv,
        file_name="stock_predictions.csv",
        mime="text/csv"
    )
    
else:
    st.info("Please upload a sales data file to get started.")

# Add footer
st.markdown("---")
st.markdown(
    "**Smart Stock Prediction Tool** | "
    "Avoid stockouts and overstocking with data-driven inventory management"
)
