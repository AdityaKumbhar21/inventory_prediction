"""
Feature engineering service for prediction
"""
import pandas as pd
import numpy as np
from datetime import timedelta
from typing import Tuple


class FeatureEngineer:
    """Handles feature engineering for predictions"""
    
    @staticmethod
    def create_time_features(df: pd.DataFrame) -> pd.DataFrame:
        """Create time-based features"""
        df = df.copy()
        
        # Extract date components
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['day'] = df['date'].dt.day
        df['day_of_week'] = df['date'].dt.dayofweek
        df['day_of_year'] = df['date'].dt.dayofyear
        df['week_of_year'] = df['date'].dt.isocalendar().week
        df['quarter'] = df['date'].dt.quarter
        
        # Cyclical encoding
        df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
        df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
        df['day_of_week_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
        df['day_of_week_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
        df['day_of_year_sin'] = np.sin(2 * np.pi * df['day_of_year'] / 365)
        df['day_of_year_cos'] = np.cos(2 * np.pi * df['day_of_year'] / 365)
        
        # Boolean features
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        df['is_month_start'] = df['date'].dt.is_month_start.astype(int)
        df['is_month_end'] = df['date'].dt.is_month_end.astype(int)
        
        return df
    
    @staticmethod
    def create_lag_features(
        pred_row: pd.DataFrame,
        historical_data: pd.DataFrame,
        pred_date: pd.Timestamp,
        lag_periods: list
    ) -> pd.DataFrame:
        """Create lag features from historical data"""
        pred_row = pred_row.copy()
        
        for lag in lag_periods:
            lag_date = pred_date - timedelta(days=lag)
            lag_value = historical_data[
                historical_data['date'] <= lag_date
            ]['sales'].tail(1)
            
            if len(lag_value) > 0:
                pred_row[f'sales_lag_{lag}'] = lag_value.values[0]
            else:
                pred_row[f'sales_lag_{lag}'] = historical_data['sales'].mean()
        
        return pred_row
    
    @staticmethod
    def create_rolling_features(
        pred_row: pd.DataFrame,
        historical_data: pd.DataFrame,
        pred_date: pd.Timestamp,
        rolling_windows: list
    ) -> pd.DataFrame:
        """Create rolling window features"""
        pred_row = pred_row.copy()
        
        for window in rolling_windows:
            window_data = historical_data[
                historical_data['date'] < pred_date
            ].tail(window)['sales']
            
            if len(window_data) > 0:
                pred_row[f'sales_rolling_mean_{window}'] = window_data.mean()
                pred_row[f'sales_rolling_std_{window}'] = window_data.std()
                pred_row[f'sales_rolling_min_{window}'] = window_data.min()
                pred_row[f'sales_rolling_max_{window}'] = window_data.max()
            else:
                pred_row[f'sales_rolling_mean_{window}'] = historical_data['sales'].mean()
                pred_row[f'sales_rolling_std_{window}'] = historical_data['sales'].std()
                pred_row[f'sales_rolling_min_{window}'] = historical_data['sales'].min()
                pred_row[f'sales_rolling_max_{window}'] = historical_data['sales'].max()
        
        return pred_row
    
    @staticmethod
    def create_aggregate_features(
        pred_row: pd.DataFrame,
        store: int,
        item: int,
        store_item_data: pd.DataFrame,
        all_data: pd.DataFrame
    ) -> pd.DataFrame:
        """Create store and item aggregate features"""
        pred_row = pred_row.copy()
        
        # Store-level statistics
        store_data = all_data[all_data['store'] == store]['sales']
        pred_row['store_avg_sales'] = store_data.mean()
        pred_row['store_std_sales'] = store_data.std()
        pred_row['store_median_sales'] = store_data.median()
        
        # Item-level statistics
        item_data = all_data[all_data['item'] == item]['sales']
        pred_row['item_avg_sales'] = item_data.mean()
        pred_row['item_std_sales'] = item_data.std()
        pred_row['item_median_sales'] = item_data.median()
        
        # Store-Item combination statistics
        pred_row['store_item_avg_sales'] = store_item_data['sales'].mean()
        pred_row['store_item_std_sales'] = store_item_data['sales'].std()
        
        return pred_row
    
    @classmethod
    def prepare_features(
        cls,
        store: int,
        item: int,
        date: str,
        all_data: pd.DataFrame,
        lag_periods: list,
        rolling_windows: list
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Prepare all features for prediction
        
        Returns:
            Tuple of (features_df, store_item_historical_data)
        """
        pred_date = pd.to_datetime(date)
        
        # Get historical data for this store-item
        store_item_data = all_data[
            (all_data['store'] == store) & 
            (all_data['item'] == item)
        ].copy()
        
        if len(store_item_data) == 0:
            raise ValueError(f"No historical data for store {store}, item {item}")
        
        # Initialize prediction row
        pred_row = pd.DataFrame({
            'date': [pred_date],
            'store': [store],
            'item': [item],
            'sales': [0]
        })
        
        # Add all features
        pred_row = cls.create_time_features(pred_row)
        pred_row = cls.create_lag_features(pred_row, store_item_data, pred_date, lag_periods)
        pred_row = cls.create_rolling_features(pred_row, store_item_data, pred_date, rolling_windows)
        pred_row = cls.create_aggregate_features(pred_row, store, item, store_item_data, all_data)
        
        # Get feature columns (exclude non-feature columns and include 'item')
        exclude_cols = ['date', 'sales', 'store']
        feature_cols = [col for col in pred_row.columns if col not in exclude_cols]
        
        return pred_row[feature_cols], store_item_data


# Global feature engineer instance
feature_engineer = FeatureEngineer()
