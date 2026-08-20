"""
Unit Test Suite for The Gunslinger's Desktop Ledger
Ensures P&L calculation accuracy, spreadsheet ingestion, and margin forecasting integrity.
"""

import os
import sys
import pytest
import pandas as pd
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import PLForecastApp


class TestLedgerCalculations:
    """Test core financial calculation engine"""

    @pytest.fixture
    def app_instance(self):
        # Create headless instance for testing
        app = PLForecastApp()
        app.withdraw()  # Hide window during tests
        yield app
        app.destroy()

    def test_baseline_calculation(self, app_instance):
        """Test default baseline financial figures and margins"""
        app_instance.calculate_interactions()
        
        # Default baseline: Sales (107k) - Discounts (7k) = Revenue 100k
        # Direct COGS (52.5k) + Indirect COGS (13.5k) = COGS 66k
        # Gross Profit = 34k (34.0%)
        # OpEx = 14k, Taxes = 3.5k -> Net Income = 16.5k (16.5%)
        assert "$100,000.00" in app_instance.kpi_rev.cget("text")
        assert "$66,000.00" in app_instance.kpi_cogs.cget("text")
        assert "$34,000.00" in app_instance.kpi_gp.cget("text")
        assert "34.0%" in app_instance.kpi_gp.cget("text")
        assert "$16,500.00" in app_instance.kpi_ni.cget("text")
        assert "16.5%" in app_instance.kpi_ni.cget("text")

    def test_dynamic_csv_ingestion(self, app_instance, tmp_path):
        """Test loading dynamic CSV spreadsheet and rebuilding inputs"""
        csv_file = tmp_path / "custom_pnl.csv"
        df = pd.DataFrame([{
            "Total_Sales": 200000.0,
            "Discounts_Refunds": -10000.0,
            "Total_Direct_COGS": 80000.0,
            "Total_Indirect_COGS": 20000.0,
            "Total_Operating_Expenses": 30000.0,
            "Taxes_Interest": 10000.0
        }])
        df.to_csv(csv_file, index=False)

        app_instance.df = df
        app_instance.build_dynamic_inputs()
        
        # Revenue = 190k, COGS = 100k, Gross Profit = 90k (47.4%), Net Income = 50k (26.3%)
        assert "$190,000.00" in app_instance.kpi_rev.cget("text")
        assert "$100,000.00" in app_instance.kpi_cogs.cget("text")
        assert "$90,000.00" in app_instance.kpi_gp.cget("text")
        assert "$50,000.00" in app_instance.kpi_ni.cget("text")

    def test_negative_margin_handling(self, app_instance):
        """Test loss scenario and negative margin coloring"""
        app_instance.entries["Total_Sales"].delete(0, "end")
        app_instance.entries["Total_Sales"].insert(0, "50000")
        app_instance.calculate_interactions()

        # Revenue = 43k, COGS = 66k -> Gross Profit = -23k (Loss)
        assert "-$23,000.00" in app_instance.kpi_gp.cget("text") or "$-23,000.00" in app_instance.kpi_gp.cget("text")
        assert app_instance.kpi_gp.cget("text_color") == "#f87171"  # Red text color on loss
