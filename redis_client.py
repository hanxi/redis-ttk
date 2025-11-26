"""
Redis 连接管理模块
提供 Redis 数据库连接、操作和管理功能
"""

import logging
from dataclasses import dataclass
from typing import Any

import redis


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class RedisConfig:
    """Redis 连接配置"""

    host: str = "localhost"
    port: int = 6379
    password: str | None = None
    db: int = 0
    decode_responses: bool = True
    socket_timeout: float = 5.0
    socket_connect_timeout: float = 5.0
    retry_on_timeout: bool = True


class RedisClient:
    """Redis 客户端管理类"""

    def __init__(self, config: RedisConfig | None = None):
        """初始化 Redis 客户端"""
        self.config = config or RedisConfig()
        self.client: redis.Redis | None = None
        self.is_connected = False

    def connect(self) -> bool:
        """连接到 Redis 服务器"""
        try:
            self.client = redis.Redis(
                host=self.config.host,
                port=self.config.port,
                password=self.config.password,
                db=self.config.db,
                decode_responses=self.config.decode_responses,
                socket_timeout=self.config.socket_timeout,
                socket_connect_timeout=self.config.socket_connect_timeout,
                retry_on_timeout=self.config.retry_on_timeout,
            )

            # 测试连接
            self.client.ping()
            self.is_connected = True
            logger.info(f"成功连接到 Redis: {self.config.host}:{self.config.port}")
            return True

        except redis.ConnectionError as e:
            logger.error(f"Redis 连接失败: {e}")
            self.is_connected = False
            return False
        except redis.AuthenticationError as e:
            logger.error(f"Redis 认证失败: {e}")
            self.is_connected = False
            return False
        except Exception as e:
            logger.error(f"Redis 连接异常: {e}")
            self.is_connected = False
            return False

    def disconnect(self):
        """断开 Redis 连接"""
        if self.client:
            try:
                self.client.close()
                logger.info("Redis 连接已断开")
            except Exception as e:
                logger.error(f"断开 Redis 连接时出错: {e}")

        self.client = None
        self.is_connected = False

    def test_connection(self) -> bool:
        """测试 Redis 连接状态"""
        if not self.client:
            return False

        try:
            self.client.ping()
            return True
        except Exception:
            self.is_connected = False
            return False

    def get_server_info(self) -> dict[str, Any]:
        """获取 Redis 服务器信息"""
        if not self.is_connected or not self.client:
            raise ConnectionError("未连接到 Redis 服务器")

        try:
            return self.client.info()
        except Exception as e:
            logger.error(f"获取服务器信息失败: {e}")
            raise

    def get_databases(self) -> list[int]:
        """获取可用的数据库列表"""
        if not self.is_connected or not self.client:
            raise ConnectionError("未连接到 Redis 服务器")

        try:
            info = self.client.info()
            # 从配置中获取数据库数量，默认为 16
            db_count = info.get("databases", 16)
            return list(range(db_count))
        except Exception as e:
            logger.error(f"获取数据库列表失败: {e}")
            # 返回默认数据库列表
            return list(range(16))

    def select_database(self, db_number: int) -> bool:
        """选择数据库"""
        if not self.is_connected or not self.client:
            raise ConnectionError("未连接到 Redis 服务器")

        try:
            # 创建新的连接到指定数据库
            new_config = RedisConfig(
                host=self.config.host,
                port=self.config.port,
                password=self.config.password,
                db=db_number,
                decode_responses=self.config.decode_responses,
                socket_timeout=self.config.socket_timeout,
                socket_connect_timeout=self.config.socket_connect_timeout,
                retry_on_timeout=self.config.retry_on_timeout,
            )

            new_client = redis.Redis(
                host=new_config.host,
                port=new_config.port,
                password=new_config.password,
                db=new_config.db,
                decode_responses=new_config.decode_responses,
                socket_timeout=new_config.socket_timeout,
                socket_connect_timeout=new_config.socket_connect_timeout,
                retry_on_timeout=new_config.retry_on_timeout,
            )

            # 测试新连接
            new_client.ping()

            # 关闭旧连接
            if self.client:
                self.client.close()

            # 更新配置和客户端
            self.config = new_config
            self.client = new_client

            logger.info(f"已切换到数据库 {db_number}")
            return True

        except Exception as e:
            logger.error(f"切换数据库失败: {e}")
            return False

    def get_all_keys(self, pattern: str = "*") -> list[str]:
        """获取所有键"""
        if not self.is_connected or not self.client:
            raise ConnectionError("未连接到 Redis 服务器")

        try:
            keys = self.client.keys(pattern)
            return sorted(keys) if keys else []
        except Exception as e:
            logger.error(f"获取键列表失败: {e}")
            raise

    def get_key_info(self, key: str) -> dict[str, Any]:
        """获取键的详细信息"""
        if not self.is_connected or not self.client:
            raise ConnectionError("未连接到 Redis 服务器")

        try:
            key_type = self.client.type(key)
            ttl = self.client.ttl(key)

            # 尝试获取内存使用情况，如果不支持则返回 None
            size = None
            try:
                if hasattr(self.client, "memory_usage"):
                    size = self.client.memory_usage(key)
            except Exception as memory_error:
                # Redis 版本不支持 MEMORY USAGE 命令，忽略此错误
                logger.debug(f"MEMORY USAGE 命令不支持: {memory_error}")
                size = None

            return {"key": key, "type": key_type, "ttl": ttl, "size": size}
        except Exception as e:
            logger.error(f"获取键信息失败: {e}")
            raise

    def get_value(self, key: str) -> Any:
        """获取键的值"""
        if not self.is_connected or not self.client:
            raise ConnectionError("未连接到 Redis 服务器")

        try:
            key_type = self.client.type(key)

            if key_type == "string":
                return self.client.get(key)
            elif key_type == "list":
                return self.client.lrange(key, 0, -1)
            elif key_type == "set":
                return list(self.client.smembers(key))
            elif key_type == "zset":
                return self.client.zrange(key, 0, -1, withscores=True)
            elif key_type == "hash":
                return self.client.hgetall(key)
            else:
                return None

        except Exception as e:
            logger.error(f"获取键值失败: {e}")
            raise

    def set_value(
        self, key: str, value: Any, key_type: str = "string", **kwargs
    ) -> bool:
        """设置键的值"""
        if not self.is_connected or not self.client:
            raise ConnectionError("未连接到 Redis 服务器")

        try:
            if key_type == "string":
                return self.client.set(key, value, **kwargs)
            elif key_type == "list":
                # 清空列表并重新添加
                self.client.delete(key)
                if isinstance(value, (list, tuple)):
                    for item in value:
                        self.client.rpush(key, item)
                else:
                    self.client.rpush(key, value)
                return True
            elif key_type == "set":
                # 清空集合并重新添加
                self.client.delete(key)
                if isinstance(value, (list, tuple, set)):
                    for item in value:
                        self.client.sadd(key, item)
                else:
                    self.client.sadd(key, value)
                return True
            elif key_type == "zset":
                # 清空有序集合并重新添加
                self.client.delete(key)
                if isinstance(value, (list, tuple)):
                    for item in value:
                        if isinstance(item, (list, tuple)) and len(item) == 2:
                            # (member, score) 格式
                            self.client.zadd(key, {item[0]: item[1]})
                        else:
                            # 默认分数为 0
                            self.client.zadd(key, {item: 0})
                elif isinstance(value, dict):
                    self.client.zadd(key, value)
                return True
            elif key_type == "hash":
                # 清空哈希并重新添加
                self.client.delete(key)
                if isinstance(value, dict):
                    self.client.hset(key, mapping=value)
                return True
            else:
                return False

        except Exception as e:
            logger.error(f"设置键值失败: {e}")
            raise

    def delete_key(self, key: str) -> bool:
        """删除键"""
        if not self.is_connected or not self.client:
            raise ConnectionError("未连接到 Redis 服务器")

        try:
            result = self.client.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"删除键失败: {e}")
            raise

    def rename_key(self, old_key: str, new_key: str) -> bool:
        """重命名键"""
        if not self.is_connected or not self.client:
            raise ConnectionError("未连接到 Redis 服务器")

        try:
            self.client.rename(old_key, new_key)
            return True
        except Exception as e:
            logger.error(f"重命名键失败: {e}")
            raise

    def set_ttl(self, key: str, seconds: int) -> bool:
        """设置键的过期时间"""
        if not self.is_connected or not self.client:
            raise ConnectionError("未连接到 Redis 服务器")

        try:
            return self.client.expire(key, seconds)
        except Exception as e:
            logger.error(f"设置过期时间失败: {e}")
            raise

    def remove_ttl(self, key: str) -> bool:
        """移除键的过期时间"""
        if not self.is_connected or not self.client:
            raise ConnectionError("未连接到 Redis 服务器")

        try:
            return self.client.persist(key)
        except Exception as e:
            logger.error(f"移除过期时间失败: {e}")
            raise
