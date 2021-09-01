import pandas as pd
import numpy as np
import robin_stocks.robinhood as r
import robin_stocks
import pyotp

import os
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.


class TradeBot:

    def __init__(self, username: str, password: str, code: str, money: float, symbol: str) -> None:
        self.username = username
        self.password = password
        self.money = money
        self.symbol = symbol

        # Math variables.
        self.percent_buy: float = float(1.5)
        self.percent_sell: float = float(1.5)
        self.buy_price: float = float(0.0)
        self.sell_price: float = float(0.0)

        # Get the totp code from user.
        totp = pyotp.TOTP(code).now()

        # Set up Robinhood login.
        r.login(username, password, mfa_code=totp)

        # Get portfolio information.
        # self.my_stocks = r.build_holdings()

        # Check user has enough money to buy.
        user_account: dict = robin_stocks.robinhood.profiles.load_account_profile()
        self.account_money: float = float(user_account["cash"])

        if self.account_money < self.money:
            raise ValueError("Not enough money to buy.")


        coin_info = self.get_symbol_info()
        self.initial_price: float = float(coin_info["open_price"])

        # Store data for the day.
        self.daily_history_data: dict = {}
        self.daily_history_data[0] = float(coin_info["mark_price"])



    def get_symbol_positions(self) -> int:
        """
        Get all symbol positions.
        """
        crypto_positions = r.crypto.get_crypto_positions()

        for crypto in crypto_positions:
            if crypto["currency"]["code"] == self.symbol:
                symbol_position = crypto

        return symbol_position["quantity"]


    def get_symbol_info(self) -> float:
        """
        Get the info of symbol.
        """
        symbol_coin_info: dict = r.crypto.get_crypto_quote(self.symbol)

        return symbol_coin_info   

    
    def get_symbol_price(self) -> float:
        """
        Get the price of symbol.
        """
        symbol_coin_info: dict = r.crypto.get_crypto_quote(self.symbol)
        symbol_coin_price: int = symbol_coin_info["mark_price"]

        return symbol_coin_price


    def buy_crypto_order(self, amount: float) -> dict:
        buy_order = robin_stocks.robinhood.orders.order_buy_crypto_by_price(self.symbol, amount)
        return buy_order


    def sell_crytpo_order(self, amount: float) -> dict:
        sell_order = robin_stocks.robinhood.orders.order_sell_crypto_by_price(self.symbol, amount)
        return sell_order


    def check_for_trade(self):
        """
        Take the intial_price and current_price and see if we should execute a buy or sell order based on our parameters.
        """

        current_price: float = self.get_symbol_price()

        # Get the historal_data and append new current_price for reference.
        current_key: int = self.daily_history_data.keys()[-1]
        current_key += 1
        self.daily_history_data[current_key] = current_price


        # If we have not yet made any buy orders, then we can't sell anything.
        if self.buy_price == float(0):
            pass
        
        else:
            # If we have a buy price, we need to make sure we sell when we have a profit.
            percent_change: float = float(((current_price - self.buy_price) / self.buy_price) * 100)
            if percent_change > self.percent_sell:
                # Execute a sell order.
                # self.sell_crypto_order(self.get_symbol_positions())
                pass




        



instance = TradeBot(
    username=os.getenv("username"),
    password=os.getenv("password"),
    code=os.getenv("code"),
    money=100.00,
    symbol="DOGE"
)

print(instance.get_symbol_price())



# IS the answer going to be:
# Running get_doge_coin_price() every minute? And checking current vs previous values?