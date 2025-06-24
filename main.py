import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
import customtkinter as ctk
from PIL import Image, ImageTk
from datetime import datetime, timedelta
import asyncio
import threading
import logging
import pytz
import mplfinance as mpf
import matplotlib.backends.backend_pdf
import webbrowser
import io
import json
import time
import sys
import os
from tkinter import filedialog
try:
    from realtime_data import CoinGeckoAPI, fetch_realtime_data
except ImportError:
    print("Модуль realtime_data не найден. Функция получения данных в реальном времени недоступна.")

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("crypto_analyzer_log.txt", encoding="utf-8"), logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

matplotlib.use('Agg')

class CryptoAnalyzer:
    def __init__(self, file_path: str = "", currency: str = "BTC", mode: str = "crypto"):
        """Инициализация анализатора криптовалют."""
        self.file_path = Path(file_path) if file_path else None
        self.currency = currency.upper()
        self.mode = mode
        self.df = pd.DataFrame()
        self.output_dir = Path("crypto_results") / f"{self.mode}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.api = CoinGeckoAPI() if 'CoinGeckoAPI' in globals() else None
        logger.info(f"Инициализирован CryptoAnalyzer в режиме {self.mode}, валюта: {self.currency}, файл: {self.file_path}")

    def fetch_realtime_data(self) -> str:
        """Получение данных в реальном времени."""
        if not self.api:
            logger.error("API CoinGecko недоступен")
            return "API CoinGecko недоступен!"
        result, df = fetch_realtime_data(self.currency, self.mode, self.api)
        self.df = df
        return result

    async def load_data_async(self, chunk_size: int = 10000) -> str:
        """Асинхронная загрузка данных из CSV."""
        if not self.file_path or not self.file_path.exists():
            logger.error(f"Файл не найден: {self.file_path}")
            return f"Файл {self.file_path} не найден! Попробуйте загрузить данные реального времени."
        try:
            if self.file_path.suffix == '.csv':
                chunks = pd.read_csv(self.file_path, chunksize=chunk_size)
                self.df = pd.concat(chunks, ignore_index=False)
                if self.mode == "crypto" and 'symbol' in self.df.columns:
                    self.df = self.df[self.df['symbol'].str.upper() == self.currency]
                    if self.df.empty:
                        logger.error(f"Нет данных для валюты {self.currency}")
                        return f"Нет данных для валюты {self.currency} в файле!"
                if 'timestamp' in self.df.columns:
                    self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
                    self.df.set_index('timestamp', inplace=True)
                if self.mode == "crypto" and 'volume' not in self.df.columns:
                    self.df['volume'] = self.df['close'].mean() * 0.1
                self.df.sort_index(inplace=True, errors='ignore')
                logger.info(f"Данные загружены: {self.df.shape}, столбцы: {list(self.df.columns)}")
                return f"Данные загружены для {self.mode}! Размер: {self.df.shape}\nСтолбцы: {list(self.df.columns)}"
            else:
                raise ValueError("Поддерживается только формат CSV")
        except Exception as e:
            logger.error(f"Ошибка загрузки данных: {str(e)}")
            return f"Ошибка загрузки данных: {str(e)}"

    def calculate_crypto_metrics(self) -> None:
        """Расчет технических индикаторов для криптовалют."""
        if self.df.empty or len(self.df) < 26:
            logger.error("Недостаточно данных для расчета метрик")
            return
        try:
            if self.mode == "crypto":
                self.df['log_return'] = np.log(self.df['close'] / self.df['close'].shift(1))
                self.df['volatility'] = self.df['log_return'].rolling(window=14).std() * np.sqrt(365) * 100
                self.df['sma_20'] = self.df['close'].rolling(window=20).mean()
                delta = self.df['close'].diff()
                gain = delta.where(delta > 0, 0)
                loss = -delta.where(delta < 0, 0)
                avg_gain = gain.rolling(window=14).mean()
                avg_loss = loss.rolling(window=14).mean()
                rs = avg_gain / avg_loss.replace(0, np.finfo(float).eps)
                self.df['rsi'] = 100 - (100 / (1 + rs))
                self.df['bb_middle'] = self.df['close'].rolling(window=20).mean()
                self.df['bb_std'] = self.df['close'].rolling(window=20).std()
                self.df['bb_upper'] = self.df['bb_middle'] + 2 * self.df['bb_std']
                self.df['bb_lower'] = self.df['bb_middle'] - 2 * self.df['bb_std']
                ema_12 = self.df['close'].ewm(span=12, adjust=False).mean()
                ema_26 = self.df['close'].ewm(span=26, adjust=False).mean()
                self.df['macd'] = ema_12 - ema_26
                self.df['macd_signal'] = self.df['macd'].ewm(span=9, adjust=False).mean()
                self.df['macd_hist'] = self.df['macd'] - self.df['macd_signal']
            else:  # big_data mode
                self.df['percent_change_24h'] = self.df['percent_change_24h'].astype(float)
                self.df['market_cap_rank'] = self.df['market_cap_usd'].rank(method='dense', ascending=False)
                self.df['volume_to_market_cap'] = self.df['volume_24h_usd'] / self.df['market_cap_usd']
                self.df['price_volatility'] = self.df.groupby('symbol')['price_usd'].transform(
                    lambda x: x.rolling(window=14, min_periods=1).std())
            logger.info(f"Рассчитаны метрики для режима {self.mode}")
        except Exception as e:
            logger.error(f"Ошибка расчета метрик: {str(e)}")

    def basic_analysis(self) -> str:
        """Базовый анализ данных."""
        if self.df.empty:
            logger.error("Данные не загружены")
            return "Данные не загружены!"
        try:
            self.calculate_crypto_metrics()
            output = [f"💎 Анализ для {self.mode}:\n"]
            if self.mode == "crypto":
                latest_data = self.df[['close', 'volatility', 'sma_20', 'rsi']].tail(5)
                if not latest_data.empty:
                    change_percent = ((self.df['close'].iloc[-1] - self.df['close'].iloc[-2]) /
                                      self.df['close'].iloc[-2] * 100).round(2)
                    output.append(f"📈 Последняя цена: {self.df['close'].iloc[-1]:.2f} USD\n")
                    output.append(f"🔄 Изменение цены (1 день): {change_percent}% "
                                  f"{'(рост)' if change_percent > 0 else '(падение)'}\n")
                    output.append(f"📊 Волатильность (14 дней): {self.df['volatility'].iloc[-1]:.2f}%\n")
                    output.append(f"📉 SMA 20 дней: {self.df['sma_20'].iloc[-1]:.2f} USD\n")
                    output.append(f"📊 RSI (14 дней): {self.df['rsi'].iloc[-1]:.2f} "
                                  f"{'(перекуплен)' if self.df['rsi'].iloc[-1] > 70 else '(перепродан)' if self.df['rsi'].iloc[-1] < 30 else '(нейтрален)'}\n")
                    output.append(f"📈 Последние 5 записей:\n{latest_data.to_string()}\n")
            else:  # big_data mode
                latest_data = self.df[['symbol', 'price_usd', 'market_cap_usd', 'percent_change_24h',
                                       'volume_to_market_cap']].tail(5)
                if not latest_data.empty:
                    output.append(f"📈 Общее количество активов: {len(self.df)}\n")
                    output.append(f"📊 Средняя цена: {self.df['price_usd'].mean():.2f} USD\n")
                    output.append(f"📉 Среднее изменение за 24ч: {self.df['percent_change_24h'].mean():.2f}%\n")
                    output.append(f"📈 Последние 5 записей:\n{latest_data.to_string()}\n")
            output.append(f"🚀 Пропущенные значения:\n{self.df.isnull().sum().to_string()}\n")
            analysis_path = self.output_dir / f'{self.mode}_analysis.txt'
            with open(analysis_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(output))
            logger.info(f"Анализ сохранен: {analysis_path}")
            return "\n".join(output)
        except Exception as e:
            logger.error(f"Ошибка в базовом анализе: {str(e)}")
            return f"Ошибка в анализе: {str(e)}"

    def clean_data(self) -> str:
        """Очистка данных от выбросов и пропусков."""
        if self.df.empty:
            logger.error("Данные не загружены")
            return "Данные не загружены!"
        try:
            initial_count = len(self.df)
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns
            self.df[numeric_cols] = self.df[numeric_cols].astype(float)
            self.df = self.df.fillna(method='ffill')
            for column in numeric_cols:
                Q1 = self.df[column].quantile(0.25)
                Q3 = self.df[column].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                self.df = self.df[(self.df[column] >= lower_bound) & (self.df[column] <= upper_bound)]
            new_count = len(self.df)
            if new_count == 0:
                logger.warning(f"Нет строк после очистки: {initial_count}")
                return f"Нет строк после очистки! Начальный размер: {initial_count}"
            logger.info(f"Данные очищены: {new_count} строк")
            return f"Данные очищены! Новый размер: {new_count}"
        except Exception as e:
            logger.error(f"Ошибка очистки данных: {str(e)}")
            return f"Ошибка очистки данных: {str(e)}"

    def visualize_data(self, numeric_col: str = None, numeric_col2: str = None,
                       categorical_col: str = None, theme: str = 'dark',
                       chart_type: str = None) -> tuple[str, list[Path]]:
        """Визуализация данных с различными типами графиков."""
        if self.df.empty:
            logger.error("Данные не загружены")
            return "Данные не загружены!", []
        if len(self.df) < 10:
            logger.error("Недостаточно данных")
            return "Недостаточно данных (минимум 10 строк)!", []
        try:
            self.calculate_crypto_metrics()
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns
            categorical_cols = self.df.select_dtypes(include=['object', 'category']).columns
            numeric_col = (numeric_col if numeric_col in numeric_cols else
                           'close' if self.mode == "crypto" and 'close' in numeric_cols else
                           'price_usd' if 'price_usd' in numeric_cols else
                           numeric_cols[0] if numeric_cols.size > 0 else None)
            numeric_col2 = (numeric_col2 if numeric_col2 in numeric_cols else
                            'volume' if self.mode == "crypto" and 'volume' in numeric_cols else
                            'volume_24h_usd' if 'volume_24h_usd' in numeric_cols else
                            numeric_cols[1] if numeric_cols.size > 1 else None)
            categorical_col = (categorical_col if categorical_col in categorical_cols else
                               categorical_cols[0] if categorical_cols.size > 0 else None)

            sns.set_style("whitegrid" if theme == 'white' else "darkgrid")
            bg_color = '#F5F5F5' if theme == 'white' else '#121212'
            text_color = '#212121' if theme == 'white' else '#FFFFFF'
            plot_color = '#0288D1' if theme == 'white' else '#FF9800'
            accent_color = '#D81B60' if theme == 'white' else '#2196F3'

            image_paths: list[Path] = []
            available_charts = []
            if self.mode == "crypto" and all(col in self.df.columns for col in ['open', 'high', 'low', 'close']) and len(self.df) >= 50:
                available_charts.extend(['Японские свечи', 'Свечной график крипты'])
            if numeric_col:
                available_charts.extend(['Гистограмма', 'Ящик с усами', 'Линейный', 'Заполненный', 'Плотность'])
            if numeric_col and numeric_col2:
                available_charts.extend(['Точечный', 'Цена-Объем'])
            if len(numeric_cols) > 1:
                available_charts.append('Корреляция')
            if self.mode == "crypto" and 'bb_upper' in self.df.columns and len(self.df) >= 20:
                available_charts.append('Полосы Боллинджера')
            if self.mode == "crypto" and 'macd' in self.df.columns and len(self.df) >= 26:
                available_charts.append('MACD')
            chart_types = [chart_type] if chart_type and chart_type in available_charts else available_charts

            for chart in chart_types:
                try:
                    if chart == 'Японские свечи' and self.mode == "crypto":
                        ohlcv = self.df[['open', 'high', 'low', 'close', 'volume']].tail(100)
                        if not ohlcv.empty:
                            fig, ax = plt.subplots(figsize=(10, 6), facecolor=bg_color)
                            mpf.plot(ohlcv, type='candle', style='charles' if theme == 'white' else 'nightclouds',
                                     ax=ax, volume=True, title=f'Японские свечи {self.currency}',
                                     title_kwargs={'color': text_color, 'fontsize': 16},
                                     facecolor=bg_color, edgecolor=text_color)
                            fig.patch.set_facecolor(bg_color)
                            candle_path = self.output_dir / f'{self.currency}_candlestick.png'
                            plt.savefig(candle_path, bbox_inches='tight', facecolor=bg_color, dpi=300)
                            plt.close(fig)
                            if candle_path.exists():
                                image_paths.append(candle_path)
                                logger.info(f"Японские свечи сохранены: {candle_path}")

                    elif chart == 'Свечной график крипты' and self.mode == "crypto":
                        ohlcv = self.df[['open', 'high', 'low', 'close', 'volume']].tail(100)
                        if not ohlcv.empty and 'rsi' in self.df.columns and 'macd' in self.df.columns:
                            apds = [
                                mpf.make_addplot(self.df['rsi'].tail(100), panel='lower', color=accent_color,
                                                 title='RSI', ylabel='RSI', secondary_y=False),
                                mpf.make_addplot(self.df['macd'].tail(100), panel='lower', color=plot_color,
                                                 title='MACD', ylabel='MACD'),
                                mpf.make_addplot(self.df['macd_signal'].tail(100), panel='lower', color=accent_color,
                                                 secondary_y=True, linestyle='--')
                            ]
                            fig, axes = mpf.plot(ohlcv, type='candle', style='charles' if theme == 'white' else 'nightclouds',
                                                 addplot=apds, volume=True, figscale=1.2,
                                                 title=f'Свечной график {self.currency}',
                                                 title_kwargs={'color': text_color, 'fontsize': 16},
                                                 facecolor=bg_color, edgecolor=text_color, returnfig=True)
                            fig.patch.set_facecolor(bg_color)
                            crypto_path = self.output_dir / f'{self.currency}_crypto_candlestick.png'
                            plt.savefig(crypto_path, bbox_inches='tight', facecolor=bg_color, dpi=300)
                            plt.close(fig)
                            if crypto_path.exists():
                                image_paths.append(crypto_path)
                                logger.info(f"Свечной график крипты сохранен: {crypto_path}")

                    elif chart == 'Гистограмма' and numeric_col:
                        fig, ax = plt.subplots(figsize=(10, 6), facecolor=bg_color)
                        data = self.df[numeric_col].dropna()
                        if not data.empty:
                            sns.histplot(data, bins=30, color=plot_color, edgecolor=accent_color, alpha=0.7)
                            ax.set_title(f'Гистограмма {numeric_col}', color=text_color, fontsize=16, pad=10)
                            ax.set_xlabel(numeric_col, color=text_color, fontsize=12)
                            ax.set_ylabel('Частота', color=text_color, fontsize=12)
                            ax.grid(True, linestyle='--', alpha=0.3, color=accent_color)
                            fig.patch.set_facecolor(bg_color)
                            hist_path = self.output_dir / f'hist_{self.mode}_{numeric_col}.png'
                            plt.savefig(hist_path, bbox_inches='tight', facecolor=bg_color, dpi=300)
                            plt.close(fig)
                            if hist_path.exists():
                                image_paths.append(hist_path)
                                logger.info(f"Гистограмма сохранена: {hist_path}")

                    elif chart == 'Ящик с усами' and numeric_col:
                        fig, ax = plt.subplots(figsize=(10, 6), facecolor=bg_color)
                        data = self.df[numeric_col].dropna()
                        if not data.empty:
                            sns.boxplot(y=data, color=plot_color)
                            ax.set_title(f'Ящик с усами {numeric_col}', color=text_color, fontsize=16, pad=10)
                            ax.set_ylabel(numeric_col, color=text_color, fontsize=12)
                            ax.grid(True, linestyle='--', alpha=0.3, color=accent_color)
                            fig.patch.set_facecolor(bg_color)
                            box_path = self.output_dir / f'box_{self.mode}_{numeric_col}.png'
                            plt.savefig(box_path, bbox_inches='tight', facecolor=bg_color, dpi=300)
                            plt.close(fig)
                            if box_path.exists():
                                image_paths.append(box_path)
                                logger.info(f"Ящик с усами сохранен: {box_path}")

                    elif chart == 'Линейный' and numeric_col:
                        fig, ax = plt.subplots(figsize=(10, 6), facecolor=bg_color)
                        data = self.df[numeric_col].dropna()
                        if not data.empty and not self.df.index.empty:
                            ax.plot(self.df.index, data, color=plot_color, linewidth=2, label=numeric_col)
                            ax.set_title(f'Линейный график {numeric_col}', color=text_color, fontsize=16, pad=10)
                            ax.set_xlabel('Дата', color=text_color, fontsize=12)
                            ax.set_ylabel(numeric_col, color=text_color, fontsize=12)
                            ax.grid(True, linestyle='--', alpha=0.3, color=accent_color)
                            ax.legend(facecolor=bg_color, edgecolor=accent_color, labelcolor=text_color)
                            fig.patch.set_facecolor(bg_color)
                            line_path = self.output_dir / f'line_{self.mode}_{numeric_col}.png'
                            plt.savefig(line_path, bbox_inches='tight', facecolor=bg_color, dpi=300)
                            plt.close(fig)
                            if line_path.exists():
                                image_paths.append(line_path)
                                logger.info(f"Линейный график сохранен: {line_path}")

                    elif chart == 'Заполненный' and numeric_col:
                        fig, ax = plt.subplots(figsize=(10, 6), facecolor=bg_color)
                        data = self.df[numeric_col].dropna()
                        if not data.empty and not self.df.index.empty:
                            ax.fill_between(self.df.index, data, color=plot_color, alpha=0.4)
                            ax.plot(self.df.index, data, color=plot_color, linewidth=2)
                            ax.set_title(f'Заполненный график {numeric_col}', color=text_color, fontsize=16, pad=10)
                            ax.set_xlabel('Дата', color=text_color, fontsize=12)
                            ax.set_ylabel(numeric_col, color=text_color, fontsize=12)
                            ax.grid(True, linestyle='--', alpha=0.3, color=accent_color)
                            fig.patch.set_facecolor(bg_color)
                            area_path = self.output_dir / f'area_{self.mode}_{numeric_col}.png'
                            plt.savefig(area_path, bbox_inches='tight', facecolor=bg_color, dpi=300)
                            plt.close(fig)
                            if area_path.exists():
                                image_paths.append(area_path)
                                logger.info(f"Заполненный график сохранен: {area_path}")

                    elif chart == 'Плотность' and numeric_col:
                        fig, ax = plt.subplots(figsize=(10, 6), facecolor=bg_color)
                        data = self.df[numeric_col].dropna()
                        if not data.empty:
                            sns.kdeplot(data, color=plot_color, fill=True, alpha=0.4)
                            ax.set_title(f'Плотность {numeric_col}', color=text_color, fontsize=16, pad=10)
                            ax.set_xlabel(numeric_col, color=text_color, fontsize=12)
                            ax.set_ylabel('Плотность', color=text_color, fontsize=12)
                            ax.grid(True, linestyle='--', alpha=0.3, color=accent_color)
                            fig.patch.set_facecolor(bg_color)
                            kde_path = self.output_dir / f'kde_{self.mode}_{numeric_col}.png'
                            plt.savefig(kde_path, bbox_inches='tight', facecolor=bg_color, dpi=300)
                            plt.close(fig)
                            if kde_path.exists():
                                image_paths.append(kde_path)
                                logger.info(f"График плотности сохранен: {kde_path}")

                    elif chart == 'Точечный' and numeric_col and numeric_col2:
                        fig, ax = plt.subplots(figsize=(10, 6), facecolor=bg_color)
                        data = self.df[[numeric_col, numeric_col2]].dropna()
                        if not data.empty:
                            sns.scatterplot(x=data[numeric_col], y=data[numeric_col2], color=plot_color, s=100, alpha=0.6)
                            ax.set_title(f'Точечный график: {numeric_col} vs {numeric_col2}', color=text_color, fontsize=16, pad=10)
                            ax.set_xlabel(numeric_col, color=text_color, fontsize=12)
                            ax.set_ylabel(numeric_col2, color=text_color, fontsize=12)
                            ax.grid(True, linestyle='--', alpha=0.3, color=accent_color)
                            fig.patch.set_facecolor(bg_color)
                            scatter_path = self.output_dir / f'scatter_{self.mode}_{numeric_col}_{numeric_col2}.png'
                            plt.savefig(scatter_path, bbox_inches='tight', facecolor=bg_color, dpi=300)
                            plt.close(fig)
                            if scatter_path.exists():
                                image_paths.append(scatter_path)
                                logger.info(f"Точечный график сохранен: {scatter_path}")

                    elif chart == 'Цена-Объем' and numeric_col and numeric_col2:
                        fig, ax1 = plt.subplots(figsize=(10, 6), facecolor=bg_color)
                        ax2 = ax1.twinx()
                        data = self.df[[numeric_col, numeric_col2]].dropna()
                        if not data.empty and not self.df.index.empty:
                            ax1.plot(data.index, data[numeric_col], color=plot_color, label=numeric_col)
                            ax2.bar(data.index, data[numeric_col2], color=accent_color, alpha=0.5)
                            ax1.set_title(f'Цена vs Объем', color=text_color, fontsize=16, pad=10)
                            ax1.set_xlabel('Дата', color=text_color, fontsize=12)
                            ax1.set_ylabel(numeric_col, color=text_color, fontsize=12)
                            ax2.set_ylabel(numeric_col2, color=accent_color, fontsize=12)
                            ax1.grid(True, linestyle='--', alpha=0.3, color=accent_color)
                            ax1.legend(facecolor=bg_color, edgecolor=accent_color, labelcolor=text_color)
                            fig.patch.set_facecolor(bg_color)
                            vp_path = self.output_dir / f'volumeprice_{self.mode}_{numeric_col}_{numeric_col2}.png'
                            plt.savefig(vp_path, bbox_inches='tight', facecolor=bg_color, dpi=300)
                            plt.close(fig)
                            if vp_path.exists():
                                image_paths.append(vp_path)
                                logger.info(f"График Цена-Объем сохранен: {vp_path}")

                    elif chart == 'Корреляция' and len(numeric_cols) > 1:
                        fig, ax = plt.subplots(figsize=(10, 6), facecolor=bg_color)
                        corr_matrix = self.df[numeric_cols].corr()
                        if not corr_matrix.empty:
                            sns.heatmap(corr_matrix, annot=True, cmap='Blues' if theme == 'white' else 'YlOrBr',
                                        ax=ax, annot_kws={"size": 12, "color": text_color}, linewidths=0.5)
                            ax.set_title('Матрица корреляции', color=text_color, fontsize=16, pad=10)
                            fig.patch.set_facecolor(bg_color)
                            corr_path = self.output_dir / f'correlation_{self.mode}.png'
                            plt.savefig(corr_path, bbox_inches='tight', facecolor=bg_color, dpi=300)
                            plt.close(fig)
                            if corr_path.exists():
                                image_paths.append(corr_path)
                                logger.info(f"Матрица корреляции сохранена: {corr_path}")

                    elif chart == 'Полосы Боллинджера' and self.mode == "crypto":
                        fig, ax = plt.subplots(figsize=(10, 6), facecolor=bg_color)
                        data = self.df[['close', 'bb_upper', 'bb_middle', 'bb_lower']].copy().dropna()
                        if not data.empty:
                            ax.plot(data.index, data['close'], color=plot_color, label='Цена')
                            ax.plot(data.index, data['bb_upper'], color=accent_color, linestyle='--', label='Верх')
                            ax.plot(data.index, data['bb_middle'], color='#4CAF50', linestyle='--', label='Средняя')
                            ax.plot(data.index, data['bb_lower'], color='#F44336', linestyle='--', label='Низ')
                            ax.fill_between(data.index, data['bb_lower'], data['bb_upper'], alpha=0.2, color=plot_color)
                            ax.set_title('Полосы Боллинджера', color=text_color, fontsize=16, pad=10)
                            ax.set_xlabel('Дата', color=text_color, fontsize=12)
                            ax.set_ylabel('Цена', color=text_color, fontsize=12)
                            ax.grid(True, linestyle='--', alpha=0.3, color=accent_color)
                            ax.legend(facecolor=bg_color, edgecolor=accent_color, labelcolor=text_color)
                            fig.patch.set_facecolor(bg_color)
                            bb_path = self.output_dir / f'bollinger_{self.currency}.png'
                            plt.savefig(bb_path, bbox_inches='tight', facecolor=bg_color, dpi=300)
                            plt.close(fig)
                            if bb_path.exists():
                                image_paths.append(bb_path)
                                logger.info(f"Полосы Боллинджера сохранены: {bb_path}")

                    elif chart == 'MACD' and self.mode == "crypto":
                        fig, ax1 = plt.subplots(figsize=(10, 6), facecolor=bg_color)
                        ax2 = ax1.twinx()
                        data = self.df[['close', 'macd', 'macd_signal', 'macd_hist']].copy().dropna()
                        if not data.empty:
                            ax1.plot(data.index, data['close'], color=plot_color, label='Цена')
                            ax2.plot(data.index, data['macd'], color=accent_color, label='MACD')
                            ax2.plot(data.index, data['macd_signal'], color='#4CAF50', linestyle='--', label='Сигнал')
                            ax2.bar(data.index, data['macd_hist'], color=plot_color, alpha=0.5, label='Гистограмма')
                            ax1.set_title('MACD', color=text_color, fontsize=16, pad=10)
                            ax1.set_xlabel('Дата', color=text_color, fontsize=12)
                            ax1.set_ylabel('Цена', color=text_color, fontsize=12)
                            ax2.set_ylabel('MACD', color=accent_color, fontsize=12)
                            ax1.grid(True, linestyle='--', alpha=0.3, color=accent_color)
                            ax1.legend(facecolor=bg_color, edgecolor=accent_color, labelcolor=text_color)
                            fig.patch.set_facecolor(bg_color)
                            macd_path = self.output_dir / f'macd_{self.currency}.png'
                            plt.savefig(macd_path, bbox_inches='tight', facecolor=bg_color, dpi=300)
                            plt.close(fig)
                            if macd_path.exists():
                                image_paths.append(macd_path)
                                logger.info(f"График MACD сохранен: {macd_path}")

                except Exception as e:
                    logger.error(f"Ошибка создания {chart}: {str(e)}")
                    continue

            return "Графики готовы и выглядят отлично!", image_paths
        except Exception as e:
            logger.error(f"Ошибка в visualize_data: {str(e)}")
            return f"Ошибка в визуализации: {str(e)}", []

    def save_to_csv(self) -> str:
        """Сохранение данных в CSV."""
        if self.df.empty:
            logger.error("Данные не загружены")
            return "Данные не загружены!"
        output_path = self.output_dir / f"{self.mode}_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        try:
            self.df.to_csv(output_path, encoding="utf-8")
            logger.info(f"CSV сохранён: {output_path}")
            return f"Данные сохранены в {output_path}"
        except Exception as e:
            logger.error(f"Ошибка сохранения CSV: {str(e)}")
            return f"Ошибка сохранения CSV: {str(e)}"

    def close(self):
        """Закрытие API-сессии."""
        if self.api:
            self.api.close()
            logger.info("API закрыт")

