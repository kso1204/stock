import pyupbit
import matplotlib.pyplot as plt
import time
import pandas as pd
import sys, io
from module import upbit


sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def short_trading_for_1percent(ticker):
    dfs = [ ]
    df = pyupbit.get_ohlcv(ticker, interval="minute1", to="20210414 23:00:00")
    print(df)
    dfs.append(df)

    for i in range(60):
        df = pyupbit.get_ohlcv(ticker, interval="minute1", to=df.index[0])
        dfs.append(df)
        time.sleep(0.2)

    df = pd.concat(dfs)
    df = df.sort_index()

    # df['close'].plot()
    # plt.show()

    # 1) 매수 일자 판별
    cond = df['high'] >= df['open'] * 1.01

    acc_ror = 1
    sell_date = None

    # 2) 매도 조건 탐색 및 수익률 계산
    for buy_date in df.index[cond]:
        if sell_date != None and buy_date <= sell_date:
            continue

        target = df.loc[ buy_date :  ]

        cond = target['high'] >= target['open'] * 1.02
        sell_candidate = target.index[cond]

        if len(sell_candidate) == 0:
            buy_price = df.loc[buy_date, 'open'] * 1.01
            sell_price = df.iloc[-1, 3]
            acc_ror *= (sell_price / buy_price)
            break
        else:
            sell_date = sell_candidate[0]
            acc_ror *= 1.005
            # 수수료 0.001 + 슬리피지 0.004

    return acc_ror


import os
import sys
import logging
import math
import traceback
 
# 공통 모듈 Import
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
 
# 여러 코인에 대해 get_macd 함수를 호출하고, 최종 자본금이 가장 높은 상위 10개를 선택하는 코드
def get_top_10_coins(coins, tick_kind, inq_range):
    results = []
    for coin in coins:
        result = upbit.get_macd(coin, tick_kind, inq_range)
        results.append(result)

    # 최종 자본금이 가장 높은 상위 10개 선택
    top_10 = sorted(results, key=lambda x: x['final_capital'], reverse=True)[:10]

    return top_10

def get_buy_macd(coins, tick_kind, inq_range):
    try:
        best_trades = []

        best_trade = None
        best_ocl_change = float('-inf')

        for coin in coins:
            result = upbit.get_macd2(coin, tick_kind, inq_range)

            print(result)

            trades = result['trades']

            for trade in trades[-1:]:
                if trade['type'] == 'buy' and trade['ocl_change'] > best_ocl_change:
                    best_ocl_change = trade['ocl_change']
                    best_trade = {
                        "coin": coin,
                        "date": trade['date'],
                        "price": trade['price'],
                        "quantity": trade['quantity'],
                        "ocl_change": trade['ocl_change']
                    }

            if best_trade:
                best_trades.append(best_trade)

        return best_trades

    except Exception as e:
        print(f"Error: {e}")
        raise

# -----------------------------------------------------------------------------
# - Name : main
# - Desc : 메인
# -----------------------------------------------------------------------------
if __name__ == '__main__':
 
    # noinspection PyBroadException
    try:
 
        print("***** USAGE ******")
        print("[1] 로그레벨(D:DEBUG, E:ERROR, 그외:INFO)")
 
        # 로그레벨(D:DEBUG, E:ERROR, 그외:INFO)
        upbit.set_loglevel('I')
 
        # ---------------------------------------------------------------------
        # Logic Start!
        # ---------------------------------------------------------------------
        # 보유 종목 리스트 조회
        #rsi_data = upbit.get_rsi('KRW-BTC', '3', '200')
        #logging.info(rsi_data)
        
        tickers = pyupbit.get_tickers('KRW')

        print(len(tickers))
        
        tickers = tickers[:3]

        best_buy_trades = get_buy_macd(tickers, '60', 10)
        for trade in best_buy_trades:
            print(trade)


        #for ticker in tickers:
        # print(get_top_10_coins(tickers, '60', '100'))

        #    rsi_data = upbit.get_rsi(ticker, '60', '100')
        #    print(ticker, rsi_data)
 
 
    except KeyboardInterrupt:
        logging.error("KeyboardInterrupt Exception 발생!")
        logging.error(traceback.format_exc())
        sys.exit(1)
 
    except Exception:
        logging.error("Exception 발생!")
        logging.error(traceback.format_exc())
        sys.exit(1)

# for ticker in ["KRW-BTC"]:
#     #ror = short_trading_for_1percent(ticker)
#     #print(ticker, ror)
#     rsi = calculate_rsi(ticker)
#     print(ticker, rsi)