# cbadv.abadv_client.py
# original author: Tony Denion
#
#
# Coinbase Advanced Trade API Client

import requests
import json

from cbadv.cbadv_auth import CBAdvAuth

class Client:
    """ Provides access to Endpoints on the coinbase advanced trade API.

    All requests default to the live `api_url`: 'https://api.coinbase.com'.
    To test your application using the sandbox modify the `api_url`.

    Attributes:
        url (str): The api url for this client instance to use.
        auth (CBAdvAuth): Custom authentication handler for each request.
        session (requests.Session): Persistent HTTP connection object.
    """
    def __init__(self, api_key=None, api_secret=None, api_url='https://api.coinbase.com/api/v3/brokerage'):
        """ Initializes a Client instance.
        
        Args:
            api_key (str): Your coinbase advanced trade API key.
            api_secret (str): Your coinbase advanced trade API secret.
            api_url (str): The api url for this client instance to use.
        """
        self.url = api_url
        self.auth = CBAdvAuth(api_key, api_secret)
        self.session = requests.Session()

    def list_accounts(self):
        """ List accounts.

        Returns:
            list of dict: JSON response
            {
                "accounts": {
                    "uuid": "8bfc20d7-f7c6-4422-bf07-8243ca4169fe",
                    "name": "BTC Wallet",
                    "currency": "BTC",
                    "available_balance": {
                    "value": "1.23",
                    "currency": "BTC"
                    },
                    "default": false,
                    "active": true,
                    "created_at": "2021-05-31T09:59:59Z",
                    "updated_at": "2021-05-31T09:59:59Z",
                    "deleted_at": "2021-05-31T09:59:59Z",
                    "type": "ACCOUNT_TYPE_UNSPECIFIED",
                    "ready": true,
                    "hold": {
                    "value": "1.23",
                    "currency": "BTC"
                    }
                },
                "has_next": true,
                "cursor": "789100",
                "size": "integer"
            }

        """
        return self._send_message('GET', '/accounts')

    def get_account(self, account_id):
        """ Get account.

        Args:
            account_id (str): Account ID

        Returns:
            dict: JSON response
            {
                "account": {
                    "uuid": "8bfc20d7-f7c6-4422-bf07-8243ca4169fe",
                    "name": "BTC Wallet",
                    "currency": "BTC",
                    "available_balance": {
                        "value": "1.23",
                        "currency": "BTC"
                    },
                    "default": false,
                    "active": true,
                    "created_at": "2021-05-31T09:59:59Z",
                    "updated_at": "2021-05-31T09:59:59Z",
                    "deleted_at": "2021-05-31T09:59:59Z",
                    "type": "ACCOUNT_TYPE_UNSPECIFIED",
                    "ready": true,
                    "hold": {
                        "value": "1.23",
                        "currency": "BTC"
                    }
                }
            }

        """
        return self._send_message('GET', '/accounts/' + account_id)

    def create_order(self, product_id, side, order_type=None, **kwargs):
        """ Create order.

        Args:
            order (dict): Order object
            {
                "account_id": "8bfc20d7-f7c6-4422-bf07-8243ca4169fe",
                "type": "ORDER_TYPE_UNSPECIFIED",
                "side": "ORDER_SIDE_UNSPECIFIED",
                "product_id": "BTC-USD",
                "client_oid": "string",
                "stop": "string",
                "stop_price": {
                    "value": "1.23",
                    "currency": "BTC"
                },
                "funds": {
                    "value": "1.23",
                    "currency": "BTC"
                },
                "size": {
                    "value": "1.23",
                    "currency": "BTC"
                },
                "time_in_force": "TIME_IN_FORCE_UNSPECIFIED",
                "post_only": true,
                "cancel_after": "TIME_IN_FORCE_UNSPECIFIED",
                "self_trade_prevention": "SELF_TRADE_PREVENTION_UNSPECIFIED",
                "client_id": "string",
                "stp": "SELF_TRADE_PREVENTION_UNSPECIFIED"
            }

        Returns:
            dict: JSON response
            {
                "success": true,
                "failure_reason": "string",
                "order_id": "string",
                "success_response": {
                    "order_id": "11111-00000-000000",
                    "product_id": "BTC-USD",
                    "side": "UNKNOWN_ORDER_SIDE",
                    "client_order_id": "0000-00000-000000"
                },
                "error_response": {
                    "error": "UNKNOWN_FAILURE_REASON",
                    "message": "The order configuration was invalid",
                    "error_details": "Market orders cannot be placed with empty order sizes",
                    "preview_failure_reason": "UNKNOWN_PREVIEW_FAILURE_REASON",
                    "new_order_failure_reason": "UNKNOWN_FAILURE_REASON"
                },
                "order_configuration": {
                    "market_market_ioc": {
                        "quote_size": "10.00",
                        "base_size": "0.001"
                    },
                    "limit_limit_gtc": {
                        "base_size": "0.001",
                        "limit_price": "10000.00",
                        "post_only": false
                    },
                    "limit_limit_gtd": {
                        "base_size": "0.001",
                        "limit_price": "10000.00",
                        "end_time": "2021-05-31T09:59:59Z",
                        "post_only": false
                    },
                    "stop_limit_stop_limit_gtc": {
                        "base_size": "0.001",
                        "limit_price": "10000.00",
                        "stop_price": "20000.00",
                        "stop_direction": "UNKNOWN_STOP_DIRECTION"
                    },
                    "stop_limit_stop_limit_gtd": {
                        "base_size": 0.001,
                        "limit_price": "10000.00",
                        "stop_price": "20000.00",
                        "end_time": "2021-05-31T09:59:59Z",
                        "stop_direction": "UNKNOWN_STOP_DIRECTION"
                    }
                }
            }

        """
        # Margin parameter checks
        if kwargs.get('overdraft_enabled') is not None and \
                kwargs.get('funding_amount') is not None:
            raise ValueError('Margin funding must be specified through use of '
                             'overdraft or by setting a funding amount, but not'
                             ' both')

        # Limit order checks
        if order_type == 'limit':
            if kwargs.get('cancel_after') is not None and \
                    kwargs.get('time_in_force') != 'GTT':
                raise ValueError('May only specify a cancel period when time '
                                 'in_force is `GTT`')
            if kwargs.get('post_only') is not None and kwargs.get('time_in_force') in \
                    ['IOC', 'FOK']:
                raise ValueError('post_only is invalid when time in force is '
                                 '`IOC` or `FOK`')

        # Market and stop order checks
        if order_type == 'market' or kwargs.get('stop'):
            if not (kwargs.get('size') is None) ^ (kwargs.get('funds') is None):
                raise ValueError('Either `size` or `funds` must be specified '
                                 'for market/stop orders (but not both).')

        # Build params dict
        params = {'product_id': product_id,
                  'side': side,
                  'type': order_type}
        params.update(kwargs)

        return self._send_message('POST', '/orders', data=json.dumps(params))

    def buy(self, product_id, order_type, **kwargs):
        """Place a buy order.

        This is included to maintain backwards compatibility with older versions
        of cbpro-Python. For maximum support from docstrings and function
        signatures see the order type-specific functions place_limit_order,
        place_market_order, and place_stop_order.

        Args:
            product_id (str): Product to order (eg. 'BTC-USD')
            order_type (str): Order type ('limit', 'market', or 'stop')
            **kwargs: Additional arguments can be specified for different order
                types.

        Returns:
            dict: Order details. See `create_order` for example.

        """
        return self.create_order(product_id, 'buy', order_type, **kwargs)

    def sell(self, product_id, order_type, **kwargs):
        """Place a sell order.

        This is included to maintain backwards compatibility with older versions
        of cbpro-Python. For maximum support from docstrings and function
        signatures see the order type-specific functions place_limit_order,
        place_market_order, and place_stop_order.

        Args:
            product_id (str): Product to order (eg. 'BTC-USD')
            order_type (str): Order type ('limit', 'market', or 'stop')
            **kwargs: Additional arguments can be specified for different order
                types.

        Returns:
            dict: Order details. See `create_order` for example.

        """
        return self.create_order(product_id, 'sell', order_type, **kwargs)

    def place_limit_order(self, product_id, side, price, size,
                          client_oid=None,
                          stp=None,
                          time_in_force=None,
                          cancel_after=None,
                          post_only=None,
                          overdraft_enabled=None,
                          funding_amount=None):
        """Place a limit order.

        Args:
            product_id (str): Product to order (eg. 'BTC-USD')
            side (str): Order side ('buy' or 'sell)
            price (Decimal): Price per cryptocurrency
            size (Decimal): Amount of cryptocurrency to buy or sell
            client_oid (Optional[str]): User-specified Order ID
            stp (Optional[str]): Self-trade prevention flag. See `create_order`
                for details.
            time_in_force (Optional[str]): Time in force. Options:
                'GTC'   Good till canceled
                'GTT'   Good till time (set by `cancel_after`)
                'IOC'   Immediate or cancel
                'FOK'   Fill or kill
            cancel_after (Optional[str]): Cancel after this period for 'GTT'
                orders. Options are 'min', 'hour', or 'day'.
            post_only (Optional[bool]): Indicates that the order should only
                make liquidity. If any part of the order results in taking
                liquidity, the order will be rejected and no part of it will
                execute.
            overdraft_enabled (Optional[bool]): If true funding above and
                beyond the account balance will be provided by margin, as
                necessary.
            funding_amount (Optional[Decimal]): Amount of margin funding to be
                provided for the order. Mutually exclusive with
                `overdraft_enabled`.

        Returns:
            dict: Order details. See `create_order` for example.

        """
        params = {'product_id': product_id,
                  'side': side,
                  'order_type': 'limit',
                  'price': price,
                  'size': size,
                  'client_oid': client_oid,
                  'stp': stp,
                  'time_in_force': time_in_force,
                  'cancel_after': cancel_after,
                  'post_only': post_only,
                  'overdraft_enabled': overdraft_enabled,
                  'funding_amount': funding_amount}
        params = dict((k, v) for k, v in params.items() if v is not None)

        return self.create_order(**params)

    def place_market_order(self, product_id, side, size=None, funds=None,
                           client_oid=None,
                           stp=None,
                           overdraft_enabled=None,
                           funding_amount=None):
        """ Place market order.

        Args:
            product_id (str): Product to order (eg. 'BTC-USD')
            side (str): Order side ('buy' or 'sell)
            size (Optional[Decimal]): Desired amount in crypto. Specify this or
                `funds`.
            funds (Optional[Decimal]): Desired amount of quote currency to use.
                Specify this or `size`.
            client_oid (Optional[str]): User-specified Order ID
            stp (Optional[str]): Self-trade prevention flag. See `create_order`
                for details.
            overdraft_enabled (Optional[bool]): If true funding above and
                beyond the account balance will be provided by margin, as
                necessary.
            funding_amount (Optional[Decimal]): Amount of margin funding to be
                provided for the order. Mutually exclusive with
                `overdraft_enabled`.

        Returns:
            dict: Order details. See `create_order` for example.

        """
        params = {'product_id': product_id,
                  'side': side,
                  'order_type': 'market',
                  'size': size,
                  'funds': funds,
                  'client_oid': client_oid,
                  'stp': stp,
                  'overdraft_enabled': overdraft_enabled,
                  'funding_amount': funding_amount}
        params = dict((k, v) for k, v in params.items() if v is not None)

        return self.create_order(**params)

    def place_stop_order(self, product_id, stop_type, price, size=None, funds=None,
                         client_oid=None,
                         stp=None,
                         overdraft_enabled=None,
                         funding_amount=None):
        """ Place stop order.

        Args:
            product_id (str): Product to order (eg. 'BTC-USD')
            stop_type(str): Stop type ('entry' or 'loss')
                      loss: Triggers when the last trade price changes to a value at or below the stop_price.
                      entry: Triggers when the last trade price changes to a value at or above the stop_price
            price (Decimal): Desired price at which the stop order triggers.
            size (Optional[Decimal]): Desired amount in crypto. Specify this or
                `funds`.
            funds (Optional[Decimal]): Desired amount of quote currency to use.
                Specify this or `size`.
            client_oid (Optional[str]): User-specified Order ID
            stp (Optional[str]): Self-trade prevention flag. See `create_order`
                for details.
            overdraft_enabled (Optional[bool]): If true funding above and
                beyond the account balance will be provided by margin, as
                necessary.
            funding_amount (Optional[Decimal]): Amount of margin funding to be
                provided for the order. Mutually exclusive with
                `overdraft_enabled`.

        Returns:
            dict: Order details. See `create_order` for example.

        """

        if stop_type == 'loss':
            side = 'sell'
        elif stop_type == 'entry':
            side = 'buy'
        else:
            raise ValueError('Invalid stop_type for stop order: ' + stop_type)

        params = {'product_id': product_id,
                  'side': side,
                  'price': price,
                  'order_type': None,
                  'stop': stop_type,
                  'stop_price': price,
                  'size': size,
                  'funds': funds,
                  'client_oid': client_oid,
                  'stp': stp,
                  'overdraft_enabled': overdraft_enabled,
                  'funding_amount': funding_amount}
        params = dict((k, v) for k, v in params.items() if v is not None)

        return self.create_order(**params)

    def cancel_orders(self, order_ids):
        """ Cancel orders.

        Args:
            order_ids (list): List of order IDs

        Returns:
            dict: JSON response
            {
                "results": {
                    "success": true,
                    "failure_reason": "UNKNOWN_CANCEL_FAILURE_REASON",
                    "order_id": "0000-00000"
                }
            }

        """
        return self._send_message('POST', '/orders/batch_cancel', data=json.dumps(order_ids))

    def list_orders(self):
        """ List orders.

        Returns:
            dict: JSON response
            {
                "orders": {
                    "order_id": "0000-000000-000000",
                    "product_id": "BTC-USD",
                    "user_id": "2222-000000-000000",
                    "order_configuration": {
                    "market_market_ioc": {
                        "quote_size": "10.00",
                        "base_size": "0.001"
                    },
                    "limit_limit_gtc": {
                        "base_size": "0.001",
                        "limit_price": "10000.00",
                        "post_only": false
                    },
                    "limit_limit_gtd": {
                        "base_size": "0.001",
                        "limit_price": "10000.00",
                        "end_time": "2021-05-31T09:59:59Z",
                        "post_only": false
                    },
                    "stop_limit_stop_limit_gtc": {
                        "base_size": "0.001",
                        "limit_price": "10000.00",
                        "stop_price": "20000.00",
                        "stop_direction": "UNKNOWN_STOP_DIRECTION"
                    },
                    "stop_limit_stop_limit_gtd": {
                        "base_size": 0.001,
                        "limit_price": "10000.00",
                        "stop_price": "20000.00",
                        "end_time": "2021-05-31T09:59:59Z",
                        "stop_direction": "UNKNOWN_STOP_DIRECTION"
                    }
                    },
                    "side": "UNKNOWN_ORDER_SIDE",
                    "client_order_id": "11111-000000-000000",
                    "status": "OPEN",
                    "time_in_force": "UNKNOWN_TIME_IN_FORCE",
                    "created_time": "2021-05-31T09:59:59Z",
                    "completion_percentage": "50",
                    "filled_size": "0.001",
                    "average_filled_price": "50",
                    "fee": "string",
                    "number_of_fills": "2",
                    "filled_value": "10000",
                    "pending_cancel": true,
                    "size_in_quote": false,
                    "total_fees": "5.00",
                    "size_inclusive_of_fees": false,
                    "total_value_after_fees": "string",
                    "trigger_status": "UNKNOWN_TRIGGER_STATUS",
                    "order_type": "UNKNOWN_ORDER_TYPE",
                    "reject_reason": "REJECT_REASON_UNSPECIFIED",
                    "settled": "boolean",
                    "product_type": "SPOT",
                    "reject_message": "string",
                    "cancel_message": "string"
                },
                "sequence": "string",
                "has_next": true,
                "cursor": "789100"
            }
        """
        return self._send_message('GET', '/orders/historical/batch')

    def list_fills(self):
        """ List fills.

        Returns:
            dict: JSON response
            {
                "fills": {
                    "entry_id": "22222-2222222-22222222",
                    "trade_id": "1111-11111-111111",
                    "order_id": "0000-000000-000000",
                    "trade_time": "2021-05-31T09:59:59Z",
                    "trade_type": "FILL",
                    "price": "10000.00",
                    "size": "0.001",
                    "commission": "1.25",
                    "product_id": "BTC-USD",
                    "sequence_timestamp": "2021-05-31T09:58:59Z",
                    "liquidity_indicator": "UNKNOWN_LIQUIDITY_INDICATOR",
                    "size_in_quote": false,
                    "user_id": "3333-333333-3333333",
                    "side": "UNKNOWN_ORDER_SIDE"
                },
                "cursor": "789100"
            }
        """
        return self._send_message('GET', '/orders/historical/fills')

    def get_order(self, order_id):
        """ Get order.

        Args:
            order_id (str): Order ID

        Returns:
            dict: JSON response
            {
                "order": {
                        "order_id": "0000-000000-000000",
                        "product_id": "BTC-USD",
                        "user_id": "2222-000000-000000",
                        "order_configuration": {
                        "market_market_ioc": {
                            "quote_size": "10.00",
                            "base_size": "0.001"
                        },
                        "limit_limit_gtc": {
                            "base_size": "0.001",
                            "limit_price": "10000.00",
                            "post_only": false
                        },
                        "limit_limit_gtd": {
                            "base_size": "0.001",
                            "limit_price": "10000.00",
                            "end_time": "2021-05-31T09:59:59Z",
                            "post_only": false
                        },
                        "stop_limit_stop_limit_gtc": {
                            "base_size": "0.001",
                            "limit_price": "10000.00",
                            "stop_price": "20000.00",
                            "stop_direction": "UNKNOWN_STOP_DIRECTION"
                        },
                        "stop_limit_stop_limit_gtd": {
                            "base_size": 0.001,
                            "limit_price": "10000.00",
                            "stop_price": "20000.00",
                            "end_time": "2021-05-31T09:59:59Z",
                            "stop_direction": "UNKNOWN_STOP_DIRECTION"
                        }
                    },
                    "side": "UNKNOWN_ORDER_SIDE",
                    "client_order_id": "11111-000000-000000",
                    "status": "OPEN",
                    "time_in_force": "UNKNOWN_TIME_IN_FORCE",
                    "created_time": "2021-05-31T09:59:59Z",
                    "completion_percentage": "50",
                    "filled_size": "0.001",
                    "average_filled_price": "50",
                    "fee": "string",
                    "number_of_fills": "2",
                    "filled_value": "10000",
                    "pending_cancel": true,
                    "size_in_quote": false,
                    "total_fees": "5.00",
                    "size_inclusive_of_fees": false,
                    "total_value_after_fees": "string",
                    "trigger_status": "UNKNOWN_TRIGGER_STATUS",
                    "order_type": "UNKNOWN_ORDER_TYPE",
                    "reject_reason": "REJECT_REASON_UNSPECIFIED",
                    "settled": "boolean",
                    "product_type": "SPOT",
                    "reject_message": "string",
                    "cancel_message": "string"
                }
                
        """
        return self._send_message('GET', '/orders/historical/' + order_id)

    def list_products(self):
        """ List products.

        Returns:
            list of dicts: JSON response
            {
                "products": {
                    "product_id": "BTC-USD",
                    "price": "140.21",
                    "price_percentage_change_24h": "9.43%",
                    "volume_24h": "1908432",
                    "volume_percentage_change_24h": "9.43%",
                    "base_increment": "0.00000001",
                    "quote_increment": "0.00000001",
                    "quote_min_size": "0.00000001",
                    "quote_max_size": "1000",
                    "base_min_size": "0.00000001",
                    "base_max_size": "1000",
                    "base_name": "Bitcoin",
                    "quote_name": "US Dollar",
                    "watched": true,
                    "is_disabled": false,
                    "new": true,
                    "status": "string",
                    "cancel_only": true,
                    "limit_only": true,
                    "post_only": true,
                    "trading_disabled": false,
                    "auction_mode": true,
                    "product_type": "SPOT",
                    "quote_currency_id": "USD",
                    "base_currency_id": "BTC",
                    "mid_market_price": "140.22"
                },
                "num_products": 100
            }
        """
        return self._send_message('GET', '/products')

    def get_product(self, product_id):
        """ Get product.

        Args:
            product_id (str): Product ID

        Returns:
            dict: JSON response
            {
                "product_id": "BTC-USD",
                "price": "140.21",
                "price_percentage_change_24h": "9.43%",
                "volume_24h": "1908432",
                "volume_percentage_change_24h": "9.43%",
                "base_increment": "0.00000001",
                "quote_increment": "0.00000001",
                "quote_min_size": "0.00000001",
                "quote_max_size": "1000",
                "base_min_size": "0.00000001",
                "base_max_size": "1000",
                "base_name": "Bitcoin",
                "quote_name": "US Dollar",
                "watched": true,
                "is_disabled": false,
                "new": true,
                "status": "string",
                "cancel_only": true,
                "limit_only": true,
                "post_only": true,
                "trading_disabled": false,
                "auction_mode": true,
                "product_type": "SPOT",
                "quote_currency_id": "USD",
                "base_currency_id": "BTC",
                "mid_market_price": "140.22"
            }
        """
        return self._send_message('GET', '/products/' + product_id)

    def get_product_candles(self, product_id, start, end, granularity):
        """ Get product candles.

        Args:
            product_id (str): Product ID
            start (str): Start time
            end (str): End time
            granularity (str): Granularity

        Returns:
            list of dicts: JSON response
            [
                "candles": {
                    "start": "1639508050",
                    "low": "140.21",
                    "high": "140.21",
                    "open": "140.21",
                    "close": "140.21",
                    "volume": "56437345"
                }
            ]
        """
        params = {
            'start': start,
            'end': end,
            'granularity': granularity
        }
        return self._send_message('GET', '/products/' + product_id + '/candles',
                                  params=params)

    def get_market_trades(self, product_id, limit="10000"):
        """ Get market trades.

        Args:
            product_id (str): Product ID

        Returns:
            list of dicts: JSON response
            [
                "trades": {
                    "trade_id": "34b080bf-fcfd-445a-832b-46b5ddc65601",
                    "product_id": "BTC-USD",
                    "price": "140.91",
                    "size": "4",
                    "time": "2021-05-31T09:59:59Z",
                    "side": "UNKNOWN_ORDER_SIDE",
                    "bid": "291.13",
                    "ask": "292.40"
                }
            ]
        """
        params = {
            'limit': limit
        }
        return self._send_message('GET', '/products/' + product_id + '/trades',
                                  params=params)

    def get_transactions_summary(self, start_date, end_date, user_native_currency='USD'):
        """ Get transactions summary.

        Returns:
            dict: JSON response
            {
                "total_volume": 1000,
                "total_fees": 25,
                "fee_tier": {
                    "pricing_tier": "<$10k",
                    "usd_from": "0",
                    "usd_to": "10,000",
                    "taker_fee_rate": "0.0010",
                    "maker_fee_rate": "0.0020"
                },
                "margin_rate": {
                    "value": "string"
                },
                "goods_and_services_tax": {
                    "rate": "string",
                    "type": "INCLUSIVE"
                },
                "advanced_trade_only_volume": 1000,
                "advanced_trade_only_fees": 25,
                "coinbase_pro_volume": 1000,
                "coinbase_pro_fees": 25
            }
        """
        params = {
            'start_date': start_date,
            'end_date': end_date,
            'user_native_currency': user_native_currency
        }
        return self._send_message('GET', '/transactions_summary', params=params)

    def _send_message(self, method, endpoint, params=None, data=None):
        """Send API request.

        Args:
            method (str): HTTP method (get, post, delete, etc.)
            endpoint (str): Endpoint (to be added to base URL)
            params (Optional[dict]): HTTP request parameters
            data (Optional[str]): JSON-encoded string payload for POST

        Returns:
            dict/list: JSON response

        """
        url = self.url + endpoint
        r = self.session.request(method, url, params=params, data=data,
                                 auth=self.auth, timeout=30)
        return r.json()