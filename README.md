# AI & ML based Restock Predictor

📦 Smart Stock Prediction & Restock Reminder Tool
A Streamlit-based inventory intelligence app that predicts stockouts, visualizes sales trends, and helps businesses restock smartly before they run out of inventory.

🧠 Overview
    The Smart Stock Prediction Tool helps businesses forecast when products will run out of stock by analyzing sales velocity (average daily sales) and current stock levels.
    It also provides proactive restock alerts, visual dashboards, and data export features.
    With this tool, businesses can:
        Prevent stockouts and lost sales.
        Avoid overstocking.
        Plan inventory purchases more efficiently.
        Get visual insights into inventory health.

🚀 Key Features
    ✅ Upload Sales Data – Import CSV or Excel files with your sales and inventory data.
    ✅ Flexible Date Parsing – Automatically detects and parses multiple date formats.
    ✅ Dynamic Column Mapping – Assign your own columns (date, product, quantity, stock, receipts).
    ✅ Stockout Prediction – Predicts when each product will go out of stock based on sales trends.
    ✅ Visual Dashboards:

📈 Stockout Timeline
    🛍️ Sales & Receipts  Trends

    ❤️ Inventory Health Pie Chart
    ✅ Restock Suggestions – Recommends reorder quantities to maintain 30 days of inventory.
    ✅ Email Notification Setup – Add your email to receive simulated stock alerts.
    ✅ Custom Alerts – Set your own stockout alert threshold (e.g., 7 or 14 days).
    ✅ Download Predictions – Export stock predictions as a CSV file.

🧩 Tech Stack
    Component	Technology
    Frontend UI	Streamlit
    Backend	Python
    Data Analysis	Pandas, NumPy
    Date Parsing	python-dateutil
    Visualization	Matplotlib, Streamlit Charts
    Notifications (Simulated)	Streamlit UI Alerts
    Deployment Streamlit Cloud (Recommended)
⚙️ Installation & Setup
    1️⃣ Clone the Repository
        git clone https://github.com/your-username/smart-stock-prediction.git
        cd smart-stock-prediction

    2️⃣ Create a Virtual Environment (Recommended)
        python -m venv venv
        source venv/bin/activate      # On macOS/Linux
        venv\Scripts\activate         # On Windows

    3️⃣ Install Dependencies
        pip install -r requirements.txt

    4️⃣ Run the Application
        streamlit run smart_stock_prediction.py

📄 requirements.txt
    streamlit==1.38.0
    pandas==2.2.2
    numpy==1.26.4
    matplotlib==3.9.2
    python-dateutil==2.9.0.post0
    openpyxl==3.1.5    # Required for Excel file uploads

🧾 How It Works
    Upload your sales data file
    Supports .csv or .xlsx
    Must contain at least:
      Date column
      Product name column
      Quantity sold column
    Optional:
      Current stock column
      Stock receipts column
      Map the Columns
      Assign correct columns for date, product, quantity, and stock.
      Process & Analyze
    The app calculates:
      Average daily sales
      Adjusted stock levels
      Estimated stockout dates
      Visualize Predictions
    View graphical dashboards:
      Stockout Timeline
      Daily Sales Trends
      Inventory Health Pie Chart
      Get Restock Alerts
      Critical products (within your set threshold) are highlighted.
      Option to simulate alerts or export prediction data.
      Export Predictions
      Download results as stock_predictions.csv

📊 Dashboard Highlights
    Section	Description
    Stockout Timeline	Bar chart showing days until stockout for each product with color-coded safety levels.
    Sales Trends	Line and bar charts for sales, stock receipts, and moving averages.
    Inventory Health	Pie chart summarizing products by stock health (Safe / Low / Critical).
    Restock Suggestions	Recommended reorder quantities based on forecasted sales.
    Alerts	Simulated email alerts for products nearing stockout.
🧠 Prediction Logic

    The stockout prediction formula used:
    Days Until Stockout = (Current Stock + Stock Receipts) / Average Daily Sales
    A product is:
    🟢 Safe → >14 days of stock left
    
    🟡 Low → Between 7–14 days
    
    🔴 Critical → <7 days

📧 Simulated Notifications
    Enter your email in the sidebar.
    Alerts are simulated (displayed in the UI).
    In production, you can integrate SMTP or APIs (like SendGrid) to send actual email alerts.

💾 Output Files
    File Name	Description
    stock_predictions.csv	Predicted stockout data for all products
    (Your uploaded files remain local — nothing is stored externally)	
🔮 Future Enhancements

    🔔 Real email/SMS notifications
    🧠 AI-powered demand forecasting
    🗓️ Automated reorder scheduling
    ☁️ Cloud database (SQLite / Firebase)
    📊 Interactive visualizations with Plotly

👩‍💻 Author

Rashmi G.
Built for businesses to optimize inventory management using sales intelligence.
