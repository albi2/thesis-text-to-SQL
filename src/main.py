

if __name__ == "__main__":
    converter = DatabaseSchemaConverter()
    msql_schema = converter.process_database()
    print("--- M-SQL Schema Description ---")
    print(msql_schema)
    print("------------------------------")

