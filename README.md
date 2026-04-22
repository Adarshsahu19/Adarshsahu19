# Advanced Stock Price Predictor + Dashboard

A Streamlit app that forecasts stock closing prices with two model families and compares their performance:

- **LSTM** (TensorFlow/Keras)
- **ARIMA** (statsmodels)

It also supports optional **news-sentiment adjustment** using Yahoo Finance headlines and VADER sentiment.

## Features

- Download historical stock data from Yahoo Finance
- Train and compare LSTM vs ARIMA on the same train/test split
- Show RMSE, MAE, and MAPE metrics side-by-side
- Visualize actual vs both forecasts in an interactive Plotly chart
- Apply sentiment-based adjustment to both forecasts

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Notes

- This project is for educational purposes.
- Forecasts are not investment advice.
- ARIMA order is currently fixed to `(5, 1, 0)` and can be extended.
