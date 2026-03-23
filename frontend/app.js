// 霍尔木兹海峡船只追踪器 - 前端脚本

let comparisonChart = null;
let historyChart = null;

// 检查服务是否已唤醒
async function waitForService(maxRetries = 15, interval = 1000) {
    for (let i = 0; i < maxRetries; i++) {
        try {
            const response = await fetch('/api/stats', { 
                signal: AbortSignal.timeout(5000)
            });
            if (response.ok) return true;
        } catch (e) {
            // 服务还在唤醒中，等待...
        }
        await new Promise(r => setTimeout(r, interval));
    }
    return false;
}

// 初始化
document.addEventListener('DOMContentLoaded', async () => {
    // 先等待服务唤醒（Render免费版会休眠）
    document.getElementById('lastUpdate').textContent = '服务唤醒中，请稍候...';
    const isReady = await waitForService();
    
    if (isReady) {
        loadLatestData();
        loadHistoryData();
        loadStats();
        
        // 每30秒自动刷新
        setInterval(() => {
            loadLatestData();
            loadStats();
        }, 30000);
    } else {
        document.getElementById('lastUpdate').textContent = '服务唤醒超时，请刷新重试';
    }
});

// 加载最新数据
async function loadLatestData() {
    try {
        const response = await fetch('/api/latest', {
            signal: AbortSignal.timeout(15000)
        });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const result = await response.json();
        
        if (result.success) {
            const data = result.data;
            
            document.getElementById('passedCount').textContent = data.passed_count ?? '--';
            document.getElementById('pendingCount').textContent = data.pending_count ?? '--';
            document.getElementById('lastUpdate').textContent = data.date 
                ? new Date(data.date).toLocaleDateString('zh-CN', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                  })
                : '暂无数据';
            
            if (data.passed_count != null && data.pending_count != null) {
                updateComparisonChart(data.passed_count, data.pending_count);
            }
        } else {
            document.getElementById('lastUpdate').textContent = '数据加载失败';
        }
    } catch (error) {
        console.error('Error loading latest data:', error);
        document.getElementById('lastUpdate').textContent = '网络错误，请刷新重试';
    }
}

// 加载历史数据
async function loadHistoryData() {
    try {
        const response = await fetch('/api/history?days=14', {
            signal: AbortSignal.timeout(15000)
        });
        const result = await response.json();
        
        if (result.success && result.data.length > 0) {
            updateHistoryChart(result.data.reverse());
        }
    } catch (error) {
        console.error('Error loading history data:', error);
    }
}

// 加载统计
async function loadStats() {
    try {
        const response = await fetch('/api/stats', {
            signal: AbortSignal.timeout(15000)
        });
        const result = await response.json();
        
        if (result.success) {
            document.getElementById('totalViews').textContent = result.data.total_views;
            document.getElementById('uniqueVisitors').textContent = result.data.unique_visitors;
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// 更新对比图表
function updateComparisonChart(passed, pending) {
    const ctx = document.getElementById('comparisonChart').getContext('2d');
    
    if (comparisonChart) {
        comparisonChart.data.datasets[0].data = [passed, pending];
        comparisonChart.update();
    } else {
        comparisonChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['已通过', '待通过'],
                datasets: [{
                    label: '船只数量',
                    data: [passed, pending],
                    backgroundColor: [
                        'rgba(0, 255, 136, 0.7)',
                        'rgba(255, 217, 61, 0.7)'
                    ],
                    borderColor: [
                        '#00ff88',
                        '#ffd93d'
                    ],
                    borderWidth: 2,
                    borderRadius: 10
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        padding: 12,
                        displayColors: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: '#8892b0'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            color: '#ccd6f6',
                            font: {
                                size: 14
                            }
                        }
                    }
                }
            }
        });
    }
}

// 更新历史趋势图
function updateHistoryChart(historyData) {
    const ctx = document.getElementById('historyChart').getContext('2d');
    
    const labels = historyData.map(d => {
        const date = new Date(d.date);
        return `${date.getMonth() + 1}/${date.getDate()}`;
    });
    
    const passedData = historyData.map(d => d.passed_count);
    const pendingData = historyData.map(d => d.pending_count);
    
    if (historyChart) {
        historyChart.destroy();
    }
    
    historyChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: '已通过',
                    data: passedData,
                    borderColor: '#00ff88',
                    backgroundColor: 'rgba(0, 255, 136, 0.1)',
                    fill: true,
                    tension: 0.4,
                    pointRadius: 4,
                    pointHoverRadius: 6
                },
                {
                    label: '待通过',
                    data: pendingData,
                    borderColor: '#ffd93d',
                    backgroundColor: 'rgba(255, 217, 61, 0.1)',
                    fill: true,
                    tension: 0.4,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                legend: {
                    labels: {
                        color: '#ccd6f6',
                        usePointStyle: true,
                        padding: 20
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    padding: 12
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#8892b0'
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)'
                    },
                    ticks: {
                        color: '#8892b0'
                    }
                }
            }
        }
    });
}

// 手动刷新数据
async function refreshData() {
    const btn = document.querySelector('.refresh-btn');
    btn.textContent = '⏳ 刷新中...';
    btn.disabled = true;
    
    try {
        const response = await fetch('/api/refresh', { 
            method: 'POST',
            signal: AbortSignal.timeout(30000)
        });
        const result = await response.json();
        
        if (result.success) {
            await loadLatestData();
            await loadHistoryData();
            await loadStats();
        }
    } catch (error) {
        console.error('Error refreshing data:', error);
    } finally {
        btn.textContent = '🔄 刷新数据';
        btn.disabled = false;
    }
}
