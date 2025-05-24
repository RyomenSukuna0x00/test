from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
import requests
import json
import os

HISTORY_FILE = "trade_history.json"

class ProfitCalculator(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)

        # Input Fields
        self.qty_bought = TextInput(hint_text='Quantity Bought', input_filter='float', multiline=False)
        self.buy_price = TextInput(hint_text='Buy Price (USDT)', input_filter='float', multiline=False)
        self.qty_sold = TextInput(hint_text='Quantity Sold', input_filter='float', multiline=False)
        self.sell_price = TextInput(hint_text='Sell Price (USDT)', input_filter='float', multiline=False)
        self.result = Label(text='')

        self.add_widget(self.qty_bought)
        self.add_widget(self.buy_price)
        self.add_widget(self.qty_sold)
        self.add_widget(self.sell_price)

        # Buttons
        calc_button = Button(text="Calculate Profit")
        calc_button.bind(on_press=self.calculate_profit)
        self.add_widget(calc_button)

        clear_button = Button(text="Clear History")
        clear_button.bind(on_press=self.clear_history)
        self.add_widget(clear_button)

        self.add_widget(self.result)

        # History Log
        self.history_layout = GridLayout(cols=1, size_hint_y=None)
        self.history_layout.bind(minimum_height=self.history_layout.setter('height'))
        self.scroll = ScrollView(size_hint=(1, 1))
        self.scroll.add_widget(self.history_layout)
        self.add_widget(self.scroll)

        self.load_history()

    def save_history_entry(self, entry):
        history = []
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r') as f:
                history = json.load(f)
        history.append(entry)
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f)

    def load_history(self):
        self.history_layout.clear_widgets()
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r') as f:
                history = json.load(f)
                for entry in reversed(history[-50:]):  # Show last 50
                    self.history_layout.add_widget(Label(text=entry, size_hint_y=None, height=30))

    def clear_history(self, instance):
        if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)
        self.load_history()
        self.result.text = "History cleared."

    def calculate_profit(self, instance):
        try:
            qty_b = float(self.qty_bought.text)
            buy_p = float(self.buy_price.text)
            qty_s = float(self.qty_sold.text)
            sell_p = float(self.sell_price.text)
            fee_rate = 0.0008

            total_buy = qty_b * buy_p
            total_sell = qty_s * sell_p
            buy_fee = total_buy * fee_rate
            sell_fee = total_sell * fee_rate

            total_buy_with_fee = total_buy + buy_fee
            total_sell_after_fee = total_sell - sell_fee
            profit_usdt = total_sell_after_fee - total_buy_with_fee

            response = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=tether&vs_currencies=php")
            php_rate = response.json()['tether']['php']
            profit_php = profit_usdt * php_rate

            result_msg = f"Profit: {profit_usdt:.4f} USDT (₱{profit_php:.2f})"
            self.result.text = result_msg
            self.result.color = (0, 1, 0, 1) if profit_usdt > 0 else (1, 0, 0, 1)

            entry = f"{qty_b} → {qty_s} | Buy {buy_p} / Sell {sell_p} | ₱{profit_php:.2f}"
            self.save_history_entry(entry)
            self.load_history()

        except Exception as e:
            self.result.text = f"Error: {e}"
            self.result.color = (1, 0, 0, 1)

class CryptoApp(App):
    def build(self):
        return ProfitCalculator()

if __name__ == "__main__":
    CryptoApp().run()
                         
