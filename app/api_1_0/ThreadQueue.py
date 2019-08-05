#!/usr/bin/env python
# -*- coding:utf-8 -*-
# *************************************************************************
#   Copyright © 2019 Godinsec. All rights reserved.
#   File Name: QueueThread.py
#   Author: velve
#   Mail: haoliang.cui@godinsec.com
#   Created Time: 19/05/26
# *************************************************************************
import datetime
import threading
import queue
from multiprocessing.pool import ThreadPool
from app import redis
from time import sleep, time


class QueueThread:
    def __init__(self):
        self.pool = ThreadPool(50)
        self.old = int(time())
        self.limit = 50
        # FeatureApi 缓存队列
        self.fe_queue = queue.Queue(100)
        self.fe_mutex = threading.Lock()

    # FeatureApi module start
    def feature(self, data):
        self.pool.apply_async(thread_write_data, args=(self, self.fe_queue, self.fe_mutex, data, self.feature_redis))

    def feature_redis(self):
        with redis.pipeline(transaction=False) as p:
            while not self.fe_queue.empty():
                p.rpush('%s-feature' % datetime.datetime.now().date(), self.fe_queue.get(block=False))
            p.execute()

    @staticmethod
    def write_redis(mutex, func):
        if mutex.acquire(1):
            func()
            mutex.release()


# 公共写入线程 qt
def thread_write_data(qt, fe_queue, mutex, data, func):
    fe_queue.put(data)
    try:
        n = int(time())
        if n - qt.old > 120:
            qt.old = n
            # size = redis.get("featureapilimitsize")
            # if size:
            #     qt.limit = int(size)
        if fe_queue.qsize() > qt.limit:
            qt.write_redis(mutex, func)
        elif n - qt.old > 100:
            qt.write_redis(mutex, func)
    except Exception as e:
        print("thread_feature_api_write_data error " + e)


if __name__ == "__main__":
    th = QueueThread()
    for i in range(10028):
        th.feature(str(i))

    sleep(6)
