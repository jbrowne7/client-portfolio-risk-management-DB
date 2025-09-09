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
        choices=["init", "load_data", "get_portfolios_with_clients", "port_vals", 
                 "percent_invested", "add_client", "search_client", 
                 "get_all_clients", "portfolio_asset_trades",
                 "get_top_portfolios", "get_clients_with_no_trades",
                 "get_trade_counts_by_asset", "get_recent_trades",
                 "get_assets_latest_price", "get_notes_with_possible_assets",
                 "get_all_assets_and_notes", "get_assets_with_possible_notes"],
        help="Action to perform: 'init' to create tables, " \
        "'load_data' to load sample data, " \
        "'get_portfolios_with_clients' to get a mapping of client names to portfolio ids, " \
        "'port_vals' to get values of each portfolio" \
        "'percent_invested' to get percentage invested for each portfolio" \
        "'add_client' to add a new client to the clients table" \
        "'search_client' to search for a client by their name for their ID" \
        "'get_all_clients' to get all clients in the db" \
        "'portfolio_asset_trades' to get all trades for a particular asset within a portfolio (ordered by trade date)" \
        "'get_top_portfolios' to get top `n` portfolios by total value, default `n` is 5" \
        "'get_clients_with_no_trades' to get clients who have not got any trades in any of their portfolios" \
        "'get_trade_counts_by_asset' to get a total count of trades for each asset" \
        "'get_recent_trades' to get all trades opened within the last 30 days"
        "'get_assets_latest_price' to get the latest price of assets" \
        "'get_notes_with_possible_assets' to get all notes and their linked asset if they have one" \
        "'get_all_assets_and_notes' to get all notes matched with assets if possible" \
        "'get_assets_with_possible_notes' to get all assets matched with notes if possible"
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

    parser.add_argument(
        "--n",
        type=str,
        help="integer used in get_top_portfolios to specify number of portfolios to get"
    )

    args = parser.parse_args()
    conn = get_connection()

    results = columns = None
    if args.action == "init":
        create_tables(conn)
    elif args.action == "load_data":
        load_sample_data(conn)
    elif args.action == "get_portfolios_with_clients":
        results, columns = get_portfolios_with_clients(conn)
    elif args.action == "port_vals":
        results, columns = get_portfolio_total_values(conn)
    elif args.action == "percent_invested":
        results, columns = get_percentage_invested(conn)
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
    elif args.action == "get_all_clients":
        results, columns = get_all_clients(conn)
    elif args.action == "portfolio_asset_trades":
        if not args.portfolio_id or not args.asset_id:
            print("Please prove both a portfolio id with --portfolio_id and asset id with --asset_id")
        else:
            results, columns = get_all_trades_for_asset_in_portfolio(conn, args.portfolio_id, args.asset_id)
    elif args.action == "get_top_portfolios":
        if not args.n:
            results, columns = get_top_portfolios_by_value(conn)
        else:
            results, columns = get_top_portfolios_by_value(conn, args.n)
    elif args.action == "get_clients_with_no_trades":
        results, columns = get_clients_with_no_trades(conn)
    elif args.action == "get_trade_counts_by_asset":
        results, columns = get_trade_counts_by_asset(conn)
    elif args.action == "get_recent_trades":
        results, columns = get_recent_trades(conn)
    elif args.action == "get_assets_latest_price":
        results, columns = get_assets_latest_price(conn)
    elif args.action == "get_notes_with_possible_assets":
        results, columns = get_notes_with_possible_assets(conn)
    elif args.action == "get_all_assets_and_notes":
        results, columns = get_all_assets_and_notes(conn)
    elif args.action == "get_assets_with_possible_notes":
        results, columns = get_assets_with_possible_notes(conn)

    if results and columns:
        print(format_query_results(results, columns))
        

