#欢迎使用 SpiderKeeper
**SpiderKeeper** 是一款基于[scrapyd](https://github.com/scrapy/scrapyd)服务的scrapy爬虫管理程序，实现了对scrapy爬虫的可视化管理，包括爬虫的启动与取消，定时抓取任务的设置和周期执行,并可对在运行爬虫的日志，运行状态进行查看。

##运行

    修改 dist/scripts/scripts.*.js
    设置 scrapyd 服务地址
    运行index.html,或将dist下文件部署至web服务器

##Build & development

    Run `grunt` for building and `grunt serve` for preview.

##Testing

    Running `grunt test` will run the unit tests with karma.
