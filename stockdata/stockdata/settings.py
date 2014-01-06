# Scrapy settings for stockdata project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'stockdata'

SPIDER_MODULES = ['stockdata.spiders']
NEWSPIDER_MODULE = 'stockdata.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'stockdata (+http://www.yourdomain.com)'
