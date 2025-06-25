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

![image](https://github.com/user-attachments/assets/ca7df2d2-71dd-4a10-afcf-01c3e23f0dd8)

![image](https://github.com/user-attachments/assets/c0cda0b1-3f07-40ba-bf19-fda56c7910f3)

![image](https://github.com/user-attachments/assets/57beb404-ae33-4a8c-8f0b-6ff1d0531da1)

![image](https://github.com/user-attachments/assets/ccb5c7bd-a56e-4280-bbb7-e87efd95ca18)

![image](https://github.com/user-attachments/assets/17e40893-0258-4eaa-a5cd-b59d5bac85c7)

![image](https://github.com/user-attachments/assets/1997a9fe-f267-4afe-8aa6-77851133c1ac)

![image](https://github.com/user-attachments/assets/f80bd762-9091-44d1-96b5-078bc8061824)

![image](https://github.com/user-attachments/assets/5413741f-2180-4634-b377-05b1f72ffc7c)

![image](https://github.com/user-attachments/assets/622e1afd-3dcc-4431-80a5-1d01ba684d03)

![image](https://github.com/user-attachments/assets/03d62ade-87e4-4799-bd2a-c5b1d909d651)

![image](https://github.com/user-attachments/assets/a2fa5a68-a1f7-4ffa-b841-76bf633436e2)

![image](https://github.com/user-attachments/assets/7f5f6b52-f57c-4d3e-a916-885c4127ef69)

![image](https://github.com/user-attachments/assets/ea90d969-c1bd-4145-a71e-514d2868b09f)

![image](https://github.com/user-attachments/assets/e9fe7683-9dd5-4563-9827-57d794cc262a)

![image](https://github.com/user-attachments/assets/4b5c2e83-e440-4f00-9953-9484a9f878e7)

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

Подробная документация доступна в (# 📚 Wiki для CryptoAnalyzer Pro](https://github.com/Xizzz11/-/wiki)

