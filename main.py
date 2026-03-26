"""
大众点评霸王餐自动报名脚本

使用 OpenCV 图像识别 + pyautogui 实现自动点击报名
适用于 Mac 镜像模式
"""

import logging
import time
from pathlib import Path

import cv2
import numpy as np
import pyautogui
from PIL import Image

import config

# 配置日志
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT,
)
logger = logging.getLogger(__name__)

# 配置 pyautogui
pyautogui.FAILSAFE = True  # 鼠标移到屏幕角落可终止
pyautogui.PAUSE = 0.1  # 操作间隔（减小以便更精细控制）

# 获取屏幕缩放比例
def get_screen_scale():
    """获取 macOS 屏幕的缩放比例"""
    import objc
    from AppKit import NSScreen

    screens = NSScreen.screens()
    if screens:
        # 获取主屏幕
        main_screen = screens[0]
        # 获取 backing scale factor (Retina 缩放比例)
        scale = main_screen.backingScaleFactor()
        return float(scale)
    return 2.0  # 默认 Retina 2x

SCREEN_SCALE = get_screen_scale()
logger.info(f"屏幕缩放比例：{SCREEN_SCALE}x")

def convert_to_logical_coords(x, y):
    """将 Retina 像素坐标转换为逻辑坐标"""
    return int(x / SCREEN_SCALE), int(y / SCREEN_SCALE)


# ============ 验证码相关 ============

