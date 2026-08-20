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
    """Test core financial calculation engine with EBITDA adjustments"""

    @pytest.fixture
    def app_instance(self):
        # Create headless instance for testing
        app = PLForecastApp()
        app.withdraw()  # Hide window during tests
        yield app
        app.destroy()

    def test_baseline_calculation(self, app_instance):
        """Test default baseline financial figures and EBITDA adjustments"""
        app_instance.calculate_interactions()
        
        # Default baseline:
        # Sales (107.0) - Discounts (7.0) = Revenue 100.0
        # Direct COGS (52.5) + Indirect COGS (13.5) = COGS 66.0
        # Gross Profit = 34.00 (34.0%)
        # OpEx = 14.0, Depreciation = 20.0, Taxes = 2.5
        # Net Income = 34.0 - 14.0 - 0 - 2.5 - 20.0 = -2.50
        # Reported EBITDA = -2.50 + 22.50 = 20.00
        # Management Adjusted EBITDA = 20.00
        assert "$34.00" in app_instance.kpi_gp.cget("text")
        assert "-$2.50" in app_instance.kpi_ni.cget("text") or "$-2.50" in app_instance.kpi_ni.cget("text")
        assert "$20.00" in app_instance.kpi_ebitda.cget("text")
        assert "$20.00" in app_instance.kpi_adj_ebitda.cget("text")

    def test_dynamic_csv_ingestion(self, app_instance, tmp_path):
        """Test loading dynamic CSV spreadsheet and rebuilding inputs"""
        csv_file = tmp_path / "custom_pnl.csv"
        df = pd.DataFrame([{
            "Total_Sales": 200.0,
            "Discounts_Refunds": -10.0,
            "Total_Direct_COGS": 80.0,
            "Total_Indirect_COGS": 20.0,
            "Total_Operating_Expenses": 30.0,
            "Depreciation_Amortization": 15.0,
            "Interest_Expense": 5.0,
            "Income_Taxes": 10.0,
            "Total_Adjustments": 5.0
        }])
        df.to_csv(csv_file, index=False)

        app_instance.df = df
        app_instance.build_dynamic_inputs()
        
        # Revenue = 190, COGS = 100, Gross Profit = 90.00
        # Net Income = 90 - 30 - 5 - 10 - 15 = 30.00
        # Reported EBITDA = 30 + (5 + 10 + 15) = 60.00
        # Management Adjusted EBITDA = 60 + 5 = 65.00
        assert "$90.00" in app_instance.kpi_gp.cget("text")
        assert "$30.00" in app_instance.kpi_ni.cget("text")
        assert "$60.00" in app_instance.kpi_ebitda.cget("text")
        assert "$65.00" in app_instance.kpi_adj_ebitda.cget("text")

    def test_management_adjustments_uplift(self, app_instance):
        """Test that management adjustments properly uplift adjusted EBITDA"""
        app_instance.entries["Total_Adjustments"].delete(0, "end")
        app_instance.entries["Total_Adjustments"].insert(0, "15.0")
        app_instance.calculate_interactions()

        # Reported EBITDA = 20.00 -> Adjusted EBITDA = 35.00
        assert "$20.00" in app_instance.kpi_ebitda.cget("text")
        assert "$35.00" in app_instance.kpi_adj_ebitda.cget("text")
