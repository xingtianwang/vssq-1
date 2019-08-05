from . import WexinPay

if __name__ == "__main__":
    res = WexinPay().unified_order(out_trade_no='vip20170929104945Br0JUelVCO6on29',
                                   total_fee=490,
                                   body='月卡', trade_type='APP')
    print(res)
