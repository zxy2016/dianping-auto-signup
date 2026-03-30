"""
大众点评霸王餐自动报名脚本配置文件
"""

# ============ 滑动配置 ============
# 滑动距离比例（相对于屏幕高度）
SWIPE_DISTANCE_RATIO = 0.6
# 滑动后等待时间（秒），等待页面加载
SWIPE_WAIT_TIME = 2.0
# 列表页大幅滑动轮数
PAGE_SCROLL_ROUNDS = (1, 2)
# 列表页每轮滚动量
PAGE_SCROLL_AMOUNT = (72, 96)
# 空页补偿滑动轮数
RECOVERY_SCROLL_ROUNDS = (2, 3)
# 空页补偿滑动量
RECOVERY_SCROLL_AMOUNT = (88, 120)
# 列表页小幅滚动量
SMALL_SCROLL_AMOUNT = (8, 14)

# ============ 等待时间配置 ============
# 点击后等待时间（秒）
CLICK_WAIT_TIME = 1.5
# 报名成功后等待时间（秒）
SUCCESS_WAIT_TIME = 3.0
# 页面加载最大等待时间（秒）
PAGE_LOAD_TIMEOUT = 10
# 列表页快速扫描超时
LIST_SCAN_TIMEOUT = 2.2
# 列表页重复位置后复扫超时
LIST_RESCAN_TIMEOUT = 1.2
# 空页补偿后的复查超时
RECOVERY_SCAN_TIMEOUT = 3.0

# ============ 图像识别配置 ============
# 图像识别阈值（0-1，越高越严格）
IMAGE_RECOGNITION_THRESHOLD = 0.8
# 最大滑动次数（超过后认为没有更多商品）
MAX_SWIPE_COUNT = 20
# 每页最大商品数
MAX_ITEMS_PER_PAGE = 5
# 连续多少个空页后才停止，避免快速扫描误判
MAX_CONSECUTIVE_EMPTY_PAGES = 4
# 列表页快速扫描轮询间隔
FIND_RETRY_INTERVAL = 0.25

# ============ 模板目录 ============
TEMPLATE_DIR = "templates"

# ============ 日志配置 ============
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
