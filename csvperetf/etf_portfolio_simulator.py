import pandas as pd
from typing import List, Tuple, Dict
from backtesting_utils import calculate_budget, initialize_data, allocate_monthly_addition

class ETFPortfolioSimulator:
    def __init__(self, path: str, portfolios: List[Tuple[List[str], List[float], List[str]]], initial_budget: float, monthly_increase: float):
        self.path = path
        self.portfolios = portfolios
        self.initial_budget = initial_budget
        self.monthly_increase = monthly_increase
        self.portfolio_data = []
        self.investment_values = []
        self.total_investments = []
        self.percentage_increase = []
        self.etf_prices = []
        self.money_invested = []

    def load_and_initialize_data(self, start_date: str = '2017-03-01', end_date: str = None):
        """Load and initialize portfolio data using the initialize_data function."""
        self.portfolio_data = initialize_data(self.path, self.portfolios, start_date, end_date)

    def calculate_investment_values_with_additions(self):
        dates = self.portfolio_data[0][0].index[:-1]

        for n, (_, allocations, etf_names) in enumerate(self.portfolios):
            current_budget = self.initial_budget
            quota_invested = [current_budget * allocation for allocation in allocations]
            current_investments = quota_invested.copy()
            investment_values_over_time = {name: [] for name in etf_names}
            total_investment_over_time = []
            etf_prices_over_time = {name: [] for name in etf_names}
            money_invested_over_time = {name: [] for name in etf_names}
            percentage_growth_over_time = {name: [] for name in etf_names}

            for month_idx, date in enumerate(dates):
                current_budget = calculate_budget(self.initial_budget, self.monthly_increase, month_idx)
                
                # Calculate month-over-month percentage increase first
                percentage_increases = []
                for i, df in enumerate(self.portfolio_data[n]):
                    prev_date = dates[month_idx - 1] if month_idx > 0 else date
                    percentage_increase = (df.loc[date].values[0] / df.loc[prev_date].values[0]) - 1
                    percentage_increases.append(percentage_increase)
                    current_investments[i] *= (1 + percentage_increase)  # Apply growth
                
                # Now allocate the additional monthly investment based on the lowest increase
                current_investments = allocate_monthly_addition(current_investments, etf_names, percentage_increases, self.monthly_increase)
                

                for i, df in enumerate(self.portfolio_data[n]):
                    investment_values_over_time[etf_names[i]].append(current_investments[i])
                    etf_prices_over_time[etf_names[i]].append(df.loc[date].values[0])
                    money_invested_over_time[etf_names[i]].append(quota_invested[i])
                    percentage_growth_over_time[etf_names[i]].append(percentage_increases[i])

                total_investment_over_time.append(sum(current_investments))

            self.investment_values.append({name: pd.Series(data=investment_values_over_time[name], index=dates) for name in etf_names})
            self.total_investments.append(pd.Series(data=total_investment_over_time, index=dates))
            self.etf_prices.append({name: pd.Series(data=etf_prices_over_time[name], index=dates) for name in etf_names})
            self.money_invested.append({name: pd.Series(data=money_invested_over_time[name], index=dates) for name in etf_names})
            self.percentage_increase.append({name: pd.Series(data=percentage_growth_over_time[name], index=dates) for name in etf_names})

    def get_simulation_results_as_dataframe(self) -> Dict[str, pd.DataFrame]:
        """Return investment results as pandas DataFrames for easy viewing in the variable explorer."""
        total_investment_df = pd.DataFrame({f'Portfolio {i+1}': series for i, series in enumerate(self.total_investments)})

        individual_etf_dfs = {}
        for i, (portfolio_investments, portfolio_prices, portfolio_money, portfolio_growth, (_, _, etf_names)) in enumerate(zip(self.investment_values, self.etf_prices, self.money_invested, self.percentage_increase, self.portfolios)):
            df = pd.DataFrame({
                name: portfolio_investments[name] for name in etf_names
            })
            df_prices = pd.DataFrame({
                name + '_Price': portfolio_prices[name] for name in etf_names
            })
            df_money = pd.DataFrame({
                name + '_Invested': portfolio_money[name] for name in etf_names
            })
            df_growth = pd.DataFrame({
                name + '_Growth': portfolio_growth[name] for name in etf_names
            })
            individual_etf_dfs[f'Portfolio_{i+1}_ETFs'] = pd.concat([df, df_prices, df_money, df_growth], axis=1)

        return {
            "Total_Investment": total_investment_df,
            **individual_etf_dfs
        }
