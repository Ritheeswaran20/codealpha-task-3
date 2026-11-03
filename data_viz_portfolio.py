"""Task 3: Data Visualization - Retail Sales Portfolio (Matplotlib + Seaborn)"""
import numpy as np, pandas as pd
import matplotlib.pyplot as plt, seaborn as sns

sns.set_theme(style="whitegrid", palette="deep", font_scale=1.0)
rng = np.random.default_rng(42)

# ---------- 1. RAW DATA ----------
months = pd.date_range("2025-01-01", periods=12, freq="MS")
regions = ["North", "South", "East", "West"]
cats = ["Electronics", "Clothing", "Home", "Grocery"]
rows = []
for m in months:
    for r in regions:
        for c in cats:
            base = {"Electronics": 900, "Clothing": 600, "Home": 500, "Grocery": 700}[c]
            season = 1 + 0.35 * (m.month in (10, 11, 12)) + 0.1 * np.sin(m.month / 2)
            growth = 1 + 0.02 * m.month
            sales = base * season * growth * rng.normal(1, 0.08) * {"North": 1.1, "South": 0.9, "East": 1.0, "West": 1.2}[r]
            margin = {"Electronics": .18, "Clothing": .35, "Home": .28, "Grocery": .12}[c] + rng.normal(0, .02)
            rows.append([m, r, c, round(sales, 2), round(sales * margin, 2), int(sales / rng.uniform(30, 60))])
df = pd.DataFrame(rows, columns=["Month", "Region", "Category", "Sales", "Profit", "Units"])
df.to_csv("retail_sales_raw.csv", index=False)

# ---------- 2. INDIVIDUAL CHARTS ----------
def save(fig, name): fig.tight_layout(); fig.savefig(name, dpi=150); plt.close(fig)

monthly = df.groupby("Month")[["Sales", "Profit"]].sum()
fig, ax = plt.subplots(figsize=(9, 4.5))
ax.plot(monthly.index, monthly.Sales, marker="o", lw=2.5, label="Sales")
ax.plot(monthly.index, monthly.Profit, marker="s", lw=2.5, label="Profit")
ax.annotate("Q4 festive spike", (monthly.index[10], monthly.Sales.iloc[10]),
            xytext=(-120, 10), textcoords="offset points", arrowprops=dict(arrowstyle="->"))
ax.set(title="Sales & Profit Trend 2025", ylabel="Amount ($)"); ax.legend()
save(fig, "1_trend_line.png")

cat = df.groupby("Category")[["Sales", "Profit"]].sum().sort_values("Sales", ascending=False)
fig, ax = plt.subplots(figsize=(8, 4.5))
cat.plot.bar(ax=ax, rot=0); ax.set(title="Sales vs Profit by Category", ylabel="Amount ($)")
save(fig, "2_category_bar.png")

pivot = df.pivot_table(index="Region", columns="Category", values="Sales", aggfunc="sum")
fig, ax = plt.subplots(figsize=(8, 4.5))
sns.heatmap(pivot, annot=True, fmt=".0f", cmap="YlGnBu", ax=ax); ax.set_title("Sales Heatmap: Region x Category")
save(fig, "3_heatmap.png")

fig, ax = plt.subplots(figsize=(8, 4.5))
sns.boxplot(data=df, x="Category", y="Sales", hue="Category", legend=False, ax=ax)
ax.set_title("Sales Distribution by Category")
save(fig, "4_boxplot.png")

df["Margin%"] = df.Profit / df.Sales * 100
fig, ax = plt.subplots(figsize=(8, 4.5))
sns.scatterplot(data=df, x="Sales", y="Margin%", hue="Category", size="Units", alpha=.7, ax=ax)
ax.set_title("Sales vs Profit Margin (bubble = units)")
save(fig, "5_scatter.png")

# ---------- 3. DASHBOARD ----------
fig = plt.figure(figsize=(16, 10))
gs = fig.add_gridspec(3, 3, height_ratios=[.5, 1.5, 1.5])
tot_s, tot_p = df.Sales.sum(), df.Profit.sum()
kpis = [("Total Sales", f"${tot_s/1e3:,.0f}K"), ("Total Profit", f"${tot_p/1e3:,.0f}K"),
        ("Profit Margin", f"{tot_p/tot_s:.1%}")]
for i, (k, v) in enumerate(kpis):
    a = fig.add_subplot(gs[0, i]); a.axis("off")
    a.text(.5, .6, v, ha="center", fontsize=30, weight="bold", color="#1f77b4")
    a.text(.5, .15, k, ha="center", fontsize=14, color="gray")
a = fig.add_subplot(gs[1, :2])
a.plot(monthly.index, monthly.Sales, marker="o", lw=2.5, label="Sales")
a.plot(monthly.index, monthly.Profit, marker="s", lw=2.5, label="Profit"); a.legend(); a.set_title("Monthly Trend")
a = fig.add_subplot(gs[1, 2]); reg = df.groupby("Region").Sales.sum().sort_values()
a.barh(reg.index, reg.values, color=sns.color_palette("deep")[2]); a.set_title("Sales by Region")
a = fig.add_subplot(gs[2, :2]); sns.heatmap(pivot, annot=True, fmt=".0f", cmap="YlGnBu", ax=a, cbar=False); a.set_title("Region x Category")
a = fig.add_subplot(gs[2, 2]); mg = (cat.Profit / cat.Sales * 100).sort_values()
a.bar(mg.index, mg.values, color=sns.color_palette("deep")[1]); a.set_title("Profit Margin % by Category"); a.tick_params(axis="x", rotation=30)
fig.suptitle("Retail Performance Dashboard - 2025", fontsize=22, weight="bold")
save(fig, "dashboard.png")

# ---------- 4. INSIGHTS ----------
best_reg = df.groupby("Region").Sales.sum().idxmax()
best_margin = (cat.Profit / cat.Sales).idxmax()
top_profit = cat.Profit.idxmax()
q4 = monthly.Sales.iloc[-3:].mean() / monthly.Sales.iloc[:9].mean() - 1
print(f"Best region: {best_reg}\nHighest margin: {best_margin}\nMost total profit: {top_profit}\nQ4 uplift: {q4:.0%}")
