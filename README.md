# 🧁 Smart Bakery Management System – Prototype  
**By Tasbeeh Takrori**

## 📌 About  
This is an AI-powered bakery management prototype built using **Streamlit** and **SQLite**, designed to support small bakeries in making smarter daily decisions. It includes features like AI demand forecasting, stock tracking, and raw material consumption estimation.

> ⚠️ Note: The system uses **fake/generated data** for testing and demo purposes.

---

## ✅ Features Implemented

### 🛒 Product & Inventory Management  
- Add, edit, and delete **products** and their **ingredients**  
- Manage **raw materials** and monitor stock levels  
- Real-time **alerts** for low stock  

### 📈 AI Demand Forecasting  
- Predict product demand using **Facebook Prophet**
- Demand is affected by:
  - 📍 **Weather conditions** (temperature, humidity, wind)
  - 🚧 **Checkpoint conditions** (5 dynamic barriers)
- Daily and 7-day forecast per product
- Visualized predictions with interactive charts

### 🧠 Raw Material Forecasting  
- Estimate the expected daily demand for each raw material
- Show **"Days to depletion"** per ingredient based on product predictions
- Color-coded risk indicators (e.g., red for < 3 days)

### 🧾 Order Management  
- Add new customer orders  
- Automatically:
  - Reduce product stock  
  - Reduce raw materials based on product recipe
- Prevent order placement if stock is insufficient

### 📊 Data Visualizations  
- Product demand trends over time  
- Daily product orders (last 7 days)  
- Raw material usage and remaining stock  

### ✅ Prediction Accuracy Analysis  
- Compare predicted vs. actual demand  
- View MAE, MAPE, and Accuracy per product  
- Interactive error tables and accuracy progress bars

### 💬 AI Chatbot (Marketing Assistant)  
- Built-in **AI-based text generation assistant**  
- Helps bakery owners write promotional content (e.g., social media posts, product descriptions)  
- Generates Arabic content tailored to bakery context

---

## ▶️ How to Run

1. **Clone the repo**

  ```bash
    git clone https://github.com/TasbeehTakrori/Smart-Bakery-Management-System.git
    cd Smart-Bakery-Management-System
  ```

2. **Install requirements**
  ```bash
  pip install -r requirements.txt
  ```

3. **Run the app**
```bash
streamlit run main.py
```

---

## 🛠️ Technologies Used

| Technology      | Description                                       |
|-----------------|---------------------------------------------------|
| **Streamlit**   | For building the interactive user interface       |
| **SQLite**      | Lightweight embedded database for storage         |
| **Prophet**     | Time series forecasting model for demand prediction |
| **Pandas**      | Data manipulation and analysis                    |
| **Plotly**      | Interactive charts and visualizations             |
| **SQLAlchemy**  | ORM for database interactions                     |
| **Joblib**      | Saving and loading trained AI models              |
| **Thinkstack (GPT-based)** | Used to build the AI-powered chatbot, leveraging OpenAI's language models (ChatGPT) to generate bakery-specific marketing content in Arabic |

---

## 🧠 Notes

- All AI models are trained on **generated/fake data** for demonstration purposes only.
- Demand forecasting considers external factors like **weather conditions** and **checkpoint delays**.
- Raw materials page includes **"days to depletion"** insights to assist with inventory planning.
- The **AI chatbot** is integrated using **Thinkstack**, built on top of **OpenAI's GPT** technology, to help bakery owners write better Arabic promotional content.
- This system is a prototype developed for educational and demo use.

---

## 🙋‍♀️ Author

**Tasbeeh Takrori**  
Graduate Student in Artificial Intelligence  
An-Najah National University