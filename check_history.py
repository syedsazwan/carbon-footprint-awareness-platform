import sqlite3

conn = sqlite3.connect("database.db")
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("=" * 70)
print("CARBON CALCULATION HISTORY (carbon_history table)")
print("=" * 70)
cur.execute("""
    SELECT u.username, ch.month, ch.transport, ch.electricity,
           ch.water, ch.food, ch.waste, ch.total_emissions, ch.score_category
    FROM carbon_history ch
    JOIN users u ON u.id = ch.user_id
    ORDER BY u.username, ch.month
""")
rows = cur.fetchall()
if rows:
    print(f"{'Username':<16} {'Month':<10} {'Transport':>10} {'Electricity':>12} {'Water':>8} {'Food':>8} {'Waste':>8} {'TOTAL':>10} {'Category'}")
    print("-" * 90)
    for r in rows:
        print(f"{r['username']:<16} {r['month']:<10} {r['transport']:>10.2f} {r['electricity']:>12.2f} {r['water']:>8.2f} {r['food']:>8.2f} {r['waste']:>8.2f} {r['total_emissions']:>10.2f}  {r['score_category']}")
else:
    print("No carbon history records found.")

print()
print("=" * 70)
print("RECEIPT SCAN HISTORY (receipt_history table)")
print("=" * 70)
cur.execute("""
    SELECT u.username, rh.store_name, rh.purchase_date,
           rh.total_price, rh.total_co2, rh.eco_score, rh.created_at
    FROM receipt_history rh
    JOIN users u ON u.id = rh.user_id
    ORDER BY rh.created_at DESC
""")
rows2 = cur.fetchall()
if rows2:
    print(f"{'Username':<16} {'Store':<26} {'Date':<12} {'Cost':>8} {'CO2(kg)':>9} {'EcoScore':>9}")
    print("-" * 85)
    for r in rows2:
        print(f"{r['username']:<16} {r['store_name']:<26} {r['purchase_date']:<12} ${r['total_price']:>7.2f} {r['total_co2']:>9.2f} {r['eco_score']:>9}")
else:
    print("No receipt scan history saved yet.")

conn.close()
print()
print("Done.")
