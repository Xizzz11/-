# 💎 CryptoAnalyzer Pro

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

CryptoAnalyzer Pro — это мощное приложение на Python для анализа данных о криптовалютах и финансовых рынках. Оно предоставляет возможность получения данных в реальном времени, технического анализа, визуализации данных и удобный графический интерфейс, созданный с использованием CustomTkinter. Инструмент поддерживает как анализ отдельных криптовалют (например, BTC, ETH), так и обработку больших объемов рыночных данных, интегрируя API CoinGecko и Yahoo Finance.

## 🌟 Возможности

- **Данные в реальном времени**: Получение актуальных данных о криптовалютах через CoinGecko API и данных о акциях через Yahoo Finance.
- **Технические индикаторы**: Расчет показателей, таких как RSI, MACD, Bollinger Bands и волатильность.
- **Визуализация данных**: Создание графиков, включая свечные, гистограммы, матрицы корреляции и другие, с использованием Matplotlib и MPLFinance.
- **Графический интерфейс**: Интуитивно понятный интерфейс с темами "темная/светлая", созданный на CustomTkinter.
- **Очистка данных**: Обработка пропущенных значений и выбросов для надежного анализа.
- **Экспорт результатов**: Сохранение результатов в форматах CSV или PDF.
- **Режим больших данных**: Анализ крупных наборов данных по множеству активов.

## 📸 Скриншоты

![Скриншот интерфейса](screenshots/main_gui.png)
![Свечной график](screenshots/btc_candlestick.png)

## 🚀 Начало работы

### Необходимые условия

- Python 3.8+
- Менеджер пакетов Pip
- Git (опционально, для клонирования репозитория)

### Установка

1. **Клонирование репозитория**:
   ```bash
   git clone https://github.com/your-username/crypto-analyzer-pro.git
   cd crypto-analyzer-pro
   ```

2. **Создание виртуального окружения** (рекомендуется):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Для Windows: venv\Scripts\activate
   ```

3. **Установка зависимостей**:
   ```bash
   pip install -r requirements.txt
   ```

   Пример `requirements.txt`:
   ```
   pandas>=2.0.0
   numpy>=1.24.0
   requests>=2.31.0
   yfinance>=0.2.40
   matplotlib>=3.8.0
   seaborn>=0.13.0
   customtkinter>=5.2.0
   pillow>=10.0.0
   mplfinance>=0.12.10
   ```

4. **Запуск приложения**:
   ```bash
   python main.py
   ```

   При первом запуске будут созданы примеры CSV-файлов для BTC, ETH, XRP и LTC, если они отсутствуют, и откроется графический интерфейс.

## 🛠 Использование

1. **Запуск приложения**:
   - Выполните `python main.py`, чтобы открыть графический интерфейс.
   - Выберите **Режим криптовалют** (для анализа одной криптовалюты) или **Режим больших данных** (для анализа рынка в целом).

2. **Режим криптовалют**:
   - Выберите валюту (BTC, ETH, XRP, LTC).
   - Загрузите данные из CSV или получите их в реальном времени через CoinGecko.
   - Проведите анализ, визуализируйте графики (например, свечные, MACD) или очистите данные.
   - Экспортируйте результаты в формате CSV или PDF.

3. **Режим больших данных**:
   - Получите рыночные данные для до 1000 криптовалют и выбранных акций (например, AAPL, TSLA).
   - Проанализируйте показатели, такие как рыночная капитализация и отношение объема к капитализации.
   - Визуализируйте корреляции или точечные диаграммы.

4. **Визуализация**:
   - Выберите тип графика (например, свечной, гистограмма, Bollinger Bands).
   - Выберите числовые или категориальные столбцы для пользовательских графиков.
   - Переключайтесь между темной и светлой темами.

5. **Пример данных**:
   - Приложение создает примеры CSV-файлов (`BTC_data.csv` и др.) в директории проекта для тестирования.

## 📝 Wiki

Подробная документация доступна в [GitHub Wiki](# 📚 Wiki для CryptoAnalyzer Pro

## Оглавление
1. [Установка и настройка](#установка-и-настройка)
2. [API интеграции](#api-интеграции)
3. [Основные функции](#основные-функции)
4. [Примеры использования](#примеры-использования)
5. [Визуализация данных](#визуализация-данных)
6. [FAQ и решение проблем](#faq-и-решение-проблем)

---

## Установка и настройка

### Требования
- Python 3.8+
- Установленные зависимости из `requirements.txt`

```bash
pip install -r requirements.txt
```

### Настройка API ключей (опционально)
Для расширенного функционала создайте файл `config.json`:

```json
{
  "coingecko_api_key": "ваш_ключ",
  "proxy": "http://ваш_прокси:порт"
}
```

---

## API интеграции

### CoinGecko API
Основной класс для работы с криптовалютами:

```python
class CoinGeckoAPI:
    BASE_URL = "https://api.coingecko.com/api/v3"
    
    def fetch_ohlc_data(self, coin_id: str, days: int = 7) -> pd.DataFrame:
        """Получение OHLC данных"""
        endpoint = f"{self.BASE_URL}/coins/{coin_id}/ohlc"
        params = {"vs_currency": "usd", "days": days}
        response = self.session.get(endpoint, params=params)
        # ... обработка ответа
