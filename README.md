# coinbaseadvancedtrade-python
The Python client for the [Coinbase Advanced Trade API](https://docs.cloud.coinbase.com/advanced-trade-api/docs) (formerly known as Coinbase pro)

refactor not finished yet, but it's getting there.
Also this readme isn't fully rewritten yet.

##### Provided under MIT License by Tony Denion.
*Note: this library may be subtly broken or buggy. The code is released under
the MIT License – please take the following message to heart:*
> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## Benefits
- A simple to use python wrapper for endpoints.-
- In about 10 minutes, you could be programmatically trading on one of the
largest Bitcoin exchanges in the *world*!
- Do not worry about handling the nuances of the API with easy-to-use methods
for every API endpoint.
- Gain an advantage in the market by getting under the hood of CB Adv to learn
what and who is behind every tick.

## Under Development
- Test Scripts
- Additional Functionality for the real-time order book
- MongoDB integration

## Getting Started
This README is documentation on the syntax of the python client presented in
this repository. See function docstrings for full syntax details.  
**This API attempts to present a clean interface to CB Advanced Trade, but in order to use it
to its full potential, you must familiarize yourself with the official CB Advanced Trade
[documentation](https://docs.cloud.coinbase.com/advanced-trade-api/docs).**

- You may manually install the project or use ```pip```:
```python
pip install cbadv (not yet added to PyPi)
#or
pip install git+git://github.com/kkuette/coinbaseadv-python.git
```

### Client

```python
import cbadv

API_KEY = ''
API_SECRET = ''

client = cbadv.Client(api_key=API_KEY, api_secret=API_SECRET)
```

or

```python
import json
import cbadv

client = cbadv.Client(**json.load(open('path/to/credentials.json')))
```

### Client Methods

All API endpoints are now Private. You must setup API access within your
[account settings](https://coinbase.com/settings/api).


- [list_accounts](https://docs.cloud.coinbase.com/advanced-trade-api/reference/retailbrokerageapi_getaccounts)
```python
client.list_accounts()
```

- [get_account](https://docs.cloud.coinbase.com/advanced-trade-api/reference/retailbrokerageapi_getaccount)
```python
client.get_account("7d0f7d8e-dd34-4d9c-a846-06f431c381ba")
```

- [buy & sell](https://docs.cloud.coinbase.com/advanced-trade-api/reference/retailbrokerageapi_postorder)
```python
# Buy 0.01 BTC @ 100 USD
client.buy(price='100.00', #USD
               size='0.01', #BTC
               order_type='limit',
               product_id='BTC-USD')
```
```python
# Sell 0.01 BTC @ 200 USD
client.sell(price='200.00', #USD
                size='0.01', #BTC
                order_type='limit',
                product_id='BTC-USD')
```
```python
# Limit order-specific method
client.place_limit_order(product_id='BTC-USD', 
                              side='buy', 
                              price='200.00', 
                              size='0.01')
```
```python
# Place a market order by specifying amount of USD to use. 
# Alternatively, `size` could be used to specify quantity in BTC amount.
client.place_market_order(product_id='BTC-USD', 
                               side='buy', 
                               funds='100.00')
```
```python
# Stop order. `funds` can be used instead of `size` here.
client.place_stop_order(product_id='BTC-USD', 
                              stop_type='loss', 
                              price='200.00', 
                              size='0.01')
```

- [cancel_order](https://docs.cloud.coinbase.com/advanced-trade-api/reference/retailbrokerageapi_cancelorders)
```python
client.cancel_order("7d0f7d8e-dd34-4d9c-a846-06f431c381ba")
```

- [list_orders](https://docs.cloud.coinbase.com/advanced-trade-api/reference/retailbrokerageapi_gethistoricalorders)
```python
client.list_orders()
```

- [list_fills](https://docs.cloud.coinbase.com/advanced-trade-api/reference/retailbrokerageapi_getfills)
```python
client.list_fills()
```

- [get_order](https://docs.cloud.coinbase.com/advanced-trade-api/reference/retailbrokerageapi_gethistoricalorder)
```python
client.get_order("7d0f7d8e-dd34-4d9c-a846-06f431c381ba")
```

- [list_products](https://docs.cloud.coinbase.com/advanced-trade-api/reference/retailbrokerageapi_getproducts)
```python
client.list_products()
```

- [get_product](https://docs.cloud.coinbase.com/advanced-trade-api/reference/retailbrokerageapi_getproduct)
```python
client.get_product("BTC-USD")
```

- [get_product_candles](https://docs.cloud.coinbase.com/advanced-trade-api/reference/retailbrokerageapi_getcandles)
```python
client.get_product_candles("BTC-USD", start, end, granularity)
```

- [get_market_trades](https://docs.cloud.coinbase.com/advanced-trade-api/reference/retailbrokerageapi_getmarkettrades)
```python
client.get_market_trades("BTC-USD", limit=100) # limit default is 100
```

- [get_transactions_summary](https://docs.cloud.coinbase.com/advanced-trade-api/reference/retailbrokerageapi_gettransactionsummary)
```python
client.get_transactions_summary()
```

### WebsocketClient

If you would like to receive real-time market updates, you must subscribe to the
[websocket feed](https://docs.cloud.coinbase.com/advanced-trade-api/docs/ws-overview).
Websockets are now available for Authenticated clients only. You must setup API
access within your [account settings](https://coinbase.com/settings/api).

#### Subscribe to a single product
```python
import cbadv

# You need to provide api key and secret others parameters are optional
wsClient = cbadv.WebsocketClient(api_key, secret_key, url="wss://advanced-trade-ws.coinbase.com",
                                products="BTC-USD",
                                channels=["ticker"])
# Do other stuff...
wsClient.close()
```

#### Subscribe to multiple products
```python
import cbadv
# You need to provide api key and secret others parameters are optional
wsClient = cbadv.WebsocketClient(api_key, secret_key, url="wss://advanced-trade-ws.coinbase.com",
                                products=["BTC-USD", "ETH-USD"],
                                channels=["ticker"])
# Do other stuff...
wsClient.close()
```

### WebsocketClient Methods
The ```WebsocketClient``` subscribes in a separate thread upon initialization.
There are three methods which you could overwrite (before initialization) so it
can react to the data streaming in.  The current client is a template used for
illustration purposes only.

- onOpen - called once, *immediately before* the socket connection is made, this
is where you want to add initial parameters.
- onMessage - called once for every message that arrives and accepts one
argument that contains the message of dict type.
- on_close - called once after the websocket has been closed.
- close - call this method to close the websocket connection (do not overwrite).
```python
import cbadv, time
class myWebsocketClient(cbadv.WebsocketClient):
    def __init__(self, apit_key, secret_key):
        super().__init__(api_key, secret_key)

    def on_open(self):
        self.url = "wss://advanced-trade-ws.coinbase.com"
        self.products = ["LTC-USD"]
        self.message_count = 0
        print("Lets count the messages!")
    def on_message(self, msg):
        self.message_count += 1
        if 'price' in msg and 'type' in msg:
            print ("Message type:", msg["type"],
                   "\t@ {:.3f}".format(float(msg["price"])))
    def on_close(self):
        print("-- Goodbye! --")

api_key = ''
secret_key = ''

wsClient = myWebsocketClient(api_key, secret_key)
#wsClient = myWebsocketClient(**json.load(open('path/to/credentials.json'))) # load from file
wsClient.start()
print(wsClient.url, wsClient.products)
while (wsClient.message_count < 500):
    print ("\nmessage_count =", "{} \n".format(wsClient.message_count))
    time.sleep(1)
wsClient.close()
```
## Testing
A test suite is under development. Tests for the authenticated client require a 
set of sandbox API credentials. To provide them, rename 
`api_config.json.example` in the tests folder to `api_config.json` and edit the 
file accordingly. To run the tests, start in the project directory and run
```
python -m pytest
```

### Real-time OrderBook

The ```OrderBook``` subscribes to a websocket and keeps a real-time record of
the orderbook for the product_id input.  Please provide your feedback for future
improvements.

```python
import cbadv, time, json

API_KEY = ''
API_SECRET = ''

order_book = cbadv.OrderBooks(api_key, api_secret, product_id=['BTC-USD', 'ETH-USD'])
order_book.start()
time.sleep(10)
order_book.close()
```

### Testing
Unit tests are under development using the pytest framework. Contributions are 
welcome!

To run the full test suite, in the project 
directory run:
```bash
python -m pytest
```

## Change Log
*2.0.0*
- Refactor project for Coinbase Advanced Trade API

*1.1.2* **Current PyPI release**
- Refactor project for Coinbase Pro
- Major overhaul on how pagination is handled

*1.0*
- The first release that is not backwards compatible
- Refactored to follow PEP 8 Standards
- Improved Documentation

*0.3*
- Added crypto and LTC deposit & withdraw (undocumented).
- Added support for Margin trading (undocumented).
- Enhanced functionality of the WebsocketClient.
- Soft launch of the OrderBook (undocumented).
- Minor bug squashing & syntax improvements.

*0.2.2*
- Added additional API functionality such as cancelAll() and ETH withdrawal.

*0.2.1*
- Allowed ```WebsocketClient``` to operate intuitively and restructured example
workflow.

*0.2.0*
- Renamed project to GDAX-Python
- Merged Websocket updates to handle errors and reconnect.

*0.1.2*
- Updated JSON handling for increased compatibility among some users.
- Added support for payment methods, reports, and Coinbase user accounts.
- Other compatibility updates.

*0.1.1b2*
- Original PyPI Release.
