"""
服装商品爬虫框架（Scrapy）
════════════════════════════════════════════════════════════════
论文第三章 · 数据采集与预处理 · 爬虫系统设计与实现

架构说明
─────────
1. start_requests()   生成多关键词搜索列表页请求
2. parse_list()       解析列表页：提取商品基础信息 + 翻页
3. parse_detail()     解析详情页：补充完整描述信息
4. MySQLPipeline      见 pipelines.py，负责去重写库

核心设计原则
─────────
· 礼貌爬取（DOWNLOAD_DELAY=2s，随机化延迟，CONCURRENT_REQUESTS=4）
· 用户代理伪装（模拟真实浏览器 UA）
· 异常健壮处理（JSON 解析失败时记录日志，不中断整体爬取）
· 翻页控制（每关键词最多 5 页，共约 5×5×44 ≈ 1100 条原始数据）

运行方式（演示）
─────────
    cd spider/
    scrapy crawl clothes -o output.jsonl

注意：真实运行需配置有效的淘宝 Cookie，
      本框架展示爬虫设计架构，数据实际来源为 Amazon 公开数据集翻译处理。
"""
import scrapy
import json
import re
from urllib.parse import urlencode


class ClothesSpider(scrapy.Spider):
    """
    淘宝服装商品定向爬虫

    爬取目标：按关键词搜索结果页 → 提取商品列表 → （可选）请求详情页
    输出字段：product_id / title / price / sales / image_url / shop_name /
              category / detail_url / description
    """
    name = "clothes"
    allowed_domains = ["item.taobao.com", "s.taobao.com"]

    # ── 搜索关键词列表（对应系统的商品分类体系）─────────────────────
    SEARCH_KEYWORDS = [
        "女装上衣",      # ← 对应数据库 category = '上衣'
        "男装T恤",
        "女装连衣裙",    # ← 对应数据库 category = '裙子'
        "牛仔裤",        # ← 对应数据库 category = '裤子'
        "休闲外套",      # ← 对应数据库 category = '外套'
        "卫衣",          # ← 对应数据库 category = '卫衣'
        "运动鞋",        # ← 对应数据库 category = '鞋靴'
    ]

    # ── Scrapy 配置 ────────────────────────────────────────────────
    custom_settings = {
        # 礼貌爬取：每次请求延迟 2 秒，随机化避免封禁
        "DOWNLOAD_DELAY": 2,
        "RANDOMIZE_DOWNLOAD_DELAY": True,

        # 并发控制：同时最多 4 个请求，降低对目标服务器的压力
        "CONCURRENT_REQUESTS": 4,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 4,

        # 浏览器 UA 伪装，绕过基本 Bot 检测
        "USER_AGENT": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),

        # 数据处理管道：写入 MySQL 数据库
        "ITEM_PIPELINES": {"spider.pipelines.MySQLPipeline": 300},

        # 自动限速（AutoThrottle 扩展）：根据服务器响应时间动态调整请求频率
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_START_DELAY": 1,
        "AUTOTHROTTLE_MAX_DELAY": 10,
    }

    # ── 第一步：生成搜索列表页请求 ─────────────────────────────────
    def start_requests(self):
        """
        针对每个搜索关键词生成首页搜索请求。
        淘宝搜索 URL 格式：https://s.taobao.com/search?q=连衣裙&sort=sale-desc&s=0
        """
        for keyword in self.SEARCH_KEYWORDS:
            params = {
                "q":        keyword,
                "sort":     "sale-desc",   # 按销量降序：保证获取热销商品
                "s":        0,             # 起始偏移量，0 = 第一页
                "imgfile":  "",
                "js":       1,
            }
            url = "https://s.taobao.com/search?" + urlencode(params)
            yield scrapy.Request(
                url,
                callback=self.parse_list,
                meta={"keyword": keyword, "page": 1},
                # 注：真实账号 Cookie 在此配置（已脱敏）
                # headers={"Cookie": "YOUR_TAOBAO_COOKIE"},
                errback=self.handle_error,
            )

    # ── 第二步：解析搜索列表页 ────────────────────────────────────
    def parse_list(self, response):
        """
        淘宝列表页的商品数据以 JSON 格式内嵌在 JS 变量 g_page_config 中。
        使用正则表达式提取该 JSON 块，再按路径取出商品数组。

        数据路径：g_page_config → mods → itemlist → data → auctions[]
        """
        # 从 JS 中提取内嵌 JSON
        pattern = re.compile(r'g_page_config\s*=\s*(\{.*?\});', re.S)
        match = pattern.search(response.text)
        if not match:
            self.logger.warning(f"[列表页] 未匹配到商品数据: {response.url}")
            return

        try:
            data  = json.loads(match.group(1))
            items = data["mods"]["itemlist"]["data"]["auctions"]
        except (KeyError, json.JSONDecodeError) as e:
            self.logger.error(f"[列表页] JSON解析失败: {e} | URL: {response.url}")
            return

        self.logger.info(f"[列表页] 关键词={response.meta['keyword']} "
                         f"第{response.meta['page']}页 | 获取商品数={len(items)}")

        for item in items:
            # 基础字段提取（列表页可获得的字段）
            yield {
                "product_id":  item.get("nid"),
                "title":       item.get("raw_title"),          # 原始标题（未截断）
                "price":       item.get("view_price"),
                "sales":       item.get("view_sales"),         # 展示销量字符串
                "image_url":   "https:" + item.get("pic_url", ""),
                "shop_name":   item.get("nick"),               # 店铺名
                "category":    response.meta["keyword"],       # 用搜索词作为初始分类
                "detail_url":  f"https://item.taobao.com/item.htm?id={item.get('nid')}",
            }

        # ── 翻页逻辑（最多爬 5 页 × 44 条 = 220 条/关键词）────────
        page = response.meta["page"]
        if page < 5:
            keyword = response.meta["keyword"]
            next_params = {
                "q": keyword, "sort": "sale-desc",
                "s": page * 44,   # 淘宝每页固定 44 个商品
            }
            yield scrapy.Request(
                "https://s.taobao.com/search?" + urlencode(next_params),
                callback=self.parse_list,
                meta={"keyword": keyword, "page": page + 1},
                errback=self.handle_error,
            )

    # ── 第三步（可选）：解析商品详情页 ────────────────────────────
    def parse_detail(self, response):
        """
        详情页补充商品的完整描述文本（用于后续文本特征提取）。
        描述 HTML 通过内嵌 JS 变量 $describeInit 获取。
        """
        pattern = re.compile(r'var\s+\$describeInit\s*=\s*(\{.*?\});', re.S)
        match   = pattern.search(response.text)
        description = ""
        if match:
            try:
                desc_data   = json.loads(match.group(1))
                description = desc_data.get("desc", "")
            except json.JSONDecodeError:
                pass  # 解析失败时忽略，不影响其他字段

        yield {
            "product_id":  response.meta["product_id"],
            "description": description,   # 完整商品描述，用于文本特征提取（第四章）
        }

    # ── 异常处理 ────────────────────────────────────────────────────
    def handle_error(self, failure):
        """统一处理请求失败（超时、HTTP 错误等），记录日志后继续"""
        self.logger.error(f"[请求失败] {failure.request.url} | {repr(failure)}")
