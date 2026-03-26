"""
大众点评霸王餐自动报名脚本配置文件
"""

# ============ 滑动配置 ============
# 滑动距离比例（相对于屏幕高度）
SWIPE_DISTANCE_RATIO = 0.6
# 滑动后等待时间（秒），等待页面加载
SWIPE_WAIT_TIME = 2.0

# ============ 等待时间配置 ============
# 点击后等待时间（秒）
CLICK_WAIT_TIME = 1.5
# 报名成功后等待时间（秒）
SUCCESS_WAIT_TIME = 3.0
# 页面加载最大等待时间（秒）
PAGE_LOAD_TIMEOUT = 10

# ============ 图像识别配置 ============
# 图像识别阈值（0-1，越高越严格）
IMAGE_RECOGNITION_THRESHOLD = 0.8
# 最大滑动次数（超过后认为没有更多商品）
MAX_SWIPE_COUNT = 5
# 每页最大商品数
MAX_ITEMS_PER_PAGE = 5

# ============ 模板目录 ============
TEMPLATE_DIR = "templates"

# ============ 日志配置 ============
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
