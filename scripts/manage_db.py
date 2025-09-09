import argparse
from db_functions import *

def format_query_results(results, columns):
    if not results:
        return "No results found."
    col_widths = [max(len(str(col)), max(len(str(row[i])) for row in results)) for i, col in enumerate(columns)]
    header = " | ".join(str(col).ljust(col_widths[i]) for i, col in enumerate(columns))
    sep = "-+-".join("-" * w for w in col_widths)
    rows = [" | ".join(str(cell).ljust(col_widths[i]) for i, cell in enumerate(row)) for row in results]
    return "\n".join([header, sep] + rows)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "action",
        choices=["init", "load_data", "total_val", "port_vals", "percent_invested"],
        help="Action to perform: 'init' to create tables, " \
        "'load_data' to load sample data, " \
        "'total_val' to get a mapping of client names to portfolio ids, " \
        "port_vals to get values of each portfolio" \
        "percent_invested to get percentage invested for each portfolio"
    )

    parser.add_argument(
        "--query-number",
        type=int,
        help="Query number to run from possible queries"
    )

    args = parser.parse_args()
    conn = get_connection()

    if args.action == "init":
        create_tables(conn)
    elif args.action == "load_data":
        load_sample_data(conn)
    elif args.action == "total_val":
        results, columns = get_clients_with_portfolios(conn)
        print(format_query_results(results, columns))
    elif args.action == "port_vals":
        results, columns = get_portfolio_total_values(conn)
        print(format_query_results(results, columns))
    elif args.action == "percent_invested":
        results, columns = get_percentage_invested(conn)
        print(format_query_results(results, columns))

