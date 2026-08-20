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
        self.geometry("980x780")
        self.minsize(880, 680)

        self.df = None
        self.entries = {}
        self.sliders = {}

        # Default Baseline Model
        self.default_data = {
            "Total_Sales": 107000.0,
            "Discounts_Refunds": -7000.0,
            "Total_Direct_COGS": 52500.0,
            "Total_Indirect_COGS": 13500.0,
            "Total_Operating_Expenses": 14000.0,
            "Marketing_Advertising": 5000.0,
            "Payroll_Salaries": 22000.0,
            "Taxes_Interest": 3500.0
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
            text="Interactive Factor Sensitivity & Real-Time P&L Forecasting Engine",
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
        self.kpi_rev = self._create_kpi_box(self.kpi_frame, "TOTAL REVENUE", "$100,000", "#38bdf8", 0)
        self.kpi_cogs = self._create_kpi_box(self.kpi_frame, "TOTAL COGS", "$66,000", "#f87171", 1)
        self.kpi_gp = self._create_kpi_box(self.kpi_frame, "GROSS PROFIT", "$34,000 (34%)", "#fbbf24", 2)
        self.kpi_ni = self._create_kpi_box(self.kpi_frame, "NET INCOME", "$20,000 (20%)", "#4ade80", 3)

        # ---------------------------------------------------------------------
        # MAIN SCROLLABLE INPUT GRID
        # ---------------------------------------------------------------------
        self.main_frame = ctk.CTkScrollableFrame(
            self,
            width=940,
            height=400,
            corner_radius=10,
            fg_color=("#0f172a", "#090d16")
        )
        self.main_frame.pack(padx=16, pady=8, fill="both", expand=True)

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
                width=240
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

    def calculate_interactions(self):
        """Real-time multi-factor P&L accounting calculation"""
        data = {}
        for col, entry in self.entries.items():
            raw_text = entry.get().strip().replace("$", "").replace(",", "")
            try:
                data[col] = float(raw_text) if raw_text else 0.0
            except ValueError:
                data[col] = 0.0

        # Flexible column resolution
        def get_val(*keys, default=0.0):
            for k in keys:
                for col in data:
                    if k.lower() == col.lower() or k.lower() == col.lower().replace("_", ""):
                        return data[col]
            return default

        total_sales = get_val("Total_Sales", "Sales", "Gross_Sales", default=100000.0)
        discounts = get_val("Discounts_Refunds", "Discounts", "Refunds", default=0.0)
        total_revenue = total_sales + discounts

        direct_cogs = get_val("Total_Direct_COGS", "Direct_COGS", "COGS_Direct", default=50000.0)
        indirect_cogs = get_val("Total_Indirect_COGS", "Indirect_COGS", "COGS_Indirect", default=10000.0)
        total_cogs = direct_cogs + indirect_cogs

        gross_profit = total_revenue - total_cogs
        gp_margin = (gross_profit / total_revenue * 100.0) if total_revenue > 0 else 0.0

        # Operating Expenses
        opex_total = get_val("Total_Operating_Expenses", "Operating_Expenses", "OpEx", default=15000.0)
        marketing = get_val("Marketing_Advertising", "Marketing", "Advertising", default=0.0)
        payroll = get_val("Payroll_Salaries", "Payroll", "Salaries", default=0.0)
        taxes = get_val("Taxes_Interest", "Taxes", "Interest", default=0.0)

        # Sum granular OpEx if total was 0
        if opex_total == 0.0 and (marketing > 0 or payroll > 0):
            opex_total = marketing + payroll

        net_income = gross_profit - opex_total - taxes
        net_margin = (net_income / total_revenue * 100.0) if total_revenue > 0 else 0.0

        # Update KPI display boxes
        self.kpi_rev.configure(text=f"${total_revenue:,.2f}")
        self.kpi_cogs.configure(text=f"${total_cogs:,.2f}")
        
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
