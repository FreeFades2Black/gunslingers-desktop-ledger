"""
=============================================================================
* The Gunslinger's Desktop Ledger: Standalone P&L UI & Forecasting Engine
* Lead Architect & Developer: Free Hall
* Built for: Chuck's P&L Interaction & Forecasting Analysis
=============================================================================
"""

import os
import sys
import json
import pandas as pd
import customtkinter as ctk
from tkinter import filedialog, messagebox
from typing import Dict, Any

# Set visual theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class PLForecastApp(ctk.CTk):
    """Standalone CustomTkinter Real-Time P&L Forecasting & Interaction Engine"""

    def __init__(self):
        super().__init__()

        self.title("The Gunslinger's Desktop Ledger — P&L Forecasting Engine")
        self.geometry("980x820")
        self.minsize(880, 700)

        self.df = None
        self.entries = {}
        self.sliders = {}

        # Default Baseline Model from Financial Schema
        self.default_data = {
            "Total_Sales": 107.0,
            "Discounts_Refunds": -7.0,
            "Total_Direct_COGS": 52.5,
            "Total_Indirect_COGS": 13.5,
            "Total_Operating_Expenses": 14.0,
            "Gain_Loss_on_Sales_of_Assets": 0.0,
            "Depreciation_Amortization": 20.0,
            "Interest_Expense": 0.0,
            "Other_Income_Expenses": 0.0,
            "Other_Non_Operating_Expenses": 0.0,
            "Income_Taxes": 2.5,
            "Total_Adjustments": 0.0
        }

        self.create_widgets()
        self.load_default_baseline()

    def create_widgets(self):
        # ---------------------------------------------------------------------
        # TOP HEADER & FILE TOOLBAR
        # ---------------------------------------------------------------------
        header_frame = ctk.CTkFrame(self, corner_radius=10, fg_color=("#1e293b", "#0f172a"))
        header_frame.pack(fill="x", padx=16, pady=(12, 6))

        title_lbl = ctk.CTkLabel(
            header_frame,
            text="🤠 The Gunslinger's Desktop Ledger",
            font=ctk.CTkFont(family="Arial", size=20, weight="bold"),
            text_color="#38bdf8"
        )
        title_lbl.pack(anchor="w", padx=16, pady=(10, 2))

        subtitle_lbl = ctk.CTkLabel(
            header_frame,
            text="Interactive Factor Sensitivity, EBITDA Adjustments & Real-Time P&L Forecasting Engine",
            font=ctk.CTkFont(family="Arial", size=12),
            text_color="#94a3b8"
        )
        subtitle_lbl.pack(anchor="w", padx=16, pady=(0, 10))

        # Toolbar Frame
        toolbar_frame = ctk.CTkFrame(self, fg_color="transparent")
        toolbar_frame.pack(fill="x", padx=16, pady=4)

        self.btn_load = ctk.CTkButton(
            toolbar_frame,
            text="📂 Load Spreadsheet (.xlsx / .csv)",
            command=self.load_file,
            width=220,
            fg_color="#2563eb",
            hover_color="#1d4ed8"
        )
        self.btn_load.pack(side="left", padx=(0, 8))

        self.btn_export = ctk.CTkButton(
            toolbar_frame,
            text="💾 Save Scenario (.xlsx / .csv)",
            command=self.export_scenario,
            width=200,
            fg_color="#059669",
            hover_color="#047857"
        )
        self.btn_export.pack(side="left", padx=8)

        self.btn_reset = ctk.CTkButton(
            toolbar_frame,
            text="🔄 Reset Baseline",
            command=self.load_default_baseline,
            width=140,
            fg_color="#475569",
            hover_color="#334155"
        )
        self.btn_reset.pack(side="left", padx=8)

        self.lbl_file = ctk.CTkLabel(
            toolbar_frame,
            text="Status: Active Baseline Loaded",
            font=ctk.CTkFont(family="Arial", size=12, slant="italic"),
            text_color="#38bdf8"
        )
        self.lbl_file.pack(side="left", padx=12)

        # ---------------------------------------------------------------------
        # KPI SUMMARY BANNER (TOP DASHBOARD)
        # ---------------------------------------------------------------------
        self.kpi_frame = ctk.CTkFrame(self, corner_radius=10, fg_color=("#1e3a8a", "#172554"))
        self.kpi_frame.pack(fill="x", padx=16, pady=8)

        # Grid of 4 Key Metrics
        self.kpi_gp = self._create_kpi_box(self.kpi_frame, "GROSS PROFIT", "$34.00", "#38bdf8", 0)
        self.kpi_ni = self._create_kpi_box(self.kpi_frame, "NET INCOME", "$0.00", "#f87171", 1)
        self.kpi_ebitda = self._create_kpi_box(self.kpi_frame, "REPORTED EBITDA", "$20.00", "#fbbf24", 2)
        self.kpi_adj_ebitda = self._create_kpi_box(self.kpi_frame, "MANAGEMENT ADJ. EBITDA", "$20.00", "#4ade80", 3)

        # ---------------------------------------------------------------------
        # OUTPUT SUMMARY BANNER
        # ---------------------------------------------------------------------
        self.output_frame = ctk.CTkFrame(self, corner_radius=10, fg_color=("#0f172a", "#1e293b"))
        self.output_frame.pack(fill="x", padx=16, pady=(4, 8))

        self.lbl_results = ctk.CTkLabel(
            self.output_frame,
            text="Load a spreadsheet or edit factors to calculate real-time interactions.",
            font=ctk.CTkFont(family="Consolas", size=13, weight="bold"),
            text_color="#e2e8f0",
            justify="center"
        )
        self.lbl_results.pack(padx=12, pady=10)

        # ---------------------------------------------------------------------
        # MAIN SCROLLABLE INPUT GRID
        # ---------------------------------------------------------------------
        self.main_frame = ctk.CTkScrollableFrame(
            self,
            width=940,
            height=360,
            corner_radius=10,
            fg_color=("#0f172a", "#090d16")
        )
        self.main_frame.pack(padx=16, pady=4, fill="both", expand=True)

        # Bottom Quick Status
        self.status_bar = ctk.CTkLabel(
            self,
            text="⚡ Real-time interactive calculation active. Edit any factor above to forecast immediate margin impact.",
            font=ctk.CTkFont(family="Arial", size=11),
            text_color="#64748b"
        )
        self.status_bar.pack(side="bottom", pady=6)

    def _create_kpi_box(self, parent, title: str, default_val: str, val_color: str, col_idx: int):
        box = ctk.CTkFrame(parent, fg_color=("#1e293b", "#0f172a"), corner_radius=8)
        box.grid(row=0, column=col_idx, padx=8, pady=10, sticky="nsew")
        parent.grid_columnconfigure(col_idx, weight=1)

        lbl_t = ctk.CTkLabel(
            box,
            text=title,
            font=ctk.CTkFont(family="Arial", size=10, weight="bold"),
            text_color="#94a3b8"
        )
        lbl_t.pack(pady=(6, 0))

        lbl_v = ctk.CTkLabel(
            box,
            text=default_val,
            font=ctk.CTkFont(family="Arial", size=16, weight="bold"),
            text_color=val_color
        )
        lbl_v.pack(pady=(0, 6))
        return lbl_v

    def load_default_baseline(self):
        """Populate inputs with default baseline financial data"""
        self.df = pd.DataFrame([self.default_data])
        self.lbl_file.configure(text="Using: Standard Baseline Model")
        self.build_dynamic_inputs()

    def load_file(self):
        """Load user spreadsheet (.xlsx, .xls, .csv)"""
        file_path = filedialog.askopenfilename(
            title="Open Financial Spreadsheet",
            filetypes=[("Excel Files", "*.xlsx;*.xls"), ("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if not file_path:
            return

        try:
            if file_path.lower().endswith(('.xlsx', '.xls')):
                self.df = pd.read_excel(file_path)
            else:
                self.df = pd.read_csv(file_path)

            file_name = os.path.basename(file_path)
            self.lbl_file.configure(text=f"Loaded: {file_name}")
            self.build_dynamic_inputs()
            messagebox.showinfo("Success", f"Successfully loaded '{file_name}' ({len(self.df.columns)} financial columns detected).")
        except Exception as e:
            messagebox.showerror("Error Loading File", f"Could not parse spreadsheet:\n{e}")

    def build_dynamic_inputs(self):
        """Construct interactive input entries and labels from dataset columns"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        if self.df is None or self.df.empty:
            return

        row = self.df.iloc[0]
        self.entries = {}

        # Section Header
        hdr_lbl = ctk.CTkLabel(
            self.main_frame,
            text="📊 Financial Factors & Variable Inputs",
            font=ctk.CTkFont(family="Arial", size=14, weight="bold"),
            text_color="#38bdf8"
        )
        hdr_lbl.grid(row=0, column=0, columnspan=3, sticky="w", padx=12, pady=(8, 12))

        row_idx = 1
        for col in self.df.columns:
            # Column Display Label
            clean_col = str(col).replace("_", " ").title()
            lbl = ctk.CTkLabel(
                self.main_frame,
                text=f"{clean_col}:",
                font=ctk.CTkFont(family="Arial", size=12, weight="bold"),
                anchor="w",
                width=260
            )
            lbl.grid(row=row_idx, column=0, sticky="w", padx=12, pady=6)

            # Editable Input Field
            entry = ctk.CTkEntry(
                self.main_frame,
                width=220,
                font=ctk.CTkFont(family="Consolas", size=12)
            )
            val = row[col]
            try:
                formatted_val = f"{float(val):.2f}"
            except (ValueError, TypeError):
                formatted_val = str(val)

            entry.insert(0, formatted_val)
            entry.grid(row=row_idx, column=1, padx=12, pady=6, sticky="w")

            # Real-time recalculation listener
            entry.bind("<KeyRelease>", lambda event: self.calculate_interactions())

            self.entries[col] = entry
            row_idx += 1

        self.calculate_interactions()

    def calculate_interactions(self, event=None):
        """Real-time factor recalculation with EBITDA adjustments"""
        try:
            # Extract active values from inputs
            data = {}
            for col, entry in self.entries.items():
                raw_text = entry.get().strip().replace("$", "").replace(",", "")
                try:
                    data[col] = float(raw_text) if raw_text else 0.0
                except ValueError:
                    data[col] = 0.0
            
            # 1. Revenue
            total_sales = data.get('Total_Sales', 107.0)
            discounts = data.get('Discounts_Refunds', -7.0)
            total_revenue = total_sales + discounts

            # 2. COGS
            total_direct_cogs = data.get('Total_Direct_COGS', 52.5)
            total_indirect_cogs = data.get('Total_Indirect_COGS', 13.5)
            total_cogs = total_direct_cogs + total_indirect_cogs

            # 3. Gross Profit
            gross_profit = total_revenue - total_cogs
            gp_margin = (gross_profit / total_revenue * 100.0) if total_revenue > 0 else 0.0

            # 4. Operating Expenses
            total_opex = data.get('Total_Operating_Expenses', 14.0)

            # 5. EBITDA Adjustments & Bottom Line Items
            gain_loss_assets = data.get('Gain_Loss_on_Sales_of_Assets', 0.0)
            depreciation = data.get('Depreciation_Amortization', 20.0)
            interest_expense = data.get('Interest_Expense', 0.0)
            other_income_exp = data.get('Other_Income_Expenses', 0.0)
            other_non_op = data.get('Other_Non_Operating_Expenses', 0.0)
            income_taxes = data.get('Income_Taxes', 2.5)

            # Net Income = Gross Profit - OpEx - Interest - Taxes - Depreciation (+/- others)
            net_income = gross_profit - total_opex - interest_expense - income_taxes - depreciation + gain_loss_assets + other_income_exp + other_non_op
            net_margin = (net_income / total_revenue * 100.0) if total_revenue > 0 else 0.0

            # Total EBITDA Adjustments = Interest + Taxes + Depreciation & Amortization (plus other non-operating addbacks)
            total_ebitda_adjustments = interest_expense + income_taxes + depreciation + (-gain_loss_assets) - other_income_exp - other_non_op
            
            # Reported EBITDA = Net Income + Total EBITDA Adjustments
            reported_ebitda = net_income + total_ebitda_adjustments

            # Management Adjusted EBITDA
            total_adjustments = data.get('Total_Adjustments', 0.0)
            management_adjusted_ebitda = reported_ebitda + total_adjustments

            # Update KPI stat boxes
            gp_color = "#4ade80" if gross_profit >= 0 else "#f87171"
            self.kpi_gp.configure(
                text=f"${gross_profit:,.2f} ({gp_margin:.1f}%)",
                text_color=gp_color
            )

            ni_color = "#4ade80" if net_income >= 0 else "#f87171"
            self.kpi_ni.configure(
                text=f"${net_income:,.2f} ({net_margin:.1f}%)",
                text_color=ni_color
            )

            self.kpi_ebitda.configure(text=f"${reported_ebitda:,.2f}")
            self.kpi_adj_ebitda.configure(text=f"${management_adjusted_ebitda:,.2f}")

            # Update Output Banner text
            summary_text = (
                f"Gross Profit: {gross_profit:.2f}  |  Net Income: {net_income:.2f}\n"
                f"Reported EBITDA: {reported_ebitda:.2f}  |  Management Adjusted EBITDA: {management_adjusted_ebitda:.2f}"
            )
            self.lbl_results.configure(text=summary_text)

        except ValueError:
            pass

    def export_scenario(self):
        """Export current modified factors to Excel or CSV"""
        if not self.entries:
            messagebox.showwarning("Warning", "No active factors to export.")
            return

        file_path = filedialog.asksaveasfilename(
            title="Save P&L Forecast Scenario",
            defaultextension=".xlsx",
            filetypes=[("Excel File", "*.xlsx"), ("CSV File", "*.csv")]
        )
        if not file_path:
            return

        try:
            scenario_data = {col: [float(entry.get().strip().replace("$", "").replace(",", "") or 0.0)] for col, entry in self.entries.items()}
            export_df = pd.DataFrame(scenario_data)

            if file_path.lower().endswith(".xlsx"):
                export_df.to_excel(file_path, index=False)
            else:
                export_df.to_csv(file_path, index=False)

            messagebox.showinfo("Export Complete", f"Successfully saved scenario to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Could not save file:\n{e}")


if __name__ == "__main__":
    app = PLForecastApp()
    app.mainloop()
