# 💳 Credit Card Statement Parser

A Python Flask web application that extracts key financial details from credit card statements of major **Indian banks**.  
This tool demonstrates intelligent PDF parsing, regex-based data extraction, and structured result presentation.

---

## 🚀 Features

- Parses **real-world PDF statements** from 5 major Indian banks  
- Extracts key data points instantly  
- Clean, modern web interface built with HTML/CSS  
- Automatically deletes uploaded files after parsing  
- Handles varying statement layouts and formats with robust regex logic  

---

## 🏦 Supported Banks

- HDFC Bank  
- ICICI Bank  
- SBI Card  
- Axis Bank  
- Kotak Mahindra Bank  

---

## 📊 Extracted Fields

For each statement, the following data points are extracted:

1. Bank Name  
2. Card Last 4 Digits  
3. Statement Date  
4. Payment Due Date  
5. Total Amount Due  
6. Minimum Amount Due  

> **Note:** For some corporate cards (like Kotak Corporate), the minimum due may not be present.

---

## 📁 Project Structure

credit-card-parser/
├── app.py # Main Flask app
├── parsers/
│ ├── init.py
│ ├── base_parser.py # Base parser class with shared logic
│ ├── hdfc_parser.py
│ ├── icici_parser.py
│ ├── sbi_parser.py
│ ├── axis_parser.py
│ └── kotak_parser.py
├── templates/
│ └── index.html # Frontend UI
├── uploads/ # Temporary upload folder (auto-created)
├── requirements.txt
└── README.md



---

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository
git clone https://github.com/kaivuxu/sure.financial_task.git
cd credit-card-parser
2️⃣ Create a Virtual Environment 
python -m venv venv
# Activate it
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows
3️⃣ Install Dependencies
pip install -r requirements.txt
4️⃣ Run the Application
python app.py