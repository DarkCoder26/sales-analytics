
import pandas as pd
from database.connection import get_connection


def get_sales_data():
    conn = None

    query = """
        SELECT
            o.order_id,
            o.order_date,
            c.customer_id,
            c.customer_name,
            c.city,
            c.state,
            c.gender,
            p.product_id,
            p.product_name,
            p.category,
            p.price,
            o.quantity,
            o.total_amount
        FROM orders AS o
        INNER JOIN customers AS c
            ON o.customer_id = c.customer_id
        INNER JOIN products AS p
            ON o.product_id = p.product_id
        ORDER BY o.order_date;
    """

    try:
        conn = get_connection()

        cursor = conn.cursor()
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
        finally:
            cursor.close()

        df = pd.DataFrame(rows, columns=columns)
        df["order_date"] = pd.to_datetime(df["order_date"])

        return df

    finally:
        if conn is not None and conn.is_connected():
            conn.close()


if __name__ == "__main__":
    try:
        df = get_sales_data()

        print("\nSALES DATA")
        print(df.to_string(index=False))

        print("\nSHAPE")
        print(df.shape)

        print("\nCOLUMNS")
        print(df.columns.tolist())

        print("\nDATA TYPES")
        print(df.dtypes)

    except Exception as error:
        print(f"Error fetching sales data: {error}")