class DataAnalyzerApp:
    def __init__(self, root: ctk.CTk):
        """Инициализация графического интерфейса."""
        self.root = root
        self.root.title("💎 Криптоанализатор Про 💎")
        self.root.geometry("1600x900")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.current_currency = "BTC"
        self.mode = None
        self.crypto_analyzer = None
        self.current_theme = "dark"
        self.numeric_col = None
        self.numeric_col2 = None
        self.categorical_col = None
        self.chart_type = None
        self.image_labels = []
        self.welcome_label = None
        self.progress_bar = None
        self.currency_label = None
        self.currency_menu = None
        self.action_window = None

        self.root.configure(fg_color="#121212")
        self._create_welcome_widget()

        self.nav_panel = ctk.CTkFrame(self.root, height=80, fg_color="#1E1E1E", corner_radius=10)
        self.time_label = ctk.CTkLabel(self.nav_panel, text="", font=("Arial", 18, "bold"), text_color="#2196F3")
        self.time_label.pack(side=ctk.TOP, pady=10)

        self.button_frame = ctk.CTkFrame(self.nav_panel, fg_color="#1E1E1E", corner_radius=10)
        self.button_frame.pack(side=ctk.TOP, fill=ctk.X, pady=5)

        self.text_area = ctk.CTkTextbox(self.root, height=250, font=("Arial", 16), wrap="word", fg_color="#2A2A2A",
                                        text_color="#FFFFFF", border_color="#2196F3")
        self.button_frame_2 = ctk.CTkFrame(self.root, fg_color="#121212", corner_radius=10)

        self.numeric_label = ctk.CTkLabel(self.button_frame_2, text="🔢 Числовой 1:", font=("Arial", 16, "bold"),
                                         text_color="#2196F3")
        self.numeric_label.pack(side=ctk.LEFT, padx=15)
        self.numeric_menu = ctk.CTkOptionMenu(self.button_frame_2, values=["Выберите..."], command=self.set_numeric_col,
                                             width=180, fg_color="#2196F3", button_color="#1976D2",
                                             button_hover_color="#42A5F5", text_color="#FFFFFF", font=("Arial", 14))
        self.numeric_menu.pack(side=ctk.LEFT, padx=5)

        self.numeric_label2 = ctk.CTkLabel(self.button_frame_2, text="🔢 Числовой 2:", font=("Arial", 16, "bold"),
                                          text_color="#2196F3")
        self.numeric_label2.pack(side=ctk.LEFT, padx=15)
        self.numeric_menu2 = ctk.CTkOptionMenu(self.button_frame_2, values=["Выберите..."], command=self.set_numeric_col2,
                                              width=180, fg_color="#2196F3", button_color="#1976D2",
                                              button_hover_color="#42A5F5", text_color="#FFFFFF", font=("Arial", 14))
        self.numeric_menu2.pack(side=ctk.LEFT, padx=5)

        self.categorical_label = ctk.CTkLabel(self.button_frame_2, text="📋 Категория:", font=("Arial", 16, "bold"),
                                             text_color="#2196F3")
        self.categorical_label.pack(side=ctk.LEFT, padx=15)
        self.categorical_menu = ctk.CTkOptionMenu(self.button_frame_2, values=["Выберите..."],
                                                 command=self.set_categorical_col,
                                                 width=180, fg_color="#2196F3", button_color="#1976D2",
                                                 button_hover_color="#42A5F5", text_color="#FFFFFF", font=("Arial", 14))
        self.categorical_menu.pack(side=ctk.LEFT, padx=5)

        self.chart_type_label = ctk.CTkLabel(self.button_frame_2, text="📊 График:", font=("Arial", 16, "bold"),
                                            text_color="#2196F3")
        self.chart_type_label.pack(side=ctk.LEFT, padx=15)
        self.chart_type_menu = ctk.CTkOptionMenu(self.button_frame_2,
                                                values=["Выберите..."],
                                                command=self.set_chart_type, width=200,
                                                fg_color="#2196F3", button_color="#1976D2",
                                                button_hover_color="#42A5F5",
                                                text_color="#FFFFFF", font=("Arial", 14))
        self.chart_type_menu.pack(side=ctk.LEFT, padx=5)

        self.visualize_button = ctk.CTkButton(
            self.button_frame_2, text="📈 Визуализировать", command=self.open_visualization_window,
            width=200, height=40, fg_color="#2196F3", hover_color="#42A5F5",
            text_color="#FFFFFF", font=("Arial", 16, "bold")
        )
        self.visualize_button.pack(side=ctk.LEFT, padx=15)
        self.animate_button(self.visualize_button)

        self.image_frame = ctk.CTkScrollableFrame(self.root, fg_color="#121212", corner_radius=10)
        self.back_button = ctk.CTkButton(
            self.root, text="🏠 Вернуться на главный экран", command=self.return_to_main_screen,
            width=250, height=40, fg_color="#2196F3", hover_color="#42A5F5", text_color="#FFFFFF",
            font=("Arial", 16, "bold")
        )
        self.back_button.pack(side=ctk.BOTTOM, pady=10)
        self.back_button.pack_forget()
        logger.info("Интерфейс инициализирован успешно!")

    def _create_welcome_widget(self):
        """Создание приветственного виджета."""
        self.welcome_label = ctk.CTkLabel(
            self.root, text="💎 Добро пожаловать в Криптоанализатор Про! 💎\nВыберите режим анализа.",
            font=("Arial", 24, "bold"), text_color="#2196F3"
        )
        self.welcome_label.place(relx=0.5, rely=0.4, anchor=ctk.CENTER)

        self.crypto_button = ctk.CTkButton(
            self.root, text="📊 Анализ криптовалют", command=self.select_crypto_mode, width=200, height=40,
            fg_color="#2196F3", hover_color="#42A5F5", text_color="#FFFFFF", font=("Arial", 16, "bold")
        )
        self.crypto_button.place(relx=0.4, rely=0.55, anchor=ctk.CENTER)
        self.animate_button(self.crypto_button)

        self.big_data_button = ctk.CTkButton(
            self.root, text="📈 Большие данные", command=self.select_big_data_mode, width=200, height=40,
            fg_color="#2196F3", hover_color="#42A5F5", text_color="#FFFFFF", font=("Arial", 16, "bold")
        )
        self.big_data_button.place(relx=0.6, rely=0.55, anchor=ctk.CENTER)
        self.animate_button(self.big_data_button)

    def select_crypto_mode(self):
        """Выбор режима анализа криптовалют."""
        self.mode = "crypto"
        self.crypto_analyzer = CryptoAnalyzer(currency=self.current_currency, mode=self.mode)
        self.welcome_label.configure(text="💎 Анализ криптовалют 💎\nВыберите действие.")
        self.crypto_button.place_forget()
        self.big_data_button.place_forget()

        self.currency_label = ctk.CTkLabel(self.root, text="💰 Валюта:", font=("Arial", 18, "bold"), text_color="#2196F3")
        self.currency_label.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)
        self.currency_menu = ctk.CTkOptionMenu(
            self.root, values=["BTC", "ETH", "XRP", "LTC"], command=self.set_currency,
            width=150, fg_color="#2196F3", button_color="#1976D2", button_hover_color="#42A5F5",
            text_color="#FFFFFF", font=("Arial", 16)
        )
        self.currency_menu.place(relx=0.5, rely=0.55, anchor=ctk.CENTER)

        self.open_action_window()

    def select_big_data_mode(self):
        """Выбор режима анализа больших данных."""
        self.mode = "big_data"
        self.crypto_analyzer = CryptoAnalyzer(mode=self.mode)
        self.welcome_label.configure(text="💎 Большие данные 💎\nВыберите действие.")
        self.crypto_button.place_forget()
        self.big_data_button.place_forget()

        self.open_action_window()

    def set_currency(self, currency: str) -> None:
        """Установка валюты."""
        self.current_currency = currency
        if self.mode == "crypto":
            self.crypto_analyzer = CryptoAnalyzer(currency=self.current_currency, mode=self.mode)
            self.write_message(f"Выбрана валюта: {self.current_currency}")
            logger.info(f"Выбрана валюта: {self.current_currency}")

    def set_numeric_col(self, column: str) -> None:
        """Установка первого числового столбца."""
        self.numeric_col = column if column != "Выберите..." else None
        self.update_chart_options()
        logger.info(f"Числовой столбец 1: {self.numeric_col}")

    def set_numeric_col2(self, column: str) -> None:
        """Установка второго числового столбца."""
        self.numeric_col2 = column if column != "Выберите..." else None
        self.update_chart_options()
        logger.info(f"Числовой столбец 2: {self.numeric_col2}")

    def set_categorical_col(self, column: str) -> None:
        """Установка категориального столбца."""
        self.categorical_col = column if column != "Выберите..." else None
        self.update_chart_options()
        logger.info(f"Категориальный столбец: {self.categorical_col}")

    def set_chart_type(self, chart_type: str) -> None:
        """Установка типа графика."""
        self.chart_type = chart_type if chart_type != "Выберите..." else None
        logger.info(f"Тип графика: {self.chart_type}")

    def update_chart_options(self):
        """Обновление опций графиков."""
        if self.crypto_analyzer and not self.crypto_analyzer.df.empty:
            numeric_cols = list(self.crypto_analyzer.df.select_dtypes(include=[np.number]).columns)
            categorical_cols = list(self.crypto_analyzer.df.select_dtypes(include=['object', 'category']).columns)
            self.numeric_menu.configure(values=["Выберите..."] + numeric_cols)
            self.numeric_menu2.configure(values=["Выберите..."] + numeric_cols)
            self.categorical_menu.configure(values=["Выберите..."] + categorical_cols)

            available_charts = ["Выберите..."]
            if self.mode == "crypto" and all(col in self.crypto_analyzer.df.columns for col in ['open', 'high', 'low', 'close']) and len(self.crypto_analyzer.df) >= 50:
                available_charts.extend(['Японские свечи', 'Свечной график крипты'])
            if self.numeric_col:
                available_charts.extend(['Гистограмма', 'Ящик с усами', 'Линейный', 'Заполненный', 'Плотность'])
            if self.numeric_col and self.numeric_col2:
                available_charts.extend(['Точечный', 'Цена-Объем'])
            if len(numeric_cols) > 1:
                available_charts.append('Корреляция')
            if self.mode == "crypto" and 'bb_upper' in self.crypto_analyzer.df.columns and len(self.crypto_analyzer.df) >= 20:
                available_charts.append('Полосы Боллинджера')
            if self.mode == "crypto" and 'macd' in self.crypto_analyzer.df.columns and len(self.crypto_analyzer.df) >= 26:
                available_charts.append('MACD')
            self.chart_type_menu.configure(values=available_charts)
            if self.chart_type not in available_charts:
                self.chart_type = None
                self.chart_type_menu.set("Выберите...")

    def update_time(self):
        """Обновление времени в МСК."""
        msk = pytz.timezone('Europe/Moscow')
        current_time = datetime.now(msk)
        formatted_time = current_time.strftime("%H:%M:%S МСК, %d.%m.%Y")
        self.time_label.configure(text=f"⏰ {formatted_time}")
        self.root.after(1000, self.update_time)

    def animate_button(self, button: ctk.CTkButton) -> None:
        """Анимация кнопки."""
        def pulse():
            if not self.root.winfo_exists():
                return
            current_color = button.cget("fg_color")
            new_color = "#1976D2" if current_color == "#2196F3" else "#2196F3"
            button.configure(fg_color=new_color)
            self.root.after(800, pulse)
        threading.Thread(target=pulse, daemon=True).start()

    def show_progress(self):
        """Отображение прогресс-бара."""
        if not self.progress_bar:
            self.progress_bar = ctk.CTkProgressBar(self.root, width=400, mode='indeterminate')
            self.progress_bar.place(relx=0.5, rely=0.8, anchor=ctk.CENTER)
            self.progress_bar.start()
            self.root.update()

    def hide_progress(self):
        """Скрытие прогресс-бара."""
        if self.progress_bar:
            self.progress_bar.stop()
            self.progress_bar.destroy()
            self.progress_bar = None
            self.root.update()

    def toggle_theme(self):
        """Переключение темы."""
        self.current_theme = "white" if self.current_theme == "dark" else "dark"
        ctk.set_appearance_mode(self.current_theme)
        bg_color = "#F5F5F5" if self.current_theme == "white" else "#121212"
        text_color = "#212121" if self.current_theme == "white" else "#FFFFFF"
        button_color = "#2196F3" if self.current_theme == "white" else "#1976D2"
        hover_color = "#42A5F5" if self.current_theme == "white" else "#42A5F5"

        self.root.configure(fg_color=bg_color)
        self.text_area.configure(fg_color="#E0E0E0" if self.current_theme == "white" else "#2A2A2A", text_color=text_color)
        self.nav_panel.configure(fg_color="#E0E0E0" if self.current_theme == "white" else "#1E1E1E")
        self.button_frame.configure(fg_color="#E0E0E0" if self.current_theme == "white" else "#1E1E1E")
        self.button_frame_2.configure(fg_color=bg_color)
        self.image_frame.configure(fg_color=bg_color)

        for widget in [self.numeric_menu, self.numeric_menu2, self.categorical_menu, self.chart_type_menu]:
            widget.configure(fg_color=button_color, button_color=hover_color, button_hover_color=button_color,
                            text_color=text_color)
        for label in [self.time_label, self.numeric_label, self.numeric_label2, self.categorical_label,
                      self.chart_type_label]:
            label.configure(text_color="#2196F3" if self.current_theme == "white" else "#42A5F5")
        if self.welcome_label:
            self.welcome_label.configure(text_color="#2196F3" if self.current_theme == "white" else "#42A5F5")
        if self.currency_label:
            self.currency_label.configure(text_color="#2196F3" if self.current_theme == "white" else "#42A5F5")
        if self.visualize_button:
            self.visualize_button.configure(fg_color=button_color, hover_color=hover_color, text_color=text_color)

        # Обновление темы в окне действий, если оно открыто
        if self.action_window:
            self.action_window.configure(fg_color=bg_color)
            for widget in self.action_window.winfo_children():
                if isinstance(widget, ctk.CTkFrame):
                    widget.configure(fg_color=bg_color)
                elif isinstance(widget, ctk.CTkButton):
                    widget.configure(fg_color=button_color, hover_color=hover_color, text_color=text_color)

        logger.info(f"Тема переключена на: {self.current_theme}")
        self.write_message(f"Тема изменена на {'светлую' if self.current_theme == 'white' else 'темную'}!")
        self.update_chart_options()

    def write_message(self, message: str) -> None:
        """Отображение сообщения в текстовом поле."""
        self.text_area.delete(1.0, ctk.END)
        self.text_area.insert(ctk.END, message + "\n\n")
        self.text_area.see(ctk.END)
        logger.info(f"Сообщение отображено: {message[:50]}...")

    def clear_images(self) -> None:
        """Очистка изображений."""
        for label in self.image_labels:
            label.destroy()
        self.image_labels = []
        logger.info("Визуализации очищены")

    def load_data(self) -> None:
        """Загрузка данных из CSV."""
        file_path = filedialog.askopenfilename(filetypes=[("CSV файлы", "*.csv")])
        if file_path:
            self.crypto_analyzer.file_path = Path(file_path)
            self.show_progress()
            def run_async():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(self.crypto_analyzer.load_data_async(chunk_size=10000))
                loop.close()
                self.root.after(0, lambda: self._post_load_data(result))
            if self.welcome_label:
                self.welcome_label.configure(text="🔄 Загрузка данных...")
            threading.Thread(target=run_async, daemon=True).start()
        else:
            self.write_message("Загрузка данных отменена!")

    def fetch_realtime_data(self) -> None:
        """Получение данных в реальном времени."""
        self.show_progress()
        if self.welcome_label:
            self.welcome_label.configure(text=f"🔄 Получение данных для {self.mode}...")
        self.root.update()
        result = self.crypto_analyzer.fetch_realtime_data()
        self._post_load_data(result)

    def _post_load_data(self, result: str) -> None:
        """Обработка после загрузки данных."""
        self.hide_progress()
        if self.welcome_label:
            self.welcome_label.destroy()
            self.welcome_label = None
        if self.currency_label:
            self.currency_label.place_forget()
        if self.currency_menu:
            self.currency_menu.place_forget()

        self.nav_panel.pack(side=ctk.TOP, fill=ctk.X, padx=10, pady=10)
        self.update_time()
        self.text_area.pack(side=ctk.TOP, fill=ctk.X, padx=10, pady=10)
        self.button_frame_2.pack(side=ctk.TOP, fill=ctk.X, padx=10, pady=10)
        self.image_frame.pack(side=ctk.TOP, fill=ctk.BOTH, expand=True, padx=10, pady=10)
        self.back_button.pack(side=ctk.BOTTOM, pady=10)

        if self.crypto_analyzer and not self.crypto_analyzer.df.empty:
            self.update_chart_options()
            logger.info("Данные загружены успешно!")

        self.write_message(result)
        self.clear_images()

    def return_to_main_screen(self) -> None:
        """Возврат на главный экран."""
        self.nav_panel.pack_forget()
        self.text_area.pack_forget()
        self.button_frame_2.pack_forget()
        self.image_frame.pack_forget()
        self.back_button.pack_forget()
        self.clear_images()

        if self.action_window:
            self.action_window.destroy()
            self.action_window = None

        self._create_welcome_widget()
        if self.crypto_analyzer:
            self.crypto_analyzer.close()
        self.crypto_analyzer = None
        self.mode = None
        self.numeric_col = None
        self.numeric_col2 = None
        self.categorical_col = None
        self.chart_type = None
        self.update_chart_options()
        self.write_message("Вы вернулись на главный экран!")
        logger.info("Возврат на главный экран выполнен")

    def preview_data(self, num_rows: int = 10) -> None:
        """Предпросмотр данных."""
        if not self.crypto_analyzer or self.crypto_analyzer.df.empty:
            self.write_message("Данные не загружены!")
            return
        try:
            num_rows = int(self.rows_entry.get() or num_rows)
            if num_rows > 100:
                self.write_message("Максимум 100 строк!")
                return
            preview = self.crypto_analyzer.df.head(num_rows).to_string()
            self.write_message(f"Первые {num_rows} строк:\n{preview}")
        except ValueError:
            self.write_message("Введите корректное количество строк!")

    def show_analysis(self) -> None:
        """Отображение результатов анализа в основном окне."""
        if not self.crypto_analyzer:
            self.write_message("Анализатор не инициализирован!")
            return
        self.show_progress()
        result = self.crypto_analyzer.basic_analysis()
        self.hide_progress()
        self.write_message(result)

    def open_visualization_window(self) -> None:
        """Открытие окна с визуализацией."""
        if not self.crypto_analyzer:
            self.write_message("Анализатор не инициализирован!")
            return
        self.show_progress()
        self.clear_images()
        result, image_paths = self.crypto_analyzer.visualize_data(
            numeric_col=self.numeric_col, numeric_col2=self.numeric_col2,
            categorical_col=self.categorical_col, theme=self.current_theme, chart_type=self.chart_type
        )
        self.hide_progress()

        vis_window = ctk.CTkToplevel(self.root)
        vis_window.title("📈 Визуализация")
        vis_window.geometry("1200x800")
        vis_window.configure(fg_color="#F5F5F5" if self.current_theme == "white" else "#121212")

        vis_frame = ctk.CTkScrollableFrame(
            vis_window, fg_color="#F5F5F5" if self.current_theme == "white" else "#121212", corner_radius=10
        )
        vis_frame.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)

        message_label = ctk.CTkLabel(
            vis_frame, text=result, font=("Arial", 16, "bold"),
            text_color="#212121" if self.current_theme == "white" else "#FFFFFF"
        )
        message_label.pack(pady=10)

        image_labels = []
        for image_path in image_paths:
            try:
                image = Image.open(image_path)
                image = image.resize((int(image.width * 0.5), int(image.height * 0.5)), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                label = ctk.CTkLabel(vis_frame, image=photo, text="")
                label.image = photo
                label.pack(pady=15, padx=15)
                image_labels.append(label)
            except Exception as e:
                logger.error(f"Ошибка отображения {image_path}: {str(e)}")
                message_label.configure(text=f"{result}\nОшибка отображения {image_path}: {str(e)}")
        logger.info("Окно визуализации открыто")

    def clean_data(self) -> None:
        """Очистка данных."""
        if not self.crypto_analyzer:
            self.write_message("Анализатор не инициализирован!")
            return
        self.show_progress()
        result = self.crypto_analyzer.clean_data()
        self.hide_progress()
        self.write_message(result)

    def export_to_pdf(self) -> None:
        """Экспорт в PDF."""
        if not self.crypto_analyzer or self.crypto_analyzer.df.empty:
            self.write_message("Данные не загружены!")
            return
        self.show_progress()
        pdf_path = self.crypto_analyzer.output_dir / f'отчет_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        try:
            with matplotlib.backends.backend_pdf.PdfPages(pdf_path) as pdf:
                fig, ax = plt.subplots(figsize=(10, 8))
                ax.axis('off')
                analysis_text = self.crypto_analyzer.basic_analysis()
                ax.text(0.05, 0.95, analysis_text[:2000], fontsize=10, verticalalignment='top', wrap=True)
                pdf.savefig(fig, bbox_inches='tight')
                plt.close(fig)
                _, image_paths = self.crypto_analyzer.visualize_data(
                    numeric_col=self.numeric_col, numeric_col2=self.numeric_col2,
                    categorical_col=self.categorical_col, theme=self.current_theme, chart_type=self.chart_type
                )
                for image_path in image_paths:
                    if image_path.suffix != '.json':
                        fig, ax = plt.subplots(figsize=(10, 8))
                        image = Image.open(image_path)
                        ax.imshow(image)
                        ax.axis('off')
                        pdf.savefig(fig, bbox_inches='tight')
                        plt.close(fig)
            self.hide_progress()
            self.write_message(f"Отчет сохранен: {pdf_path}")
            webbrowser.open(str(pdf_path))
        except Exception as e:
            logger.error(f"Ошибка экспорта в PDF: {str(e)}")
            self.hide_progress()
            self.write_message(f"Ошибка экспорта в PDF: {str(e)}")

    def save_to_csv(self) -> None:
        """Сохранение в CSV."""
        if not self.crypto_analyzer:
            self.write_message("Анализатор не инициализирован!")
            return
        self.show_progress()
        result = self.crypto_analyzer.save_to_csv()
        self.hide_progress()
        self.write_message(result)

    def open_action_window(self):
        """Открытие окна с кнопками действий."""
        if self.action_window:
            self.action_window.destroy()
        self.action_window = ctk.CTkToplevel(self.root)
        self.action_window.title("📋 Действия")
        self.action_window.geometry("300x600")
        self.action_window.configure(fg_color="#F5F5F5" if self.current_theme == "white" else "#121212")

        action_frame = ctk.CTkFrame(self.action_window, fg_color="#F5F5F5" if self.current_theme == "white" else "#121212",
                                    corner_radius=10)
        action_frame.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)

        actions = [
            ("📂 Загрузить CSV", self.load_data),
            ("🌐 Получить данные", self.fetch_realtime_data),
            ("🔍 Просмотр", self.preview_data),
            ("📊 Анализ", self.show_analysis),
            ("🧹 Очистить данные", self.clean_data),
            ("📈 Визуализация", self.open_visualization_window),
            ("📄 Экспорт в PDF", self.export_to_pdf),
            ("💾 Сохранить в CSV", self.save_to_csv),
            ("🌙 Смена темы", self.toggle_theme),
        ]

        for i, (label, command) in enumerate(actions):
            button = ctk.CTkButton(
                action_frame, text=label, command=command,
                width=250, height=40, fg_color="#2196F3", hover_color="#42A5F5",
                text_color="#FFFFFF", font=("Arial", 16, "bold")
            )
            button.pack(pady=5)
            self.animate_button(button)

        logger.info("Окно действий открыто")

