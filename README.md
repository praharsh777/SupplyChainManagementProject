 📦 Supply chain Management and Optimization 

This project is a smart, modular **Supply chain Management and Optimization ** for logistics and supply chain analytics. It integrates four essential tools:

1. 📈 **Demand Forecasting**
2. 📉 **Risk Analysis**
3. 🏭 **Inventory Management**
4. 🚚 **Route Optimization**

### 🧠 Built to empower businesses with actionable insights, the toolkit combines the analytical power of Streamlit and the UI flexibility of React, with Flask powering backend logic and API connectivity.

---

## 🚀 Features

- ✅ React-based responsive frontend with modern UI
- 🧮 Interactive data-driven tools built in Streamlit
- 🔗 Flask backend handling API communication & tool orchestration
- 📊 Supports visualization, prediction, and optimization logic
- 🧠 Real-time interaction and prediction via web interface

---

## 🛠️ Tech Stack

| Layer       | Tech Used                     |
|-------------|-------------------------------|
| Frontend    | React.js                      |
| Backend     | Flask (Python)                |
| Tool UIs    | Streamlit                     |
| Database    | SQLite (`users.db`)           |
| Others      | Pandas, NumPy, Scikit-learn   |

---

## 📂 Project Structure

Business-Toolkit/
├── backend/ # Flask backend API
├── frontend/ # React frontend UI
│ └── (contains 4 tool sections)
├── saved_files/ # Uploaded files or outputs
├── venv/ # Virtual environment (ignored in Git)
├── streamlit_app.py # Demand Forecasting tool
├── streamlit_app_inventory.py # Inventory Management tool
├── streamlit_app_risk.py # Risk Analysis tool
├── streamlit_app_route.py # Route Optimization tool
├── users.db # SQLite database
├── .gitignore
├── package.json # React dependencies
└── README.md # This file

yaml
Copy
Edit

---

## 🧪 Running the Project

### ⚙️ 1. Backend (Flask)

```bash
cd backend
python app.py
🌐 2. Frontend (React)
bash
Copy
Edit
cd frontend
npm install
npm start
🧠 3. Run Streamlit Tools (each in a separate terminal)
bash
Copy
Edit
streamlit run streamlit_app.py                 # Demand Forecasting
streamlit run streamlit_app_inventory.py       # Inventory Management
streamlit run streamlit_app_risk.py            # Risk Analysis
streamlit run streamlit_app_route.py           # Route Optimization
📌 Roadmap
 OAuth-based user login

 Real-time data sync across modules

 RESTful API integration with ML models

 Deploy full stack on cloud (Render, AWS)

🤝 Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change or improve.

