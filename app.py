# app.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json

# --- Streamlit Config ---
st.set_page_config(page_title="💸 Paycheck & Budget Optimizer", layout="wide")
st.title("💸 Paycheck + Budget + Tax Optimizer (Twice a Month Paychecks)")

# --- Sidebar Inputs ---
st.sidebar.header("Income")
gross_salary = st.sidebar.number_input("Base Salary ($/year)", value=145000, step=1000)
bonus_income = st.sidebar.number_input("Bonus Income (Optional) ($/year)", value=0, step=1000)

# Pre-Tax Contributions
st.sidebar.header("Pre-Tax Contributions")
pretax_contributions = {
    "403(b) Traditional": st.sidebar.number_input("403(b) Traditional ($/year)", value=20000, step=500),
    "457(b) Traditional": st.sidebar.number_input("457(b) Traditional ($/year)", value=20000, step=500),
    "HSA": st.sidebar.number_input("HSA ($/year)", value=0, step=500),
    "401(a) Employee": st.sidebar.number_input("401(a) Employee Contribution ($/year)", value=0, step=500),
    "Other Pre-Tax": st.sidebar.number_input("Other Pre-Tax Deductions ($/year)", value=0, step=500),
}

# Post-Tax Contributions
st.sidebar.header("Post-Tax Contributions")
posttax_contributions = {
    "Roth 403(b)": st.sidebar.number_input("Roth 403(b) ($/year)", value=0, step=500),
    "Roth 457(b)": st.sidebar.number_input("Roth 457(b) ($/year)", value=0, step=500),
    "Roth IRA": st.sidebar.number_input("Roth IRA ($/year)", value=6500, step=500),
    "Brokerage Investments": st.sidebar.number_input("Brokerage ($/year)", value=5000, step=500),
    "Crypto Investments": st.sidebar.number_input("Crypto ($/year)", value=5000, step=500),
    "Other Post-Tax": st.sidebar.number_input("Other Post-Tax Deductions ($/year)", value=0, step=500),
}

# Other Payroll Deductions
st.sidebar.header("Other Payroll Deductions")
insurance_deductions = st.sidebar.number_input("Insurance, Parking, Other ($/year)", value=5000, step=500)

# Monthly Budget
st.sidebar.header("Monthly Budget Expenses")
housing = st.sidebar.number_input("Housing (HOA, Home Maintenance) ($/month)", value=300)
groceries = st.sidebar.number_input("Groceries ($/month)", value=600)
restaurants = st.sidebar.number_input("Restaurants ($/month)", value=400)
transport = st.sidebar.number_input("Transportation ($/month)", value=300)
utilities = st.sidebar.number_input("Utilities (Electric, Internet, Sewer) ($/month)", value=200)
subscriptions = st.sidebar.number_input("Subscriptions (Netflix, ChatGPT, Prime, etc.) ($/month)", value=100)
lifestyle = st.sidebar.number_input("Lifestyle (Shopping, Miscellaneous) ($/month)", value=800)
other_expenses = st.sidebar.number_input("Other Expenses (Prescriptions, Car Tax, etc.) ($/month)", value=100)

# Save/Load Settings
st.sidebar.header("Save/Load Settings")
if st.sidebar.button("💾 Save Current Settings"):
    settings = {
        "gross_salary": gross_salary,
        "bonus_income": bonus_income,
        "pretax_contributions": pretax_contributions,
        "posttax_contributions": posttax_contributions,
        "insurance_deductions": insurance_deductions,
        "monthly_expenses": {
            "housing": housing,
            "groceries": groceries,
            "restaurants": restaurants,
            "transport": transport,
            "utilities": utilities,
            "subscriptions": subscriptions,
            "lifestyle": lifestyle,
            "other_expenses": other_expenses
        }
    }
    st.download_button(
        "Download Settings JSON",
        data=json.dumps(settings),
        file_name="paycheck_budget_settings.json",
        mime="application/json"
    )

# --- Calculations ---

# Total Income
total_income = gross_salary + bonus_income

# Pre-Tax Contribution Total
total_pretax_contributions = sum(pretax_contributions.values())

# Adjusted Gross Income
agi = total_income - total_pretax_contributions

# Tax Estimates (simple estimates for now)
federal_tax_rate = 0.22
state_tax_rate = 0.0575

federal_tax = agi * federal_tax_rate
state_tax = agi * state_tax_rate
fica_tax = total_income * 0.062
medicare_tax = total_income * 0.0145
total_tax = federal_tax + state_tax + fica_tax + medicare_tax

# After-Tax Income
after_tax_income = total_income - total_tax

# Post-Tax Contributions
total_posttax_contributions = sum(posttax_contributions.values())

# Net Available After Post-Tax Savings
net_available_cash = after_tax_income - total_posttax_contributions - insurance_deductions

# Total Monthly Expenses
monthly_fixed_expenses = housing + groceries + restaurants + transport + utilities + subscriptions + lifestyle + other_expenses
total_annual_fixed_expenses = monthly_fixed_expenses * 12

# Final Play Money
final_play_money = net_available_cash - total_annual_fixed_expenses

# --- No Contributions Scenario ---
no_contrib_agi = total_income
no_contrib_federal_tax = no_contrib_agi * federal_tax_rate
no_contrib_state_tax = no_contrib_agi * state_tax_rate
no_contrib_total_tax = no_contrib_federal_tax + no_contrib_state_tax + fica_tax + medicare_tax
no_contrib_after_tax_income = total_income - no_contrib_total_tax

# --- Tax Savings from Contributions ---
tax_savings = no_contrib_total_tax - total_tax

# --- Display Outputs ---

st.header("🏦 Income & Contribution Summary")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Gross Annual Income", f"${total_income:,.0f}")
    st.metric("Gross Monthly Income", f"${total_income/12:,.0f}")
    st.metric("Gross Per Paycheck", f"${total_income/24:,.0f}")

with col2:
    st.metric("After-Tax Annual (w/ Contributions)", f"${after_tax_income:,.0f}")
    st.metric("After-Tax Monthly", f"${after_tax_income/12:,.0f}")
    st.metric("After-Tax Per Paycheck", f"${after_tax_income/24:,.0f}")

with col3:
    st.metric("After Post-Tax Saving Annual", f"${net_available_cash:,.0f}")
    st.metric("Play Money Annual", f"${final_play_money:,.0f}")
    st.metric("Play Money Per Paycheck", f"${final_play_money/24:,.0f}")

st.divider()

st.header("⚖️ No Contributions Scenario Comparison")
st.write(f"**Take-Home Pay with No Contributions (Annual):** ${no_contrib_after_tax_income:,.0f}")
st.write(f"**Tax Savings Due to Contributions:** ${tax_savings:,.0f}")

st.divider()

st.header("📊 Visualization: Salary Allocation")
labels = [
    "Federal Taxes", "State Taxes", "FICA/Medicare", 
    "Pre-Tax Contributions", "Post-Tax Contributions", 
    "Insurance Deductions", "Fixed Living Expenses", "Play Money"
]
values = [
    federal_tax,
    state_tax,
    fica_tax + medicare_tax,
    total_pretax_contributions,
    total_posttax_contributions,
    insurance_deductions,
    total_annual_fixed_expenses,
    final_play_money if final_play_money > 0 else 0
]

fig1, ax1 = plt.subplots()
ax1.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
ax1.axis('equal')
st.pyplot(fig1)
