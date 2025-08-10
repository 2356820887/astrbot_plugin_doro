import logging
import time
import traceback
import asyncio

import httpx
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import AstrBotConfig


@register("astrbot_plugin_doro", "shingetsu", "随机doro和cheshire表情包", "0.0.5")
class DoroCheshirePlugin(Star):
    """
    一个AstrBot插件，用于从API获取随机的Doro和Cheshire表情包。
    它具有独立的冷却时间、重试逻辑和错误处理。
    """

    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.logger = None
        self.config = config
        # 从配置中获取冷却时间，如果未设置则默认为60秒
        self.cooldown_period = config.get("cooldown_period", 60)
        # 使用字典来管理不同命令的冷却时间，更具扩展性
        self.last_called_times = {}
        self.max_retries = 3  # 最大重试次数

    async def initialize(self):
        """异步初始化插件，获取logger实例。"""
        self.logger = logging.getLogger(__name__)
        self.logger.info("Doro/Cheshire 插件已初始化。")

    def _is_on_cooldown(self, command_name: str) -> tuple[bool, float]:
        """
        检查指定命令是否在冷却时间内。

        Args:
            command_name (str): 要检查的命令名称 (例如, "doro")。

        Returns:
            tuple[bool, float]: (是否在冷却中, 剩余冷却时间)。
        """
        current_time = time.time()
        last_called = self.last_called_times.get(command_name, 0)
        elapsed_time = current_time - last_called
        is_cooling = elapsed_time < self.cooldown_period
        remaining_time = max(0, self.cooldown_period - elapsed_time)
        return is_cooling, remaining_time

    async def _get_random_sticker(
            self, event: AstrMessageEvent, command_name: str, api_url: str, entity_name: str
    ):
        """
        一个通用的方法，用于获取并发送一个随机表情包。
        此方法处理冷却、API请求、重试和错误。

        Args:
            event (AstrMessageEvent): 消息事件对象。
            command_name (str): 触发此操作的命令 ("doro", "cheshire")。
            api_url (str): 用于获取表情包的API端点。
            entity_name (str): 表情包的名称，用于用户消息 ("Doro", "Cheshire")。
        """
        # 1. 检查冷却时间
        on_cooldown, remaining_time = self._is_on_cooldown(command_name)
        if on_cooldown:
            yield event.plain_result(
                f"请稍等，距离下一次获取随机{entity_name}表情包还有 {remaining_time:.0f} 秒。"
            )
            return

        # 2. 带有重试逻辑的API请求循环
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(api_url)
                    response.raise_for_status()  # 对 4xx/5xx 响应抛出异常
                    data = response.json()

                    if data.get("success") and (sticker_url := data.get("sticker", {}).get("url")):
                        yield event.image_result(sticker_url)
                        self.last_called_times[command_name] = time.time()  # 仅在成功时更新时间
                        return  # 成功，退出函数

                    else:
                        # API报告失败或数据结构不正确
                        self.logger.warning(f"{entity_name} API未返回成功或URL: {data}")
                        yield event.plain_result(f"未能从{entity_name} API获取到有效的表情包，请稍后再试。")
                        self.last_called_times[command_name] = time.time()  # 更新冷却以防API问题
                        return

            except httpx.HTTPStatusError as e:
                # 新增：专门处理 402 错误码
                if e.response.status_code == 402:
                    self.logger.warning(f"{entity_name} API 返回 402 状态码，可能正在维护。")
                    yield event.plain_result(f"{entity_name} API 链接可能正在维护中，请稍后再试。")
                    # 遇到维护信息，直接设置冷却并返回，不再重试
                    self.last_called_times[command_name] = time.time()
                    return

                # 原有的其他 HTTP 错误处理
                self.logger.warning(f"{entity_name} - 尝试 {attempt + 1}: HTTP 状态错误: {e}")
                if attempt >= self.max_retries - 1:
                    error_detail = traceback.format_exc()
                    self.logger.error(f"{entity_name} - HTTP状态错误: {e}\n{error_detail}")
                    yield event.plain_result(f"{entity_name} API 请求失败，错误码：{e.response.status_code}")

            except httpx.RequestError as e:
                self.logger.warning(f"{entity_name} - 尝试 {attempt + 1}: 请求错误: {e}")
                if attempt >= self.max_retries - 1:
                    error_detail = traceback.format_exc()
                    self.logger.error(f"{entity_name} - 请求错误: {e}\n{error_detail}")
                    yield event.plain_result(f"请求{entity_name} API失败，请检查网络或API是否可用。")
            except Exception as e:
                # 捕获其他所有意外错误
                error_detail = traceback.format_exc()
                self.logger.error(f"{entity_name} - 未知错误: {e}\n{error_detail}")
                yield event.plain_result(f"处理{entity_name}请求时发生未知错误。")
                self.last_called_times[command_name] = time.time()  # 发生未知错误时也更新冷却
                return

            # 如果不是最后一次尝试，则进行指数退避等待
            if attempt < self.max_retries - 1:
                wait_time = 2 ** attempt
                await asyncio.sleep(wait_time)

        # 3. 如果所有重试都失败，更新冷却时间
        self.last_called_times[command_name] = time.time()

    @filter.command("doro")
    async def doro(self, event: AstrMessageEvent):
        """发送一个随机doro表情包。"""
        async for result in self._get_random_sticker(
                event=event,
                command_name="doro",
                api_url="https://www.doro.asia/api/random-sticker",
                entity_name="Doro"
        ):
            yield result

    @filter.command("cheshire")
    async def cheshire(self, event: AstrMessageEvent):
        """发送一个随机Cheshire表情包。"""
        async for result in self._get_random_sticker(
                event=event,
                command_name="cheshire",
                api_url="https://www.cheshire.asia/api/random-sticker",
                entity_name="Cheshire"
        ):
            yield result

    async def terminate(self):
        """插件被卸载/停用时调用，用于清理。"""
        self.logger.info("Doro/Cheshire 插件已卸载。")
