"""
历史记录控制器

管理实验历史记录的查询、保存和导出。
"""

from typing import List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime
import json

from ..models.history_store import HistoryStore, ExperimentHistory
from ..utils.config_manager import UserConfigManager


class HistoryController:
    """
    历史记录管理控制器

    提供历史记录的查询、管理和导出功能。
    """

    def __init__(self, db_path: Optional[str] = None):
        """
        初始化历史记录控制器

        Args:
            db_path: 数据库路径，默认使用用户配置目录
        """
        if db_path is None:
            UserConfigManager.ensure_config_dir()
            db_path = str(UserConfigManager.HISTORY_DB)

        self.store = HistoryStore(db_path)

    def close(self):
        """关闭数据库连接"""
        self.store.close()

    # ==================== 查询功能 (T025) ====================

    def query_all(self, limit: int = 100, offset: int = 0) -> List[ExperimentHistory]:
        """
        查询所有历史记录

        Args:
            limit: 返回记录数上限
            offset: 偏移量（用于分页）

        Returns:
            List[ExperimentHistory]: 历史记录列表，按时间倒序
        """
        return self.store.query_all(limit=limit, offset=offset)

    def query_by_config_file(self, config_file: str) -> List[ExperimentHistory]:
        """
        根据配置文件查询历史记录

        Args:
            config_file: 配置文件路径（支持模糊匹配）

        Returns:
            List[ExperimentHistory]: 匹配的历史记录列表
        """
        return self.store.query_by_filter(config_file=config_file)

    def query_by_date_range(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[ExperimentHistory]:
        """
        根据日期范围查询历史记录

        Args:
            start_date: 开始日期（包含）
            end_date: 结束日期（包含）

        Returns:
            List[ExperimentHistory]: 匹配的历史记录列表
        """
        kwargs = {}
        if start_date:
            kwargs['start_date'] = start_date
        if end_date:
            kwargs['end_date'] = end_date

        return self.store.query_by_filter(**kwargs)

    def query_successful(self) -> List[ExperimentHistory]:
        """
        查询所有成功的实验记录

        Returns:
            List[ExperimentHistory]: 成功的历史记录列表
        """
        return self.store.query_by_filter(success=True)

    def query_failed(self) -> List[ExperimentHistory]:
        """
        查询所有失败的实验记录

        Returns:
            List[ExperimentHistory]: 失败的历史记录列表
        """
        return self.store.query_by_filter(success=False)

    def get_by_id(self, history_id: int) -> Optional[ExperimentHistory]:
        """
        根据ID获取历史记录

        Args:
            history_id: 历史记录ID

        Returns:
            Optional[ExperimentHistory]: 历史记录对象，不存在返回None
        """
        return self.store.query_by_id(history_id)

    def get_count(self) -> int:
        """
        获取历史记录总数

        Returns:
            int: 记录总数
        """
        return self.store.get_count()

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取历史记录统计信息

        Returns:
            Dict[str, Any]: 统计信息
                {
                    "total_count": int,
                    "success_count": int,
                    "failed_count": int,
                    "avg_matches": float,
                    "avg_utilization": float
                }
        """
        return self.store.get_statistics()

    # ==================== 管理功能 (T026) ====================

    def save_experiment(
        self,
        config_file: str,
        config: Dict[str, Any],
        result: Optional[Dict[str, Any]] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        timestamp: Optional[str] = None
    ) -> int:
        """
        保存实验记录到历史数据库

        Args:
            config_file: 配置文件路径
            config: 完整配置对象
            result: 实验结果（成功时提供）
            success: 实验是否成功
            error_message: 错误信息（失败时提供）
            timestamp: 实验时间戳（默认为当前时间）

        Returns:
            int: 插入记录的ID

        Raises:
            ValueError: 参数验证失败
        """
        # 验证参数
        if not config_file:
            raise ValueError("config_file不能为空")

        if not config:
            raise ValueError("config不能为空")

        if success and result is None:
            raise ValueError("成功的实验必须提供result")

        if not success and error_message is None:
            raise ValueError("失败的实验必须提供error_message")

        # 设置默认时间戳
        if timestamp is None:
            timestamp = datetime.now().isoformat()

        # 提取配置名称
        config_name = config.get('name', Path(config_file).stem)

        # 创建历史记录对象
        history = ExperimentHistory(
            id=0,  # 会被数据库自动生成
            timestamp=timestamp,
            config_file=config_file,
            config_name=config_name,
            config=config,
            result=result,
            success=success,
            error_message=error_message
        )

        # 插入数据库
        return self.store.insert(history)

    def delete_by_id(self, history_id: int) -> bool:
        """
        删除指定的历史记录

        Args:
            history_id: 历史记录ID

        Returns:
            bool: 是否成功删除
        """
        return self.store.delete_by_id(history_id)

    def delete_all(self) -> int:
        """
        删除所有历史记录（手动清理功能）

        Returns:
            int: 删除的记录数
        """
        return self.store.delete_all()

    # ==================== 导出功能 (T027) ====================

    def export_to_json(
        self,
        output_file: str,
        history_ids: Optional[List[int]] = None,
        include_config: bool = True,
        include_result: bool = True
    ) -> int:
        """
        导出历史记录到JSON文件

        Args:
            output_file: 输出文件路径
            history_ids: 要导出的记录ID列表（None表示导出全部）
            include_config: 是否包含完整配置
            include_result: 是否包含完整结果

        Returns:
            int: 导出的记录数

        Raises:
            ValueError: 参数验证失败
            IOError: 文件写入失败
        """
        # 查询要导出的记录
        if history_ids is None:
            # 导出全部记录
            records = self.store.query_all(limit=10000)
        else:
            # 导出指定记录
            records = []
            for history_id in history_ids:
                record = self.store.query_by_id(history_id)
                if record:
                    records.append(record)

        if not records:
            raise ValueError("没有找到要导出的记录")

        # 转换为JSON格式
        export_data = []
        for record in records:
            item = {
                "id": record.id,
                "timestamp": record.timestamp,
                "config_file": record.config_file,
                "config_name": record.config_name,
                "success": record.success,
                "created_at": record.created_at.isoformat() if record.created_at else None
            }

            # 可选：包含配置
            if include_config:
                item["config"] = record.config

            # 可选：包含结果
            if include_result and record.result:
                item["result"] = record.result

            # 包含错误信息（如果有）
            if record.error_message:
                item["error_message"] = record.error_message

            export_data.append(item)

        # 写入文件
        try:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            raise IOError(f"写入文件失败: {e}")

        return len(export_data)

    def export_summary_to_json(self, output_file: str) -> Dict[str, Any]:
        """
        导出历史记录汇总统计到JSON文件

        Args:
            output_file: 输出文件路径

        Returns:
            Dict[str, Any]: 导出的统计信息

        Raises:
            IOError: 文件写入失败
        """
        # 获取统计信息
        stats = self.get_statistics()

        # 添加导出时间
        stats['exported_at'] = datetime.now().isoformat()

        # 写入文件
        try:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(stats, f, ensure_ascii=False, indent=2)

        except Exception as e:
            raise IOError(f"写入文件失败: {e}")

        return stats
