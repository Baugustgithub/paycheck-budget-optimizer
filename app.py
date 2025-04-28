# app.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json

# --- Streamlit Config ---
st.set_page_config(page_title="💸 Paycheck & Budget Optimizer", layout="wide")
st.title("💸 Paycheck + Detailed Budget + Real Tax Calculator (2025)")

# --- Sidebar Inputs ---
st.sidebar.header("Income")
gross_salary = st.sidebar.number_input("Base Salary ($/year)", value=145125, step=1000)
bonus_income = st.sidebar.number_input("Bonus Income (Optional) ($/year)", value=0, step=1000)
filing_status = st.sidebar.selectbox("Filing Status", ["Single", "Married Filing Jointly"])

# Pre-Tax Contributions
st.sidebar.header("Pre-Tax Contributions")
pension_percent = st.sidebar.number_input("Pension/VRS Contribution (% of Salary)", value=5.0, step=0.1) / 100
pension_contribution = gross_salary * pension_percent

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

# Other Payroll Deductions Per Paycheck
st.sidebar.header("Other Payroll Deductions (Per Paycheck)")
health_insurance = st.sidebar.number_input("Health Insurance ($/paycheck)", value=100)
dental_insurance = st.sidebar.number_input("Dental Insurance ($/paycheck)", value=20)
parking = st.sidebar.number_input("Parking ($/paycheck)", value=40)
disability_insurance = st.sidebar.number_input("Disability Insurance ($/paycheck)", value=15)
other_deductions = st.sidebar.number_input("Other Payroll Deductions ($/paycheck)", value=25)

# Total Payroll Deductions
total_other_deductions = 24 * (health_insurance + dental_insurance + parking + disability_insurance + other_deductions)

# Detailed Monthly Budget
st.sidebar.header("Monthly Budget (Detailed)")
# Housing
st.sidebar.subheader("🏠 Housing")
hoa = st.sidebar.number_input("HOA Fees ($/month)", value=232)
home_maintenance = st.sidebar.number_input("Home Maintenance ($/month)", value=50)
condo_insurance = st.sidebar.number_input("Condo Insurance ($/month)", value=78)
property_tax = st.sidebar.number_input("Property Taxes ($/month)", value=175)

# Groceries
st.sidebar.subheader("🥦 Groceries")
grocery_store = st.sidebar.number_input("Grocery Stores ($/month)", value=600)
costco_grocery = st.sidebar.number_input("Costco Grocery ($/month)", value=100)
amazon_grocery = st.sidebar.number_input("Amazon Grocery ($/month)", value=0)

# Restaurants
st.sidebar.subheader("🍽️ Restaurants")
dining_out = st.sidebar.number_input("Dining Out ($/month)", value=400)
takeout = st.sidebar.number_input("Takeout ($/month)", value=100)
coffee = st.sidebar.number_input("Coffee Shops ($/month)", value=50)

# Transportation
st.sidebar.subheader("🚗 Transportation")
gas = st.sidebar.number_input("Gas ($/month)", value=60)
car_insurance = st.sidebar.number_input("Car Insurance ($/month)", value=97)
rideshare = st.sidebar.number_input("Uber/Lyft ($/month)", value=30)
car_maintenance = st.sidebar.number_input("Car Maintenance ($/month)", value=60)

# Utilities
st.sidebar.subheader("⚡ Utilities")
electric = st.sidebar.number_input("Electric ($/month)", value=95)
water_sewer = st.sidebar.number_input("Water/Sewer ($/month)", value=5)
internet = st.sidebar.number_input("Internet ($/month)", value=50)
phone = st.sidebar.number_input("Phone Bill ($/month)", value=70)

# Subscriptions
st.sidebar.subheader("📺 Subscriptions")
netflix = st.sidebar.number_input("Netflix ($/month)", value=20)
chatgpt = st.sidebar.number_input("ChatGPT ($/month)", value=20)
prime = st.sidebar.number_input("Amazon Prime ($/month)", value=10)
crunchyroll = st.sidebar.number_input("Crunchyroll ($/month)", value=10)
other_subs = st.sidebar.number_input("Other Subscriptions ($/month)", value=40)

# Lifestyle
st.sidebar.subheader("🎯 Lifestyle")
amazon_misc = st.sidebar.number_input("Amazon Non-Grocery ($/month)", value=100)
clothes_drycleaning = st.sidebar.number_input("Clothes/Dry Cleaning ($/month)", value=160)
gym_supplements = st.sidebar.number_input("Gym/Supplements ($/month)", value=150)

# Other Expenses
st.sidebar.subheader("💊 Other Expenses")
medical = st.sidebar.number_input("Medical/Prescriptions ($/month)", value=75)
car_property_tax = st.sidebar.number_input("Car Property Tax ($/month)", value=13)
miscellaneous = st.sidebar.number_input("Miscellaneous ($/month)", value=50)
# --- Tax Calculation Functions ---

def calculate_federal_tax(agi, filing_status):
    brackets_single = [
        (0, 0.10),
        (11925, 0.12),
        (48475, 0.22),
        (103350, 0.24),
        (197300, 0.32),
        (250525, 0.35),
        (626350, 0.37)
    ]
    brackets_married = [
        (0, 0.10),
        (23850, 0.12),
        (96950, 0.22),
        (206700, 0.24),
        (394600, 0.32),
        (501050, 0.35),
        (752600, 0.37)
    ]
    brackets = brackets_single if filing_status == "Single" else brackets_married
    
    tax = 0
    previous_limit = 0
    for limit, rate in brackets:
        if agi > previous_limit:
            taxable_at_this_rate = min(agi, limit) - previous_limit
            tax += taxable_at_this_rate * rate
            previous_limit = limit
        else:
            break
    return max(tax, 0)

def calculate_virginia_tax(agi):
    brackets = [
        (0, 0.02),
        (3000, 0.03),
        (5000, 0.05),
        (17000, 0.0575)
    ]
    
    tax = 0
    previous_limit = 0
    for limit, rate in brackets:
        if agi > previous_limit:
            taxable_at_this_rate = min(agi, limit) - previous_limit
            tax += taxable_at_this_rate * rate
            previous_limit = limit
        else:
            break
    if agi > 17000:
        tax += (agi - 17000) * 0.0575
    return max(tax, 0)

def calculate_fica_tax(total_income):
    social_security_cap = 168600  # For 2024/2025
    taxed_income = min(total_income, social_security_cap)
    return taxed_income * 0.062

def calculate_medicare_tax(total_income):
    return total_income * 0.0145
