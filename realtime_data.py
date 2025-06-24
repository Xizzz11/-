import pandas as pd
import numpy as np
import requests
import logging
import time
from typing import List, Dict, Optional
import yfinance as yf
from datetime import datetime, timedelta
import pytz

# Настройка логирования
logger = logging.getLogger(__name__)

class CoinGeckoAPI:
    BASE_URL = "https://api.coingecko.com/api/v3"
    RATE_LIMIT_DELAY = 2

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "CryptoAnalyzer/2.0", "Accept": "application/json"})

    def fetch_ohlc_data(self, coin_id: str, days: int = 7) -> pd.DataFrame:
        endpoint = f"{self.BASE_URL}/coins/{coin_id}/ohlc"
        params = {"vs_currency": "usd", "days": days}
        try:
            logger.info(f"Получение OHLC для {coin_id}")
            response = self.session.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close"])
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            df["volume"] = np.random.uniform(100, 1000, len(df))  # Заместитель объема
            logger.info(f"Получено {len(df)} записей OHLC для {coin_id}")
            return df
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP ошибка при получении OHLC для {coin_id}: {e}")
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"Ошибка получения OHLC для {coin_id}: {str(e)}")
            return pd.DataFrame()

    def fetch_market_data(self, per_page: int = 250, page: int = 1) -> Optional[List[Dict]]:
        endpoint = f"{self.BASE_URL}/coins/markets"
        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": per_page,
            "page": page,
            "sparkline": False,
            "price_change_percentage": "24h"
        }
        try:
            logger.info(f"Отправка запроса к {endpoint}, страница {page}")
            response = self.session.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            if isinstance(data, dict) and "error" in data:
                logger.error(f"Ошибка API: {data['error']}")
                return None
            logger.info(f"Получено {len(data)} записей для страницы {page}")
            return data
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                logger.warning("Превышен лимит запросов. Ожидание 60 секунд...")
                time.sleep(60)
                return self.fetch_market_data(per_page, page)
            logger.error(f"HTTP ошибка: {e}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка запроса: {e}")
        return None

    def close(self):
        self.session.close()
        logger.info("Сессия API закрыта")

class YahooFinanceAPI:
    def fetch_market_data(self, tickers: List[str]) -> Optional[pd.DataFrame]:
        try:
            logger.info(f"Запрос данных Yahoo Finance для {len(tickers)} тикеров")
            data = []
            for ticker in tickers:
                yf_ticker = yf.Ticker(ticker)
                info = yf_ticker.info
                history = yf_ticker.history(period="1d")
                if not history.empty:
                    data.append({
                        "timestamp": datetime.now(pytz.timezone("US/Eastern")).isoformat(),
                        "symbol": ticker,
                        "name": info.get("longName", ticker),
                        "price_usd": history["Close"].iloc[-1],
                        "market_cap_usd": info.get("marketCap", 0.0),
                        "volume_24h_usd": history["Volume"].iloc[-1] * history["Close"].iloc[-1],
                        "percent_change_24h": ((history["Close"].iloc[-1] - history["Open"].iloc[-1]) / history["Open"].iloc[-1]) * 100,
                        "circulating_supply": info.get("sharesOutstanding", None),
                        "total_supply": info.get("sharesOutstanding", None)
                    })
            df = pd.DataFrame(data)
            logger.info(f"Получено {len(df)} записей от Yahoo Finance")
            return df
        except Exception as e:
            logger.error(f"Ошибка Yahoo Finance: {e}")
            return None

def fetch_realtime_data(currency: str, mode: str, api: CoinGeckoAPI) -> tuple[str, pd.DataFrame]:
    df = pd.DataFrame()
    try:
        if mode == "crypto":
            coin_ids = {"BTC": "bitcoin", "ETH": "ethereum", "XRP": "ripple", "LTC": "litecoin"}
            coin_id = coin_ids.get(currency)
            if not coin_id:
                logger.error(f"Валюта {currency} не поддерживается")
                return f"Валюта {currency} не поддерживается!", df
            df = api.fetch_ohlc_data(coin_id)
            if df.empty:
                logger.error(f"Не удалось загрузить данные для {currency}")
                return f"Не удалось загрузить данные для {currency}!", df
            df["symbol"] = currency
            df.set_index("timestamp", inplace=True)
            logger.info(f"Данные в реальном времени загружены: {df.shape}")
            return f"Данные реального времени загружены для {currency}! Размер: {df.shape}", df
        else:  # big_data mode
            timestamp = datetime.now(pytz.timezone("US/Eastern")).isoformat()
            max_coins = 1000
            stock_tickers = ["AAPL", "TSLA", "MSFT", "GLD", "SPY"]
            all_data = []
            per_page = 250
            page = 1
            while True:
                data = api.fetch_market_data(per_page=per_page, page=page)
                if not data:
                    break
                all_data.extend(data)
                if max_coins and len(all_data) >= max_coins:
                    all_data = all_data[:max_coins]
                    break
                page += 1
                time.sleep(api.RATE_LIMIT_DELAY)
            if all_data:
                df = process_crypto_data(all_data, timestamp)
                yf_api = YahooFinanceAPI()
                stock_df = yf_api.fetch_market_data(stock_tickers)
                if stock_df is not None:
                    df = pd.concat([df, stock_df], ignore_index=True)
                logger.info(f"Большие данные загружены: {df.shape}")
                return f"Большие данные загружены! Размер: {df.shape}", df
            logger.error("Не удалось загрузить большие данные")
            return "Не удалось загрузить большие данные!", df
    except Exception as e:
        logger.error(f"Ошибка в fetch_realtime_data: {str(e)}")
        return f"Ошибка при получении данных: {str(e)}", df

def process_crypto_data(raw_data: List[Dict], timestamp: str) -> pd.DataFrame:
    data = []
    try:
        for coin in raw_data:
            if coin.get("current_price") is not None:
                data.append({
                    "timestamp": timestamp,
                    "symbol": coin.get("symbol", "").upper(),
                    "name": coin.get("name", ""),
                    "price_usd": coin.get("current_price", 0.0),
                    "market_cap_usd": coin.get("market_cap", 0.0),
                    "volume_24h_usd": coin.get("total_volume", 0.0),
                    "percent_change_24h": coin.get("price_change_percentage_24h", 0.0),
                    "circulating_supply": coin.get("circulating_supply", None),
                    "total_supply": coin.get("total_supply", None)
                })
        df = pd.DataFrame(data)
        logger.info(f"Обработано {len(df)} криптовалютных записей")
        return df
    except Exception as e:
        logger.error(f"Ошибка обработки криптоданных: {str(e)}")
        return pd.DataFrame()