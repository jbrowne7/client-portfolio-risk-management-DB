import argparse
import sys
from db_functions import *
from clear_data import reset_db
from create_migration import create_migration_file
from run_migration import run_migration, run_all_migrations

def format_query_results(results, columns):
    if not results:
        return "No results found."
    col_widths = [max(len(str(col)), max(len(str(row[i])) for row in results)) for i, col in enumerate(columns)]
    header = " | ".join(str(col).ljust(col_widths[i]) for i, col in enumerate(columns))
    sep = "-+-".join("-" * w for w in col_widths)
    rows = [" | ".join(str(cell).ljust(col_widths[i]) for i, cell in enumerate(row)) for row in results]
    return "\n".join([header, sep] + rows)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print(f"Try '{sys.argv[0]} --help' for more information.")
        sys.exit(0)

    usage = f"""{sys.argv[0]} [action] [options...]

Actions:
  init                             Create tables
  generate_data                    Generate sample data using python data
  load_data                        Load sample data
  get_portfolios_with_clients      Get mapping of client names to portfolio ids
  port_vals                        Get values of each portfolio
  percent_invested                 Get percentage invested for each portfolio
  add_client                       Add a new client to the clients table
  search_client                    Search for a client by their name for their ID
  get_all_clients                  Get all clients in the db
  portfolio_asset_trades           Get all trades for a particular asset within a portfolio (ordered by trade date)
  get_top_portfolios               Get top n portfolios by total value, default n is 5
  get_clients_with_no_trades       Get clients who have not got any trades in any of their portfolios
  get_trade_counts_by_asset        Get a total count of trades for each asset
  get_recent_trades                Get all trades opened within the last 30 days
  get_assets_latest_price          Get the latest price of assets
  get_notes_with_possible_assets   Get all notes and their linked asset if they have one
  get_all_assets_and_notes         Get all notes matched with assets if possible
  get_assets_with_possible_notes   Get all assets matched with notes if possible
  make_migration                   Create db migration file
  run_migration                    Run a migration file
  run_all_migrations               Run all migration files in order
  wipe_db                          Deletes all records in the db
  add_asset                        Create a new asset
  add_price                        Add a price row for an asset
  add_portfolio                    Add a portfolio for a client
  add_trade                        Add a trade for a portfolio

Options:
  -h, --help                  Show this help message
  --name <name>               Name of the client (use with 'add_client', 'search_client')
  --portfolio_id <id>         ID of the portfolio (use with 'portfolio_asset_trades')
  --asset_id <id>             ID of the asset (use with 'portfolio_asset_trades')
  --n <number>                Number of portfolios to get (use with 'get_top_portfolios')
  --client_id <id>            ID of the client (use with 'add_portfolio')
  --cash_balance <number>     Cash value for a portfolio (use with 'add_portfolio')
  --symbol <text>             Asset symbol (use with 'add_asset')
  --asset_class <text>        Asset class (use with 'add_asset')
  --base_currency <text>      Base currency (use with 'add_asset')
  --price <number>            Price value (use with 'add_price')
  --date <YYYY-MM-DD>         Price date (use with 'add_price', 'add_trade')
"""

    choices=["init", "load_data", "get_portfolios_with_clients", "port_vals", 
                "percent_invested", "add_client", "search_client", 
                "get_all_clients", "portfolio_asset_trades",
                "get_top_portfolios", "get_clients_with_no_trades",
                "get_trade_counts_by_asset", "get_recent_trades",
                "get_assets_latest_price", "get_notes_with_possible_assets",
                "get_all_assets_and_notes", "get_assets_with_possible_notes",
                "make_migration", "run_migration", "run_all_migrations", "wipe_db", "add_portfolio",
                "add_price","add_trade", "add_asset", "generate_data"
                ]
    
    
    parser = argparse.ArgumentParser()

    parser = argparse.ArgumentParser(
        description="Client Portfolio Risk Management CLI",
        usage=usage,
        formatter_class=argparse.RawTextHelpFormatter,
        add_help=False
    )

    # Had to add this to remove error when running --help
    if "--help" in sys.argv or "-h" in sys.argv:
        parser.print_help()
        sys.exit(0)

    parser.add_argument(
        "action",
        choices=choices,
    )

    parser.add_argument("--name", type=str, help="Client name or migration file path")
    parser.add_argument("--portfolio_id", type=int, help="Portfolio ID")
    parser.add_argument("--asset_id", type=int, help="Asset ID")
    parser.add_argument("--n", type=int, help="Limit for top portfolios")
    parser.add_argument("--client_id", type=int, help="Client ID")
    parser.add_argument("--cash_balance", type=int, help="Cash balance")
    parser.add_argument("--symbol", type=str, help="Asset symbol")
    parser.add_argument("--asset_class", type=str, help="Asset class")
    parser.add_argument("--base_currency", type=str, help="Base currency")
    parser.add_argument("--price", type=float, help="Price value")
    parser.add_argument("--price_date", type=str, help="Price date (YYYY-MM-DD)")

    args = parser.parse_args()
    conn = get_connection()

    results = columns = None
    if args.action == "init":
        create_tables(conn)
    elif args.action == "generate_data":
        generate_sample_data()
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
    elif args.action == "add_portfolio":
        if not args.client_id or not args.cash_balance:
            print("Please provide the client ID and cash balance of the portfolio with --client_id and --cash-balance")
        else:
            add_portfolio(conn, args.client_id, args.cash_balance)
    elif args.action == "add_trade":
        if not args.portfolio_id or not args.asset_id or not args.side or not args.quantity or not args.price or not args.date:
            print("Please provide: --portfolio_id --asset_id --side --quantity --price --date")
        else:
            add_trade(conn, args.portfolio_id, args.asset_id, args.side, args.quantity, args.price, args.date)
    elif args.action == "add_asset":
        if not args.symbol or not args.asset_class or not args.base_currency:
            print("Please provide --symbol --asset_class --base_currency")
        else:
            asset_id = add_asset(conn, args.symbol, args.asset_class, args.base_currency)
    elif args.action == "add_price":
        if args.asset_id is None or args.price is None:
            print("Please provide --asset_id --price --price_date")
        else:
            asset_id, price_date = add_price(conn, args.asset_id, args.price, args.price_date)
    elif args.action == "wipe_db":
        reset_db(conn)
    elif args.action == "make_migration":
        if not args.name:
            print("Please provide a name for the migration with --name")
        else: 
            create_migration_file(args.name)
    elif args.action == "run_migration":
        if not args.name:
            print("Please provide the filepath for the migration file with --name")
        else:
            run_migration(args.name)
    elif args.action == "run_all_migrations":
        run_all_migrations()

    if results and columns:
        print(format_query_results(results, columns))
        

