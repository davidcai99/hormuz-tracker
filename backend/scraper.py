"""
霍尔木兹海峡船只数据抓取器
优先使用 EIA 数据，fallback 到新闻抓取
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# EIA API Key (免费申请: https://www.eia.gov/opendata/)
EIA_API_KEY = 'YOUR_EIA_API_KEY'  # 用户需要自己申请

def fetch_eia_data():
    """
    尝试从 EIA 获取石油运输数据
    EIA 有一些关于原油和石油产品运输的数据
    """
    try:
        # EIA 开放数据 API - 原油运输相关
        url = f'https://api.eia.gov/v2/petroleum/psy_supply_wkly/'
        params = {
            'api_key': EIA_API_KEY,
            'frequency': 'weekly',
            'data[0]': 'value',
            'facets[series][]': 'WCRFPUK2',
            'sort[0][column]': 'period',
            'sort[0][direction]': 'desc',
            'length': 500
        }
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'response' in data and 'data' in data['response']:
                logger.info("[EIA] Successfully fetched data")
                return data['response']['data']
        logger.warning("[EIA] No data returned or API key not set")
        return None
    except Exception as e:
        logger.error(f"[EIA] Error fetching data: {e}")
        return None

def scrape_hormuz_news():
    """
    从新闻来源抓取霍尔木兹海峡船只数据
    """
    news_data = []
    
    sources = [
        {
            'name': 'Reuters Hormuz',
            'url': 'https://www.reuters.com/search/news?blob=Hormuz+strait',
            'pattern': r'(\d+)\s*(?:vessel|ship|tanker|crude|oil).*(?:Hormuz|strait)'
        },
        {
            'name': 'Maritime Executive',
            'url': 'https://www.maritime-executive.com/?s=Hormuz',
            'pattern': r'(\d+)\s*(?:vessel|ship|tanker).*(?:Hormuz|Gulf)'
        }
    ]
    
    for source in sources:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(source['url'], headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'lxml')
                text = soup.get_text()
                
                matches = re.findall(source['pattern'], text, re.IGNORECASE)
                if matches:
                    logger.info(f"[News] Found {len(matches)} matches from {source['name']}")
                    
                    # 获取新闻标题和日期
                    articles = []
                    for article in soup.find_all('h3', limit=5):
                        title = article.get_text(strip=True)
                        articles.append(title)
                    
                    news_data.append({
                        'source': source['name'],
                        'matches': matches[:3],
                        'articles': articles
                    })
        except Exception as e:
            logger.error(f"[News] Error scraping {source['name']}: {e}")
    
    return news_data

def generate_mock_data():
    """
    生成模拟数据用于演示
    当没有真实数据源时使用
    """
    import random
    from models import insert_ship_data, get_latest_data
    
    today = datetime.now().date()
    
    # 检查今天是否已有数据
    latest = get_latest_data()
    if latest and latest['date'] == str(today):
        logger.info("[Mock] Data for today already exists")
        return latest
    
    # 生成合理的模拟数据
    # 基于实际霍尔木兹海峡日均约 15-20 艘油轮的数据
    passed = random.randint(13, 21)
    pending = random.randint(5, 12)
    
    insert_ship_data(
        date=str(today),
        passed_count=passed,
        pending_count=pending,
        source='simulation'
    )
    
    logger.info(f"[Mock] Generated data: passed={passed}, pending={pending}")
    return {'date': str(today), 'passed_count': passed, 'pending_count': pending, 'source': 'simulation'}

def fetch_and_update_data():
    """
    主函数：获取并更新数据
    """
    logger.info("[Scraper] Starting data fetch...")
    
    # 优先尝试 EIA
    eia_data = fetch_eia_data()
    if eia_data:
        logger.info("[Scraper] Using EIA data")
        # 处理 EIA 数据并存储
        # ... (根据实际 API 响应格式处理)
        return True
    
    # Fallback 到新闻抓取
    news_data = scrape_hormuz_news()
    if news_data:
        logger.info(f"[Scraper] Using news data from {len(news_data)} sources")
        # 处理新闻数据并存储
        # ... (解析新闻中的船只数量)
        return True
    
    # 最后使用模拟数据
    logger.warning("[Scraper] No real data source available, using mock data")
    generate_mock_data()
    return True

if __name__ == '__main__':
    fetch_and_update_data()
