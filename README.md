
# LLM-Driven Sales Data Explorer

This project is a Dash web application that allows users to explore sales data using natural language queries. It leverages a lightweight Large Language Model (LLM) from Hugging Face to translate user input into Pandas data filtering and Plotly visualizations.

---

## Project Structure

```
llm_for_graphs/
├── app.py                 # Main Dash app
├── llm_utils.py           # LLM query logic
├── data/
│   └── sales_data.csv     # Superstore sales dataset
├── requirements.txt       # Python dependencies
└── README.md              # Project overview
```

---

## Features

- Query the dataset using natural language like:
  - "Show total sales per region"
  - "Filter sales from California in 2017"
- Dynamic graph generation using Plotly
- Filtered data table shown below the graph
- Powered by Hugging Face's `google/gemma-2b-it` model

---

## Getting Started

### 1. Clone the Repo

```bash
git clone https://github.com/alekospj/llm_for_graphs
cd llm_for_graphs
```

### 2. Create a Virtual Environment

```bash
python -m venv llm_graphs
.\llm_graphs\Scripts\Activate.ps1  # Windows PowerShell
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the App

```bash
python app.py
```

---

##  About the Model

We use a small instruction-tuned model from Hugging Face (e.g. `google/gemma-2b-it`) to convert user queries into pandas code. The code is then executed to filter and visualize data.

Model files are cached under:
```
C:\Users\<your-user>\.cache\huggingface\hub\
```

---

##  Dataset

The sample dataset comes from [Kaggle - Superstore Sales Forecasting](https://www.kaggle.com/datasets/rohitsahoo/sales-forecasting).

Replace or expand `data/sales_data.csv` with other datasets as needed.

---

##  Future Improvements

- Export filtered data to CSV
- Let user select graph type (bar, line, pie)
- Add natural language explanations under visualizations

---

##  Credits

- Powered by Dash, Plotly, Hugging Face Transformers

