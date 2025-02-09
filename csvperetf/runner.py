import json
from etf_portfolio_simulator import ETFPortfolioSimulator
from plot_utils import (
    plot_total_investment,
    plot_individual_investments,
    plot_selected_etfs_percentage_increase
)

def load_portfolios_from_json(file_path: str):
    with open(file_path, 'r') as f:
        portfolio_data = json.load(f)
    portfolios = [
        (item["files"], item["allocations"], item["names"])
        for item in portfolio_data
    ]
    return portfolios

def main():
    # Configuration paths and parameters
    path = "/home/simone/Finance/Botto/csvperetf/"
    
    portfolios = load_portfolios_from_json("portfolios.json")
    initial_budget = 10000
    monthly_increase = 500

    # Initialize and run the ETF Portfolio Simulator
    simulator = ETFPortfolioSimulator(path, portfolios, initial_budget, monthly_increase)
    simulator.load_and_initialize_data(start_date='2020-01-01', end_date='2024-05-20')
    simulator.calculate_investment_values_with_additions()

    # Store results as DataFrames for easy inspection in the variable explorer
    simulation_results_df = simulator.get_simulation_results_as_dataframe()
    
    # Optionally, plot the results
    # plot_total_investment(simulator.total_investments, rebalance=True)
    # plot_individual_investments(simulator.investment_values, portfolios)
    # plot_selected_etfs_percentage_increase(simulator.percentage_increase, etf_names=['Invesco Physical Gold A', 'SPDR MSCI World UCITS ETF'])
    
    return simulator, simulation_results_df

# Assign simulator instance and its DataFrame results to global variables
simulator_instance, simulation_results_df = main()