def check_and_handle_captcha():
    """
    检查是否有验证码，如果有则处理
    返回：True 表示处理成功或无需处理，False 表示处理失败
    """
    import os

    # 检查是否有验证码模板
    captcha_template_path = Path("templates/captcha_bg.png")
    if not captcha_template_path.exists():
        logger.debug("验证码模板不存在，跳过检测")
        return True

    # 截取屏幕
    screenshot = pyautogui.screenshot()
    screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    # 读取验证码背景模板
    captcha_bg = cv2.imread(str(captcha_template_path))
    if captcha_bg is None:
        return True

    # 检测验证码
    result = cv2.matchTemplate(screenshot_cv, captcha_bg, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    if max_val >= 0.8:
        logger.info(f"检测到验证码！位置：{max_loc}, 置信度：{max_val:.2f}")
        # 调用验证码处理函数
        return handle_captcha(screenshot_cv, max_loc)

    logger.debug("未检测到验证码")
    return True


def handle_captcha(screenshot_cv, captcha_pos):
    """
    处理滑动验证码
    1. 识别缺口位置
    2. 模拟人类滑动
    """
    logger.info("开始处理验证码...")

    # 截取验证码区域
    x, y = captcha_pos
    h, w = screenshot_cv.shape[:2]

    # 简单策略：尝试找到滑块并拖动
    # 这需要更复杂的图像处理来识别缺口
    # 这里使用一个简化的方法：手动截取滑块和缺口模板

    slider_template = Path("templates/captcha_slider.png")
    gap_template = Path("templates/captcha_gap.png")

    if not slider_template.exists() or not gap_template.exists():
        logger.warning("滑块或缺口模板不存在，无法自动处理验证码")
        logger.warning("请手动处理验证码后继续")
        time.sleep(10)  # 等待用户手动处理
        return True

    # 读取模板
    slider_img = cv2.imread(str(slider_template))
    gap_img = cv2.imread(str(gap_template))

    if slider_img is None or gap_img is None:
        logger.warning("无法读取验证码模板")
        return False

    # 在验证码区域内匹配缺口位置
    result = cv2.matchTemplate(screenshot_cv, gap_img, cv2.TM_CCOEFF_NORMED)
    _, _, _, gap_loc = cv2.minMaxLoc(result)

    # 计算滑动距离
    target_x = gap_loc[0]

    # 获取滑块当前位置
    slider_result = cv2.matchTemplate(screenshot_cv, slider_img, cv2.TM_CCOEFF_NORMED)
    _, _, _, slider_loc = cv2.minMaxLoc(result)
    start_x = slider_loc[0]

    # 滑动距离
    distance = target_x - start_x

    logger.info(f"验证码缺口位置：{target_x}, 需要滑动：{distance} 像素")

    # 拟人化滑动
    human_like_captcha_slide(start_x, captcha_pos[1] + 20, distance)

    time.sleep(2)  # 等待验证结果
    return True


def human_like_captcha_slide(start_x, start_y, distance):
    """
    拟人化滑动验证码
    模拟人类滑动轨迹：先快后慢，带微小抖动
    """
    import math

    pyautogui.moveTo(int(start_x), int(start_y))
    time.sleep(random.uniform(0.1, 0.3))

    # 按下鼠标
    pyautogui.mouseDown(button='left')
    time.sleep(random.uniform(0.1, 0.2))

    # 滑动轨迹
    steps = random.randint(15, 25)
    total_time = random.uniform(0.8, 1.5)
    step_time = total_time / steps

    for i in range(steps + 1):
        t = i / steps

        # 使用 ease-out 曲线（先快后慢）
        progress = 1 - (1 - t) ** 3

        # 当前滑动距离
        current_dist = distance * progress

        # 添加微小抖动（模拟人类手的不稳定性）
        jitter = random.uniform(-2, 2) * (1 - t)  # 抖动随时间减小

        x = int(start_x + current_dist + jitter)
        pyautogui.moveTo(x, int(start_y))
        time.sleep(step_time * random.uniform(0.5, 1.5))

    # 释放鼠标
    time.sleep(random.uniform(0.1, 0.2))
    pyautogui.mouseUp(button='left')
    logger.info("验证码滑动完成")


# ============ 拟人化操作相关 ============

import random

def human_like_move(target_x, target_y, duration=0.3):
    """
    拟人化鼠标移动 - 使用贝塞尔曲线路径
    """
    current_x, current_y = pyautogui.position()

    # 计算控制点（添加随机偏移）
    control_x = (current_x + target_x) / 2 + random.uniform(-50, 50)
    control_y = (current_y + target_y) / 2 + random.uniform(-50, 50)

    # 分段移动，模拟人类手的微动
    steps = random.randint(10, 20)
    for i in range(steps + 1):
        t = i / steps
        # 二次贝塞尔曲线
        x = (1-t)**2 * current_x + 2*(1-t)*t * control_x + t**2 * target_x
        y = (1-t)**2 * current_y + 2*(1-t)*t * control_y + t**2 * target_y
        pyautogui.moveTo(int(x), int(y), duration=duration/steps)
        time.sleep(random.uniform(0.01, 0.03))


def human_like_click(x, y):
    """
    拟人化点击 - 移动 + 随机延迟 + 点击
    """
    # 随机延迟（模拟人类反应时间）
    time.sleep(random.uniform(0.1, 0.3))

    # 拟人化移动
    human_like_move(x, y, duration=random.uniform(0.3, 0.6))

    # 点击前微小停顿
    time.sleep(random.uniform(0.05, 0.15))

    # 点击
    pyautogui.click(button='left')


def human_like_scroll(scroll_x, scroll_y, scroll_amount):
    """
    拟人化滚动 - 分多次滚动，每次随机量
    """
    # 先移动到滚动区域
    human_like_move(scroll_x, scroll_y, duration=0.3)
    time.sleep(random.uniform(0.1, 0.2))

    # 分多次滚动
    remaining = scroll_amount
    while remaining > 0:
        step = random.randint(1, 4)
        if step > remaining:
            step = remaining
        pyautogui.scroll(-step)
        remaining -= step
        time.sleep(random.uniform(0.05, 0.15))


class DazhongdianpAutoSignup:
    """大众点评霸王餐自动报名类"""

    def __init__(self, mirror_window_title="iPhone 镜像"):
        """
        初始化

        Args:
            mirror_window_title: Mac 镜像窗口标题
        """
        self.template_dir = Path(config.TEMPLATE_DIR)
        self.templates = {}
        self.signup_count = 0
        self.failed_count = 0
        self.mirror_window = None

        # 加载所有模板
        self._load_templates()

        # 查找镜像窗口
        self._find_mirror_window(mirror_window_title)

    def _find_mirror_window(self, window_title: str) -> None:
        """查找 Mac 镜像窗口"""
        import subprocess

        # 尝试查找 iPhone 镜像窗口
        result = subprocess.run(
            ["osascript", "-e", 'tell application "System Events" to get name of every process whose name contains "iPhone"'],
            capture_output=True,
            text=True
        )
        logger.info(f"查找镜像窗口：{result.stdout}")

    def _load_templates(self) -> None:
        """加载图像模板（OpenCV 格式）"""
        # 必选模板
        required_files = {
            "free_lottery": "free_lottery.png",
            "signup_btn": "signup_btn.png",
            "confirm_btn": "confirm_btn.png",
            "view_more": "view_more.png",
        }

        for key, filename in required_files.items():
            template_path = self.template_dir / filename
            if template_path.exists():
                # 使用 OpenCV 读取模板
                template = cv2.imread(str(template_path))
                if template is not None:
                    self.templates[key] = template
                    logger.info(f"已加载模板：{key} -> {filename} ({template.shape[1]}x{template.shape[0]})")
                else:
                    logger.error(f"无法读取模板文件：{filename}")
            else:
                logger.error(f"缺少必要的模板文件：{filename}")

        # 可选模板（success_hint.png）- 如果存在则加载
        optional_template = self.template_dir / "success_hint.png"
        if optional_template.exists():
            template = cv2.imread(str(optional_template))
            if template is not None:
                self.templates["success_hint"] = template
                logger.info(f"已加载可选模板：success_hint.png")

    def _check_templates(self) -> bool:
        """检查必要的模板是否都已加载"""
        required_templates = ["free_lottery", "signup_btn", "confirm_btn", "view_more"]
        missing = [t for t in required_templates if t not in self.templates]

        if missing:
            logger.error(f"缺少必要的模板文件：{missing}")
            logger.error("请先按照 templates/README.md 的说明采集模板截图")
            return False
        return True

    def _find_element(self, template_key: str, timeout: float = 5.0, threshold: float = 0.6) -> tuple | None:
        """
        查找屏幕上的图像元素

        Args:
            template_key: 模板键名
            timeout: 超时时间（秒）
            threshold: 匹配阈值（降低到 0.6 以适应不同屏幕）

        Returns:
            元素坐标 (x, y)，未找到返回 None
        """
        if template_key not in self.templates:
            logger.error(f"模板不存在：{template_key}")
            return None

        template = self.templates[template_key]
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                # 截取屏幕
                screenshot = pyautogui.screenshot()
                screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

                # 模板匹配
                result = cv2.matchTemplate(screenshot_cv, template, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

                if max_val >= threshold:
                    logger.debug(f"找到元素 {template_key}: 位置={max_loc}, 置信度={max_val:.2f}")
                    # 返回元素中心坐标
                    h, w = template.shape[:2]
                    center_x = max_loc[0] + w // 2
                    center_y = max_loc[1] + h // 2
                    return (center_x, center_y)

            except Exception as e:
                logger.debug(f"查找元素失败：{e}")

            time.sleep(0.5)

        logger.warning(f"未找到元素：{template_key}")
        return None

    def _click_element(self, template_key: str, timeout: float = 5.0) -> bool:
        """
        点击图像元素 - 使用拟人化点击

        Args:
            template_key: 模板键名
            timeout: 超时时间（秒）

        Returns:
            是否点击成功
        """
        pos = self._find_element(template_key, timeout)
        if pos:
            # 转换为逻辑坐标
            logical_x, logical_y = convert_to_logical_coords(pos[0], pos[1])
            logger.info(f"点击 {template_key}，原始坐标：{pos}，逻辑坐标：({logical_x}, {logical_y})")

            # 使用拟人化点击
            human_like_click(logical_x, logical_y)
            time.sleep(config.CLICK_WAIT_TIME)
            return True
        return False

    def _swipe_page(self) -> None:
        """
        向上滑动页面加载更多商品

        使用鼠标滚轮向上滚动（页面向下移动，显示下方内容）
        模拟人快速滑动的习惯：一次性滚动较大距离，带随机性
        """
        # 获取屏幕尺寸（逻辑坐标）
        screen_height = pyautogui.size()[1]

        # 先移动到 iPhone 镜像窗口内的一个位置（左侧中间）
        swipe_x = 200
        swipe_y = int(screen_height * 0.5)

        # 随机决定滚动次数和每次滚动的量，模拟人的不规律操作
        scroll_rounds = random.randint(4, 8)  # 滚动 4-8 轮
        logger.info(f"滑动页面：移动到 ({swipe_x}, {swipe_y})，滚动 {scroll_rounds} 轮")

        for round in range(scroll_rounds):
            # 每轮滚动 25-40 个单位（大幅增加滚动距离）
            scroll_amount = random.randint(25, 40)
            human_like_scroll(swipe_x, swipe_y, scroll_amount)
            # 轮与轮之间随机停顿
            time.sleep(random.uniform(0.15, 0.4))

    def _small_swipe(self) -> None:
        """
        小幅度滚动，用于跳过已处理的商品
        """
        screen_height = pyautogui.size()[1]
        swipe_x = 200
        swipe_y = int(screen_height * 0.5)

        # 使用拟人化小幅度滚动
        human_like_scroll(swipe_x, swipe_y, scroll_amount=random.randint(3, 6))
        time.sleep(0.5)

    def _scroll_to_signup_btn(self) -> None:
        """
        向下滚动页面，查找"我要报名"按钮
        详情页的报名按钮通常在页面底部，需要滚动才能看到
        """
        screen_height = pyautogui.size()[1]
        # 将鼠标移到 iPhone 窗口左侧边缘（避免误触页面元素）
        swipe_x = 50  # 更靠左，确保在窗口边缘
        swipe_y = int(screen_height * 0.5)

        logger.info("向下滚动页面，查找'我要报名'按钮...")

        # 先移动到滚动位置，不点击
        pyautogui.moveTo(swipe_x, swipe_y, duration=0.3)
        time.sleep(0.2)

        # 向下滚动 2-3 次，每次滚动 15-25 个单位
        scroll_rounds = random.randint(2, 3)
        for round in range(scroll_rounds):
            scroll_amount = random.randint(15, 25)
            # 负数表示向下滚动（页面向上移动，显示下方内容）
            pyautogui.scroll(-scroll_amount)
            time.sleep(random.uniform(0.2, 0.4))

        # 等待页面加载
        time.sleep(1.0)
        logger.info("滚动完成")

    def _is_on_free_meal_page(self) -> bool:
        """检查是否在霸王餐列表页"""
        return self._find_element("free_lottery", timeout=3.0) is not None

    def _is_signup_success(self) -> bool:
        """检查是否报名成功"""
        if self.templates.get("success_hint"):
            return self._find_element("success_hint", timeout=2.0) is not None
        return True

    def _go_back_to_list(self) -> bool:
        """返回列表页"""
        # 点击"查看更多活动"按钮
        if self._click_element("view_more", timeout=5.0):
            time.sleep(2.0)
            return True

        # 如果没找到，尝试按 ESC 返回
        logger.warning("未找到'查看更多活动'按钮，尝试按 ESC 返回")
        pyautogui.press('esc')
        time.sleep(2.0)
        return True

    def signup_item(self, is_first_item: bool = False) -> bool:
        """
        报名单个商品

        Args:
            is_first_item: 是否是第一个商品（只有第一个商品的"免费抽"需要双击）

        Returns:
            是否报名成功
        """
        logger.info(">>> 开始报名商品")

        # 步骤 1: 点击"免费抽"按钮
        free_lottery_pos = self._find_element("free_lottery", timeout=5.0)
        if not free_lottery_pos:
            logger.error("未找到'免费抽'按钮")
            return False

        # 记录点击位置，用于后续检测
        clicked_pos = free_lottery_pos
        logger.info(f"准备点击'免费抽'，位置：{clicked_pos}")

        # 执行点击（转换为逻辑坐标）
        logical_x, logical_y = convert_to_logical_coords(free_lottery_pos[0], free_lottery_pos[1])
        logger.info(f"点击 free_lottery，原始坐标：{free_lottery_pos}，逻辑坐标：({logical_x}, {logical_y})")

        # 检查是否有验证码
        check_and_handle_captcha()

        # iPhone 镜像应用：第一个商品的"免费抽"需要特殊处理
        # 第一次点击激活窗口，第二次点击真正触发按钮
        if is_first_item:
            logger.info("第一个商品，执行两次点击（激活窗口 + 触发按钮）...")
            # 第一次点击 - 激活窗口
            pyautogui.click(logical_x, logical_y)
            time.sleep(0.1)  # 很短的间隔，确保在页面跳转前完成双击
            # 第二次点击 - 触发按钮（使用相同坐标）
            pyautogui.click(logical_x, logical_y)
        else:
            logger.info("非第一个商品，执行单击...")
            human_like_click(logical_x, logical_y)

        # 点击后将鼠标移到安全位置（iPhone 窗口外右侧），避免误触
        safe_x = logical_x + 500  # 向右移更多，确保移到 iPhone 窗口外
        safe_y = logical_y
        pyautogui.moveTo(safe_x, safe_y, duration=0.5)
        # 等待页面加载完成后再继续
        time.sleep(2.0)

        # 步骤 2: 等待进入详情页（增加等待时间）
        logger.info("等待页面加载...")
        time.sleep(3.0)

        # 步骤 2.5: 截取当前屏幕，调试用
        debug_screenshot = pyautogui.screenshot()
        debug_screenshot.save('debug_after_click.png')
        logger.info("已保存点击后截图：debug_after_click.png")

        # 检查是否还在列表页（可能点击失败或遇到风控）
        # 使用较短的超时时间来检测
        still_on_list = self._find_element("free_lottery", timeout=2.0)
        if still_on_list:
            # 检查是否是相同位置（真正点击失败）
            if still_on_list == clicked_pos:
                logger.warning(f"点击'免费抽'后仍在原位置 {clicked_pos}，点击未生效")
                pyautogui.press('esc')
                time.sleep(1.0)
                return False
            else:
                logger.info("检测到不同的'免费抽'按钮，可能已滚动，继续")

        # 步骤 2.6: 向下滚动页面，查找"我要报名"按钮
        self._scroll_to_signup_btn()

        # 步骤 3: 点击"我要报名"（使用更高的阈值避免误匹配）
        if not self._click_element("signup_btn", timeout=5.0):
            logger.error("未找到'我要报名'按钮")
            self._go_back_to_list()
            return False

        # 步骤 4: 点击"确认报名"
        if not self._click_element("confirm_btn", timeout=5.0):
            logger.error("未找到'确认报名'按钮")
            self._go_back_to_list()
            return False

        # 步骤 5: 等待报名成功提示
        time.sleep(config.SUCCESS_WAIT_TIME)

        # 步骤 6: 验证报名成功
        if self._is_signup_success():
            self.signup_count += 1
            logger.info(f"✓ 报名成功！累计报名：{self.signup_count} 个")
        else:
            logger.warning("未检测到报名成功提示，但继续执行")

        # 步骤 7: 返回列表
        self._go_back_to_list()

        return True

    def run(self, max_items: int = None) -> dict:
        """
        运行自动报名流程

        Args:
            max_items: 最大报名商品数，None 表示遍历所有

        Returns:
            统计结果
        """
        logger.info("=" * 50)
        logger.info("大众点评霸王餐自动报名脚本启动")
        logger.info("按 Ctrl+C 可终止脚本")
        logger.info("=" * 50)

        # 检查模板
        if not self._check_templates():
            return {"success": False, "error": "模板文件缺失"}

        # 检查是否在正确的页面
        if not self._is_on_free_meal_page():
            logger.error("当前不在霸王餐列表页，请先手动进入霸王餐模块")
            logger.error("提示：请确保 iPhone 镜像窗口已打开，且显示霸王餐页面")
            return {"success": False, "error": "不在正确的页面"}

        logger.info("✓ 检测到在霸王餐列表页")

        limit = max_items or float("inf")
        swipe_count = 0
        consecutive_no_find = 0
        last_pos = None  # 记录上一次点击的位置，用于检测是否卡住
        first_item_processed = False  # 标记是否已处理第一个商品

        while self.signup_count < limit and consecutive_no_find < 2:
            logger.info(f"\n--- 第 {swipe_count + 1} 页 ---")

            # 循环处理当前页的所有商品
            page_items = 0
            while page_items < config.MAX_ITEMS_PER_PAGE:
                if self.signup_count >= limit:
                    break

                # 查找"免费抽"按钮（30 秒超时）
                pos = self._find_element("free_lottery", timeout=30.0)
                if pos:
                    # 检查是否和上一次位置相同（可能卡住了）
                    if last_pos and pos == last_pos:
                        logger.info(f"检测到重复位置 {pos}，小幅度滑动跳过...")
                        self._small_swipe()
                        time.sleep(0.5)
                        # 重新查找
                        pos = self._find_element("free_lottery", timeout=30.0)
                        if pos and pos == last_pos:
                            logger.warning("仍然是相同位置，继续滑动...")
                            self._small_swipe()
                            continue

                    page_items += 1
                    consecutive_no_find = 0

                    # 只有第一个商品的"免费抽"需要双击
                    is_first = not first_item_processed
                    result = self.signup_item(is_first_item=is_first)
                    if result:
                        last_pos = pos  # 只有成功后才记录位置
                        first_item_processed = True  # 标记第一个商品已处理
                        logger.info(f"页面内进度：{page_items}/{config.MAX_ITEMS_PER_PAGE}")
                    else:
                        self.failed_count += 1
                        # 失败后滑动一下，尝试下一个商品
                        logger.info("报名失败，滑动到下一个商品...")
                        self._small_swipe()
                        time.sleep(0.5)
                else:
                    # 当前页没有更多商品了（30 秒内未找到）
                    logger.info(f"当前页已处理完，共 {page_items} 个商品")
                    break

            # 如果当前页没有处理任何商品，说明没有更多内容了
            if page_items == 0:
                consecutive_no_find += 1
                logger.warning(f"未找到商品 (连续 {consecutive_no_find} 次)")

            # 如果达到最大滑动次数，退出
            if swipe_count >= config.MAX_SWIPE_COUNT:
                logger.info("已达到最大滑动次数，停止")
                break

            # 如果还需要更多商品，滑动页面
            if self.signup_count < limit:
                swipe_count += 1
                logger.info(f"滑动页面加载更多... (第 {swipe_count} 次)")
                self._swipe_page()

        logger.info("\n" + "=" * 50)
        logger.info("执行完成！统计:")
        logger.info(f"  - 成功报名：{self.signup_count} 个")
        logger.info(f"  - 失败：{self.failed_count} 个")
        logger.info(f"  - 滑动页面：{swipe_count} 次")
        logger.info("=" * 50)

        return {
            "success": True,
            "signup_count": self.signup_count,
            "failed_count": self.failed_count,
            "swipe_count": swipe_count,
        }


def main(max_items: int = None):
    """主函数

    Args:
        max_items: 最大报名商品数，None 表示遍历所有
    """
    try:
        # 创建自动化实例
        auto_signup = DazhongdianpAutoSignup()

        # 运行
        result = auto_signup.run(max_items=max_items)

        if result.get("success"):
            logger.info(f"执行成功：{result}")
        else:
            logger.error(f"执行失败：{result.get('error')}")

    except KeyboardInterrupt:
        logger.info("用户中断执行")
    except Exception as e:
        logger.exception(f"执行出错：{e}")
        raise


if __name__ == "__main__":
    import sys
    # 支持命令行参数：python main.py [数量]
    max_items = None
    if len(sys.argv) > 1:
        try:
            max_items = int(sys.argv[1])
            logger.info(f"将处理最多 {max_items} 个商品")
        except ValueError:
            logger.error(f"无效的参数：{sys.argv[1]}，使用默认值（不限）")

    main(max_items=max_items)
