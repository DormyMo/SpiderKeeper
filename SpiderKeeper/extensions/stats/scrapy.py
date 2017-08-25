#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time      : 2017-04-30 18:19
# @Author    : modm
import datetime
from scrapy.statscollectors import StatsCollector


class SpiderKeeperStatsCollector(StatsCollector):
    """
        post stats data to spiderkeeper
    """

    def __init__(self, crawler):
        super(SpiderKeeperStatsCollector, self).__init__(crawler)

    def _persist_stats(self, stats, spider):
        self.spider_stats[spider.name] = stats

    def open_spider(self, spider):
        import socket;
        super(SpiderKeeperStatsCollector, self).open_spider(spider)
        if hasattr(spider, '_job'):
            _job = spider._job
            spider_name = spider.name
            job_id = _job
            args = ''
            start_time = datetime.datetime.now()
            daemon = socket.gethostname()

    def close_spider(self, spider, reason):
        if hasattr(spider, '_job'):
            _job = spider._job
            job_id = _job
            request_count = self._stats.get('downloader/request_count', 0)
            response_count = self._stats.get('downloader/response_count', 0)
            item_count = self._stats.get('item_scraped_count', 0)
            finishe_time = datetime.datetime.now()
            error_count = self._stats.get('log_count/ERROR', 0)
            finishe_reason = reason
