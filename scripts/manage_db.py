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
        choices=["init", "load_data", "total_val", "port_vals", "percent_invested", "add_client", "search_client", "get_all_clients", "portfolio_asset_trades"],
        help="Action to perform: 'init' to create tables, " \
        "'load_data' to load sample data, " \
        "'total_val' to get a mapping of client names to portfolio ids, " \
        "'port_vals' to get values of each portfolio" \
        "'percent_invested' to get percentage invested for each portfolio" \
        "'add_client' to add a new client to the clients table" \
        "'search_client' to search for a client by their name for their ID" \
        "'get_all_clients' to get all clients in the db" \
        "'portfolio_asset_trades' to get all trades for a particular asset within a portfolio (ordered by trade date)" \
    )

    parser.add_argument(
        "--name",
        type=str,
        help="Name of the client (use with 'add_client', 'search_client')"
    )

    parser.add_argument(
        "--portfolio_id",
        type=str,
        help="ID of the portfolio (use with 'portfolio_asset_trades')"
    )

    parser.add_argument(
        "--asset_id",
        type=str,
        help="ID of the asset (use with 'portfolio_asset_trades')"
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
    elif args.action == "add_client":
        if not args.name:
            print("Please provide a client name with --name")
        else:
            add_client(conn, args.name)
    elif args.action == "search_client":
        if not args.name:
            print("Please provide a name to search with --name")
        else:
            results, columns = search_clients_by_name(conn, args.name)
            print(format_query_results(results, columns))
    elif args.action == "get_all_clients":
        results, columns = get_all_clients(conn)
        print(format_query_results(results, columns))
    elif args.action == "portfolio_asset_trades":
        if not args.portfolio_id or not args.asset_id:
            print("Please prove both a portfolio id with --portfolio_id and asset id with --asset_id")
        else:
            results, columns = get_all_trades_for_asset_in_portfolio(conn, args.portfolio_id, args.asset_id)
            print(format_query_results(results, columns))
        

