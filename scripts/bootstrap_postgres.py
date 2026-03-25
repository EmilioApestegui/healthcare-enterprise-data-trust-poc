from __future__ import annotations

from healthcare_enterprise_data_trust_poc.db import app_engine, load_workbook_to_postgres, test_connection

def main():
    engine = app_engine()
    test_connection(engine)
    loaded = load_workbook_to_postgres(engine)
    print("Loaded workbook tables into Postgres:")
    for table_name, count in loaded.items():
        print(f" - {table_name}: {count}")

if __name__ == "__main__":
    main()
