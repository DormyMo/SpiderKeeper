# SpiderKeeper-2 Changelog

## 0.3.0 (2018-09-14)
- spiderkeepr was integrated into scrapyd service

## 0.2.5 (2018-09-14)
- refactoring flask application

## 0.2.0 (2017-10-26)
- SpiderKeeper was forked to Spiderkeeper-2
- Add button for removing all periodic jobs
- All tasks show stats now.
- When you run spiderkeeper under wsgi you should not use background scheduler, [see issue](https://github.com/agronholm/apscheduler/issues/160), you should run scheduler in separated process. So, scheduler was separated to own module
- Add foreign constraints to models.
- No need to create project now, all projects will be synchronized automatically with scrapyd.
- Fix bugs.