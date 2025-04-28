# app.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --- Streamlit Config ---
st.set_page_config(page_title="💸 Paycheck + Budget Optimizer", layout="wide")
st.title("💸 Paycheck + Budget + Play Money Optimizer")

# --- Sidebar Inputs ---
st.sidebar.header("Income")
gross_salary = st.sidebar.number_input("Base Salary ($/year)", value=145000, step=1000)
bonus_income = st.sidebar.number_input("Bonus Income (Optional) ($/year)", value=0, step=1000)

st.sidebar.header("Pre-Tax Contributions")
pretax_contributions = {
    "403(b) Traditional": st.sidebar.number_input("403(b) Traditional ($/year)", value=20000, step=500),
    "457(b) Traditional": st.sidebar.number_input("457(b) Traditional ($/year)", value=20000, step=500),
    "HSA": st.sidebar.number_input("HSA ($/year)", value=0, step=500),
    "401(a) Employee": st.sidebar.number_input("401(a) Employee Contribution ($/year)", value=0, step=500),
}

st.sidebar.header("Post-Tax Contributions")
posttax_contributions = {
    "Roth IRA": st.sidebar.number_input("Roth IRA ($/year)", value=6500, step=500),
    "Brokerage Investments": st.sidebar.number_input("Brokerage ($/year)", value=5000, step=500),
    "Crypto Investments": st.sidebar.number_input("Crypto ($/year)", value=5000, step=500),
}

st.sidebar.header("Monthly Budget Categories")
housing = st.sidebar.number_input("Housing (HOA, Home Maintenance) ($/month)", value=300)
groceries = st.sidebar.number_input("Groceries ($/month)", value=600)
restaurants = st.sidebar.number_input("Restaurants ($/month)", value=400)
transport = st.sidebar.number_input("Transportation (Gas, Parking, Uber, Maintenance) ($/month)", value=300)
insurance = st.sidebar.number_input("Insurance (Auto, Health, Condo) ($/month)", value=300)
utilities = st.sidebar.number_input("Utilities (Electric, Internet, Sewer) ($/month)", value=175)
subscriptions = st.sidebar.number_input("Subscriptions (Netflix, ChatGPT, Crunchyroll, Prime, etc.) ($/month)", value=100)
lifestyle = st.sidebar.number_input("Lifestyle (Shopping, Miscellaneous, Supplements) ($/month)", value=800)
other_expenses = st.sidebar.number_input("Other Expenses (Prescriptions, Car Taxes, etc.) ($/month)", value=100)

# --- Calculations ---
# Total income
total_income = gross_salary + bonus_income

# Pre-tax contributions total
total_pretax_contributions = sum(pretax_contributions.values())

# Adjusted Gross Income (AGI) approximation
agi = total_income - total_pretax_contributions

# Estimate Taxes (basic approximation for demo purposes)
federal_tax_rate = 0.22  # Simplified guess (adjust later if needed)
state_tax_rate = 0.0575  # Virginia flat approx.

federal_tax = agi * federal_tax_rate
state_tax = agi * state_tax_rate
fica_tax = total_income * 0.062  # Social Security
medicare_tax = total_income * 0.0145

total_tax = federal_tax + state_tax + fica_tax + medicare_tax

# After-tax income after pre-tax contributions
after_tax_income = total_income - total_tax

# Post-tax contributions total
total_posttax_contributions = sum(posttax_contributions.values())

# After-tax, after-post-tax-contributions income
after_saving_income = after_tax_income - total_posttax_contributions

# Annual Budget
total_annual_fixed_expenses = 12 * (housing + groceries + restaurants + transport + insurance + utilities + subscriptions + lifestyle + other_expenses)

# Play Money (what's left after savings + necessary expenses)
play_money = after_saving_income - total_annual_fixed_expenses

# --- Main Display ---
st.header("🏦 Income & Taxes Summary")
st.write(f"**Total Income:** ${total_income:,.0f}")
st.write(f"**Total Pre-Tax Contributions:** ${total_pretax_contributions:,.0f}")
st.write(f"**Adjusted Gross Income (AGI):** ${agi:,.0f}")
st.write(f"**Estimated Total Taxes:** ${total_tax:,.0f}")
st.write(f"**After-Tax Income:** ${after_tax_income:,.0f}")
st.write(f"**Total Post-Tax Contributions:** ${total_posttax_contributions:,.0f}")
st.write(f"**Disposable Income (After Taxes & Post-Tax Savings):** ${after_saving_income:,.0f}")

st.header("🧾 Budget Summary")
st.write(f"**Annual Fixed Living Expenses:** ${total_annual_fixed_expenses:,.0f}")
st.write(f"**Remaining Play Money (After Everything):** ${play_money:,.0f}")

# --- Pie Chart: Money Flow ---
st.header("📊 Money Flow Visualization")
labels = ["Federal Taxes", "State Taxes", "FICA/Medicare", "Pre-Tax Contributions", "Post-Tax Contributions", "Fixed Living Expenses", "Play Money"]
values = [
    federal_tax,
    state_tax,
    fica_tax + medicare_tax,
    total_pretax_contributions,
    total_posttax_contributions,
    total_annual_fixed_expenses,
    play_money if play_money > 0 else 0
]

fig1, ax1 = plt.subplots()
ax1.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
ax1.axis('equal')
st.pyplot(fig1)

# --- Waterfall Chart: Salary Reduction Step-by-Step ---
st.header("📉 Salary to Play Money Breakdown")

steps = [
    ("Total Income", total_income),
    ("- Pre-Tax Contributions", -total_pretax_contributions),
    ("- Federal Tax", -federal_tax),
    ("- State Tax", -state_tax),
    ("- FICA/Medicare", -(fica_tax + medicare_tax)),
    ("- Post-Tax Contributions", -total_posttax_contributions),
    ("- Fixed Expenses", -total_annual_fixed_expenses),
    ("= Play Money", play_money),
]

df_steps = pd.DataFrame(steps, columns=["Step", "Amount"])
fig2, ax2 = plt.subplots(figsize=(10,5))

running_total = 0
y = []
for amount in df_steps["Amount"]:
    running_total += amount
    y.append(running_total)

ax2.bar(df_steps["Step"], y, color=['green' if v > 0 else 'red' for v in df_steps["Amount"]])
ax2.axhline(0, color='black', linewidth=0.8)
plt.xticks(rotation=45, ha='right')
st.pyplot(fig2)
