import database as db
from reports import generate_pdf_report
import os

def main():
    # Initialize DB (creates database.db and loads sample data if not present)
    db.init_db()

    # Retrieve user 'green_hero'
    conn = db.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = 'green_hero'")
    user_row = cursor.fetchone()
    if not user_row:
        print("Error: User 'green_hero' not found.")
        conn.close()
        return
    user = dict(user_row)

    # Retrieve their latest monthly entry
    cursor.execute("SELECT * FROM carbon_history WHERE user_id = ? ORDER BY month DESC LIMIT 1", (user['id'],))
    history_row = cursor.fetchone()
    if not history_row:
        print("Error: No carbon history found for green_hero.")
        conn.close()
        return
    month_entry = dict(history_row)
    conn.close()

    # Generate PDF bytes
    print(f"Generating sustainability PDF report for user '{user['username']}' for the month '{month_entry['month']}'...")
    pdf_bytes = generate_pdf_report(user, month_entry)

    # Output file path
    filename = f"carbon_report_{user['username']}_{month_entry['month']}.pdf"
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

    with open(output_path, "wb") as f:
        f.write(pdf_bytes)

    print(f"SUCCESS: Report saved to {output_path}")

if __name__ == "__main__":
    main()
