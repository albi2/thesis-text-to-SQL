from util.db.execute import compare_sqls_outcomes
from infrastructure.database.database_manager import DatabaseManager


def main():
    db_manager = DatabaseManager()
    database_engine = db_manager.create_engine("toxicology")

    sql1 = "SELECT T1.atom_id, COUNT(DISTINCT T2.bond_type) FROM atom AS T1 INNER JOIN bond AS T2 ON T1.molecule_id = T2.molecule_id WHERE T1.molecule_id = 'TR346' GROUP BY T1.atom_id, T2.bond_type"
    sql2 = """SELECT
        T1."atom_id",
        (
            SELECT
            COUNT(DISTINCT T2."bond_type")
            FROM bond AS T2
            WHERE
            T2."molecule_id" = 'TR346'
        ) AS "distinct_bond_types_count"
        FROM atom AS T1
        WHERE
        T1."molecule_id" = 'TR346';"""
    print(compare_sqls_outcomes(sql1, sql2, "public", database_engine))


if __name__ == "__main__":
    main()