```

### Yahoo Finance API
Для работы с акциями:

```python
class YahooFinanceAPI:
    def fetch_market_data(self, tickers: List[str]) -> Optional[pd.DataFrame]:
        try:
            data = []
            for ticker in tickers:
                yf_ticker = yf.Ticker(ticker)
                info = yf_ticker.info
                # ... сбор данных
            return pd.DataFrame(data)
```

---

## Основные функции

### Загрузка данных
```python
async def load_data_async(self, chunk_size: int = 10000) -> str:
    """Асинхронная загрузка CSV"""
    if not self.file_path.exists():
        return "Файл не найден!"
    chunks = pd.read_csv(self.file_path, chunksize=chunk_size)
    self.df = pd.concat(chunks, ignore_index=False)
```

### Расчет индикаторов
```python
def calculate_crypto_metrics(self):
    """Расчет RSI, MACD и других показателей"""
    # RSI
    delta = self.df['close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss.replace(0, np.finfo(float).eps)
    self.df['rsi'] = 100 - (100 / (1 + rs))
    
    # MACD
    ema_12 = self.df['close'].ewm(span=12, adjust=False).mean()
    ema_26 = self.df['close'].ewm(span=26, adjust=False).mean()
    self.df['macd'] = ema_12 - ema_26
```

---

## Примеры использования

### Анализ одной криптовалюты
```python
analyzer = CryptoAnalyzer(currency="BTC", mode="crypto")
await analyzer.load_data_async()
analysis_result = analyzer.basic_analysis()
```

### Работа с большими данными
```python
analyzer = CryptoAnalyzer(mode="big_data")
status, df = fetch_realtime_data("BTC", "big_data", CoinGeckoAPI())
```

---

## Визуализация данных

### Доступные графики
```python
def visualize_data(self, theme: str = 'dark') -> tuple[str, list[Path]]:
    available_charts = []
    if self.mode == "crypto":
        available_charts.extend(['Японские свечи', 'MACD'])
    if numeric_col:
        available_charts.extend(['Гистограмма', 'Ящик с усами'])
```

### Пример создания свечного графика
```python
ohlcv = self.df[['open', 'high', 'low', 'close', 'volume']].tail(100)
mpf.plot(ohlcv, type='candle', style='nightclouds', 
         title=f'График {self.currency}')
```

---

## FAQ и решение проблем

### Ошибка лимита запросов
```python
except requests.exceptions.HTTPError as e:
    if response.status_code == 429:
        logger.warning("Превышен лимит запросов. Ожидание 60 секунд...")
        time.sleep(60)
        return self.fetch_market_data(per_page, page)
```

### Проблемы с данными
1. **Пропущенные значения**:
```python
self.df = self.df.fillna(method='ffill')
```

2. **Выбросы**:
```python
Q1 = self.df[column].quantile(0.25)
Q3 = self.df[column].quantile(0.75)
IQR = Q3 - Q1
self.df = self.df[(self.df[column] >= Q1 - 1.5*IQR) & (self.df[column] <= Q3 + 1.5*IQR)]
```

---

## Полезные ссылки
- [Официальная документация CoinGecko](https://www.coingecko.com/en/api)
- [Документация yfinance](https://github.com/ranaroussi/yfinance)
- [Примеры mplfinance](https://github.com/matplotlib/mplfinance)

Для дополнительных вопросов создавайте issue в репозитории проекта!). Ключевые разделы:
- [Начало работы](https://github.com/your-username/crypto-analyzer-pro/wiki/Getting-Started)
- [Интеграция API](https://github.com/your-username/crypto-analyzer-pro/wiki/API-Integration)
- [Руководство по визуализации](https://github.com/your-username/crypto-analyzer-pro/wiki/Visualization-Guide)
- [Решение проблем](https://github.com/your-username/crypto-analyzer-pro/wiki/Troubleshooting)