def generate_sample_csv(file_path: str, currency: str, num_rows: int = 100):
    """Генерация тестового CSV-файла."""
    np.random.seed(42)
    start_date = datetime(2025, 6, 1)
    timestamps = [start_date + timedelta(hours=i) for i in range(num_rows)]
    base_price = {
        'BTC': 60000,
        'ETH': 3500,
        'XRP': 0.6,
        'LTC': 80
    }.get(currency, 100)
    close_prices = base_price + np.random.normal(0, base_price * 0.02, num_rows).cumsum()
    open_prices = close_prices + np.random.normal(0, base_price * 0.001, num_rows)
    high_prices = np.maximum(open_prices, close_prices) + np.random.uniform(base_price * 0.0002,
                                                                            base_price * 0.002, num_rows)
    low_prices = np.minimum(open_prices, close_prices) - np.random.uniform(base_price * 0.0002,
                                                                           base_price * 0.002, num_rows)
    volumes = np.random.uniform(100, 1000, num_rows)
    data = pd.DataFrame({
        'timestamp': timestamps,
        'open': open_prices,
        'high': high_prices,
        'low': low_prices,
        'close': close_prices,
        'volume': volumes,
        'symbol': currency
    })
    data.to_csv(file_path, index=False, encoding='utf-8')
    logger.info(f"Пример CSV для {currency} создан: {file_path}")

def main():
    """Основная функция запуска приложения."""
    script_dir = Path(__file__).parent
    currencies = ["BTC", "ETH", "XRP", "LTC"]
    for currency in currencies:
        sample_csv = script_dir / f"{currency}_data.csv"
        if not sample_csv.exists():
            generate_sample_csv(str(sample_csv), currency, 120)
    root = ctk.CTk()
    app = DataAnalyzerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()