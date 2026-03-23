"""
霍尔木兹海峡船只追踪器 - Flask 后端
"""

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from datetime import datetime, timedelta
import models
from scraper import fetch_and_update_data
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

app = Flask(__name__, static_folder='../frontend', template_folder='../frontend')
CORS(app)

# 初始化数据库
models.init_db()

# 配置定时任务
scheduler = BackgroundScheduler()
scheduler.add_job(func=fetch_and_update_data, trigger='interval', hours=6, id='fetch_data')
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

# 首次启动时后台获取数据（不阻塞服务启动）
import threading
threading.Thread(target=fetch_and_update_data, daemon=True).start()

@app.route('/')
def index():
    """返回前端页面"""
    # 记录访问
    ip = request.remote_addr or request.headers.get('X-Forwarded-For', 'unknown')
    ua = request.headers.get('User-Agent', '')[:200]
    models.record_visit(ip, ua)
    return render_template('index.html')

@app.route('/api/latest')
def api_latest():
    """获取最新船只数据"""
    data = models.get_latest_data()
    if data:
        return jsonify({
            'success': True,
            'data': data
        })
    return jsonify({
        'success': False,
        'message': 'No data available'
    })

@app.route('/api/history')
def api_history():
    """获取历史数据"""
    days = request.args.get('days', 30, type=int)
    data = models.get_historical_data(days)
    return jsonify({
        'success': True,
        'data': data
    })

@app.route('/api/stats')
def api_stats():
    """获取访问统计"""
    return jsonify({
        'success': True,
        'data': {
            'total_views': models.get_total_views(),
            'unique_visitors': models.get_unique_visitors()
        }
    })

@app.route('/api/refresh', methods=['POST'])
def api_refresh():
    """手动触发数据更新"""
    success = fetch_and_update_data()
    return jsonify({
        'success': success,
        'message': 'Data refreshed' if success else 'Refresh failed'
    })

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
