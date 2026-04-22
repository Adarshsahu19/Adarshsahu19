import warnings
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.preprocessing import MinMaxScaler
from statsmodels.tsa.arima.model import ARIMA
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.models import Sequential
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

warnings.filterwarnings("ignore")


st.set_page_config(page_title="Stock Predictor Dashboard", layout="wide")
st.title("📈 Advanced Stock Price Predictor + Dashboard")
st.caption("LSTM vs ARIMA with optional news sentiment adjustment")


@st.cache_data(ttl=3600)
def load_data(symbol: str, start: datetime, end: datetime) -> pd.DataFrame:
    df = yf.download(symbol, start=start, end=end, auto_adjust=True, progress=False)
    if df.empty:
        raise ValueError("No price data found for this symbol/date range.")
    df = df[["Close"]].dropna()
    df.index = pd.to_datetime(df.index)
    return df


@st.cache_data(ttl=3600)
def load_news_sentiment(symbol: str, limit: int = 25) -> float:
    ticker = yf.Ticker(symbol)
    news = ticker.news or []
    if not news:
        return 0.0

    analyzer = SentimentIntensityAnalyzer()
    compound_scores = []

    for item in news[:limit]:
        title = item.get("title", "")
        summary = item.get("summary", "")
        combined = f"{title}. {summary}".strip()
        if combined:
            score = analyzer.polarity_scores(combined)["compound"]
            compound_scores.append(score)

    return float(np.mean(compound_scores)) if compound_scores else 0.0


def make_sequences(values: np.ndarray, lookback: int):
    x, y = [], []
    for i in range(lookback, len(values)):
        x.append(values[i - lookback : i])
        y.append(values[i])
    return np.array(x), np.array(y)


def train_lstm(train_series: pd.Series, test_len: int, lookback: int, epochs: int = 25):
    scaler = MinMaxScaler(feature_range=(0, 1))
    values = train_series.values.reshape(-1, 1)
    scaled = scaler.fit_transform(values)

    if len(scaled) <= lookback + test_len:
        raise ValueError("Not enough data for selected lookback and test size.")

    split_idx = len(scaled) - test_len
    train_scaled = scaled[:split_idx]

    x_train, y_train = make_sequences(train_scaled, lookback)
    x_train = x_train.reshape((x_train.shape[0], x_train.shape[1], 1))

    model = Sequential(
        [
            LSTM(64, return_sequences=True, input_shape=(lookback, 1)),
            Dropout(0.2),
            LSTM(32),
            Dropout(0.2),
            Dense(1),
        ]
    )
    model.compile(optimizer="adam", loss="mse")

    callback = EarlyStopping(monitor="loss", patience=4, restore_best_weights=True)
    model.fit(x_train, y_train, epochs=epochs, batch_size=32, verbose=0, callbacks=[callback])

    history_window = scaled[split_idx - lookback : split_idx]
    preds_scaled = []
    current = history_window.copy()

    for _ in range(test_len):
        x_input = current[-lookback:].reshape(1, lookback, 1)
        pred = model.predict(x_input, verbose=0)[0][0]
        preds_scaled.append(pred)
        current = np.vstack([current, [[pred]]])

    preds = scaler.inverse_transform(np.array(preds_scaled).reshape(-1, 1)).flatten()
    return preds


def train_arima(train_series: pd.Series, test_len: int, order=(5, 1, 0)):
    split_idx = len(train_series) - test_len
    train = train_series.iloc[:split_idx]

    model = ARIMA(train, order=order)
    fitted = model.fit()
    forecast = fitted.forecast(steps=test_len)
    return np.array(forecast)


def metrics(y_true: np.ndarray, y_pred: np.ndarray):
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae = mean_absolute_error(y_true, y_pred)
    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
    return rmse, mae, mape


def apply_sentiment_adjustment(pred: np.ndarray, sentiment: float, intensity: float):
    factor = 1 + (sentiment * intensity)
    return pred * factor


with st.sidebar:
    st.header("Settings")
    symbol = st.text_input("Ticker", value="AAPL").upper().strip()
    years = st.slider("History (years)", 2, 10, 5)
    lookback = st.slider("LSTM lookback window", 20, 120, 60, step=10)
    test_ratio = st.slider("Test split ratio", 0.1, 0.3, 0.2, step=0.05)
    use_sentiment = st.toggle("Use sentiment-adjusted forecast", value=True)
    sentiment_intensity = st.slider("Sentiment impact", 0.0, 0.15, 0.05, step=0.01)
    run = st.button("Run Models", type="primary")

if run:
    try:
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=int(365 * years))

        df = load_data(symbol, start_date, end_date)
        test_len = max(30, int(len(df) * test_ratio))

        close = df["Close"]
        y_true = close.iloc[-test_len:].values
        test_index = close.iloc[-test_len:].index

        with st.spinner("Training LSTM..."):
            lstm_pred = train_lstm(close, test_len=test_len, lookback=lookback)

        with st.spinner("Training ARIMA..."):
            arima_pred = train_arima(close, test_len=test_len)

        sentiment = load_news_sentiment(symbol) if use_sentiment else 0.0

        lstm_adj = apply_sentiment_adjustment(lstm_pred, sentiment, sentiment_intensity)
        arima_adj = apply_sentiment_adjustment(arima_pred, sentiment, sentiment_intensity)

        rmse_lstm, mae_lstm, mape_lstm = metrics(y_true, lstm_adj)
        rmse_arima, mae_arima, mape_arima = metrics(y_true, arima_adj)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("News Sentiment", f"{sentiment:.3f}")
        c2.metric("LSTM RMSE", f"{rmse_lstm:.2f}")
        c3.metric("ARIMA RMSE", f"{rmse_arima:.2f}")
        best = "LSTM" if rmse_lstm < rmse_arima else "ARIMA"
        c4.metric("Best Model", best)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=close.index, y=close.values, name="Actual", line=dict(color="#1f77b4")))
        fig.add_trace(
            go.Scatter(
                x=test_index,
                y=lstm_adj,
                name="LSTM Forecast",
                line=dict(color="#2ca02c", dash="dash"),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=test_index,
                y=arima_adj,
                name="ARIMA Forecast",
                line=dict(color="#d62728", dash="dot"),
            )
        )
        fig.update_layout(
            title=f"{symbol} Price: Model Comparison",
            xaxis_title="Date",
            yaxis_title="Price",
            height=550,
            legend=dict(orientation="h"),
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Model Performance")
        perf = pd.DataFrame(
            {
                "Model": ["LSTM", "ARIMA"],
                "RMSE": [rmse_lstm, rmse_arima],
                "MAE": [mae_lstm, mae_arima],
                "MAPE %": [mape_lstm, mape_arima],
            }
        )
        st.dataframe(perf, use_container_width=True, hide_index=True)

        st.info(
            "Sentiment is estimated from recent Yahoo Finance headlines. "
            "Use this for analysis, not financial advice."
        )

    except Exception as exc:
        st.error(f"Failed to run models: {exc}")
else:
    st.write("Set parameters and click **Run Models**.")
