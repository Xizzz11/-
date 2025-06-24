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

Подробная документация доступна в [GitHub Wiki](https://github.com/your-username/crypto-analyzer-pro/wiki). Ключевые разделы:
- [Начало работы](https://github.com/your-username/crypto-analyzer-pro/wiki/Getting-Started)
- [Интеграция API](https://github.com/your-username/crypto-analyzer-pro/wiki/API-Integration)
- [Руководство по визуализации](https://github.com/your-username/crypto-analyzer-pro/wiki/Visualization-Guide)
- [Решение проблем](https://github.com/your-username/crypto-analyzer-pro/wiki/Troubleshooting)

## 🤝 Участие в проекте

Мы приветствуем ваши вклады! Пожалуйста, следуйте следующим шагам:

1. Форкните репозиторий.
2. Создайте ветку для новой функции (`git checkout -b feature/your-feature`).
3. Зафиксируйте изменения (`git commit -m 'Добавьте вашу функцию'`).
4. Отправьте изменения в ветку (`git push origin feature/your-feature`).
5. Откройте Pull Request.

Подробности в [CONTRIBUTING.md](CONTRIBUTING.md).

## 📜 Лицензия

Этот проект распространяется под лицензией MIT. Подробнее см. [LICENSE](LICENSE).

## 🙏 Благодарности

- [CoinGecko API](https://www.coingecko.com/en/api) за данные о криптовалютах.
- [Yahoo Finance](https://github.com/ranaroussi/yfinance) за данные о акциях.
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) за фреймворк для графического интерфейса.
- [Matplotlib](https://matplotlib.org/) и [MPLFinance](https://github.com/matplotlib/mplfinance) за визуализации.

## 📬 Контакты

По вопросам или предложениям создавайте issue или пишите на [your-email@example.com](mailto:your-email@example.com).

Удачного анализа! 🚀
