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
    # --- Main Calculations ---

# Total Income
total_income = gross_salary + bonus_income

# Pre-Tax Contributions Total (including Pension)
total_pretax_contributions = pension_contribution + sum(pretax_contributions.values())

# Adjusted Gross Income (AGI)
agi = total_income - total_pretax_contributions

# Apply Standard Deduction
standard_deduction = 15000 if filing_status == "Single" else 30000
taxable_income = max(agi - standard_deduction, 0)

# --- Taxes ---
federal_tax = calculate_federal_tax(taxable_income, filing_status)
state_tax = calculate_virginia_tax(taxable_income)
fica_tax = calculate_fica_tax(total_income)
medicare_tax = calculate_medicare_tax(total_income)
total_tax = federal_tax + state_tax + fica_tax + medicare_tax

# --- After-Tax Income ---
after_tax_income = total_income - total_tax

# --- Post-Tax Contributions ---
total_posttax_contributions = sum(posttax_contributions.values())

# --- Net Available Cash After Savings ---
net_available_cash = after_tax_income - total_posttax_contributions - total_other_deductions

# --- Monthly Budget Sums ---

# Housing
housing_total = hoa + home_maintenance + condo_insurance + property_tax

# Groceries
groceries_total = grocery_store + costco_grocery + amazon_grocery

# Restaurants
restaurants_total = dining_out + takeout + coffee

# Transportation
transportation_total = gas + parking + car_insurance + rideshare + car_maintenance

# Utilities
utilities_total = electric + water_sewer + internet + phone

# Subscriptions
subscriptions_total = netflix + chatgpt + prime + crunchyroll + other_subs

# Lifestyle
lifestyle_total = amazon_misc + clothes_drycleaning + gym_supplements

# Other Expenses
other_expenses_total = medical + car_property_tax + miscellaneous

# Total Monthly Expenses
total_monthly_expenses = (
    housing_total + groceries_total + restaurants_total +
    transportation_total + utilities_total + subscriptions_total +
    lifestyle_total + other_expenses_total
)

# Total Annual Expenses
total_annual_expenses = total_monthly_expenses * 12

# --- Final Play Money ---
final_play_money = net_available_cash - total_annual_expenses
# --- Display Outputs ---

st.header("🏦 Income, Taxes, and Contributions Summary")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Gross Annual Income", f"${total_income:,.0f}")
    st.metric("Gross Monthly Income", f"${total_income/12:,.0f}")
    st.metric("Gross Per Paycheck", f"${total_income/24:,.0f}")

with col2:
    st.metric("After-Tax Annual Income", f"${after_tax_income:,.0f}")
    st.metric("After-Tax Monthly Income", f"${after_tax_income/12:,.0f}")
    st.metric("After-Tax Per Paycheck", f"${after_tax_income/24:,.0f}")

with col3:
    st.metric("Play Money Annual (after budget)", f"${final_play_money:,.0f}")
    st.metric("Play Money Monthly", f"${final_play_money/12:,.0f}")
    st.metric("Play Money Per Paycheck", f"${final_play_money/24:,.0f}")

st.divider()

# --- Detailed Budget Table ---
st.header("📋 Detailed Budget Breakdown")
budget_df = pd.DataFrame({
    "Category": [
        "Housing Total", "Groceries Total", "Restaurants Total",
        "Transportation Total", "Utilities Total", "Subscriptions Total",
        "Lifestyle Total", "Other Expenses Total"
    ],
    "Monthly Amount": [
        housing_total, groceries_total, restaurants_total,
        transportation_total, utilities_total, subscriptions_total,
        lifestyle_total, other_expenses_total
    ],
    "Annual Amount": [
        housing_total*12, groceries_total*12, restaurants_total*12,
        transportation_total*12, utilities_total*12, subscriptions_total*12,
        lifestyle_total*12, other_expenses_total*12
    ]
})
st.dataframe(budget_df, use_container_width=True)

st.divider()

# --- Pie Chart of Salary Allocation ---
st.header("📊 Salary Allocation Chart")
labels = [
    "Federal Taxes", "State Taxes", "FICA Taxes", "Medicare Taxes",
    "Pension Contribution", "Other Pre-Tax Contributions",
    "Post-Tax Contributions", "Payroll Deductions",
    "Annual Budget Expenses", "Play Money"
]
values = [
    federal_tax,
    state_tax,
    fica_tax,
    medicare_tax,
    pension_contribution,
    sum(pretax_contributions.values()),
    total_posttax_contributions,
    total_other_deductions,
    total_annual_expenses,
    final_play_money if final_play_money > 0 else 0
]

fig1, ax1 = plt.subplots()
ax1.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
ax1.axis('equal')
st.pyplot(fig1)

# --- Save/Download Settings ---
st.sidebar.header("Save Settings")
if st.sidebar.button("💾 Save Current Settings"):
    settings = {
        "gross_salary": gross_salary,
        "bonus_income": bonus_income,
        "filing_status": filing_status,
        "pretax_contributions": pretax_contributions,
        "posttax_contributions": posttax_contributions,
        "pension_percent": pension_percent * 100,
        "per_paycheck_deductions": {
            "health_insurance": health_insurance,
            "dental_insurance": dental_insurance,
            "parking": parking,
            "disability_insurance": disability_insurance,
            "other_deductions": other_deductions
        },
        "monthly_expenses": {
            "hoa": hoa,
            "home_maintenance": home_maintenance,
            "condo_insurance": condo_insurance,
            "property_tax": property_tax,
            "grocery_store": grocery_store,
            "costco_grocery": costco_grocery,
            "amazon_grocery": amazon_grocery,
            "dining_out": dining_out,
            "takeout": takeout,
            "coffee": coffee,
            "gas": gas,
            "car_insurance": car_insurance,
            "rideshare": rideshare,
            "car_maintenance": car_maintenance,
            "electric": electric,
            "water_sewer": water_sewer,
            "internet": internet,
            "phone": phone,
            "netflix": netflix,
            "chatgpt": chatgpt,
            "prime": prime,
            "crunchyroll": crunchyroll,
            "other_subs": other_subs,
            "amazon_misc": amazon_misc,
            "clothes_drycleaning": clothes_drycleaning,
            "gym_supplements": gym_supplements,
            "medical": medical,
            "car_property_tax": car_property_tax,
            "miscellaneous": miscellaneous
        }
    }
    st.download_button(
        "Download Settings JSON",
        data=json.dumps(settings),
        file_name="paycheck_budget_settings.json",
        mime="application/json"
    )

