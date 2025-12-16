"""
实验历史记录存储

使用SQLite数据库存储实验历史记录。
"""

import sqlite3
import json
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime
from pathlib import Path


@dataclass
class ExperimentHistory:
    """
    单条实验历史记录

    Attributes:
        id: 历史记录ID（数据库主键）
        timestamp: 实验运行时间戳 (ISO 8601格式)
        config_file: 配置文件路径
        config_name: 实验名称
        config: 完整配置对象（字典）
        result: 完整结果对象（字典）
        success: 实验是否成功
        error_message: 错误信息（如果失败）
        created_at: 记录创建时间
    """
    id: int
    timestamp: str
    config_file: str
    config_name: str
    config: dict
    result: Optional[dict]
    success: bool
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None

    def __post_init__(self):
        """初始化后处理"""
        if self.created_at is None:
            self.created_at = datetime.now()


class HistoryStore:
    """
    历史记录存储管理器

    使用SQLite数据库持久化存储实验历史记录。
    """

    # SQL语句
    CREATE_TABLE_SQL = """
        CREATE TABLE IF NOT EXISTS experiment_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            config_file TEXT NOT NULL,
            config_name TEXT,
            num_matches INTEGER,
            spectrum_utilization REAL,
            execution_time REAL,
            constraints_satisfied BOOLEAN,
            config_json TEXT NOT NULL,
            result_json TEXT,
            success BOOLEAN NOT NULL,
            error_message TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """

    CREATE_INDEXES_SQL = [
        "CREATE INDEX IF NOT EXISTS idx_timestamp ON experiment_history(timestamp DESC)",
        "CREATE INDEX IF NOT EXISTS idx_config_file ON experiment_history(config_file)",
        "CREATE INDEX IF NOT EXISTS idx_created_at ON experiment_history(created_at DESC)"
    ]

    def __init__(self, db_path: str = ":memory:"):
        """
        初始化历史记录存储

        Args:
            db_path: 数据库文件路径（支持~展开），默认为内存数据库
        """
        if db_path != ":memory:":
            db_path = str(Path(db_path).expanduser())

        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self._initialize_database()

    def _initialize_database(self):
        """初始化数据库（创建表和索引）"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

        # 创建表
        self.conn.execute(self.CREATE_TABLE_SQL)

        # 创建索引
        for index_sql in self.CREATE_INDEXES_SQL:
            self.conn.execute(index_sql)

        self.conn.commit()

    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            self.conn = None

    def insert(self, history: ExperimentHistory) -> int:
        """
        插入历史记录

        Args:
            history: 历史记录对象（id字段会被忽略）

        Returns:
            int: 插入记录的ID

        Raises:
            sqlite3.Error: 数据库操作失败
        """
        # 提取结果的关键指标
        num_matches = None
        spectrum_utilization = None
        execution_time = None
        constraints_satisfied = None

        if history.result:
            num_matches = history.result.get('num_matches')
            spectrum_utilization = history.result.get('spectrum_utilization')
            execution_time = history.result.get('execution_time')
            constraints_satisfied = history.result.get('constraints_satisfied')

        # 序列化config和result为JSON
        config_json = json.dumps(history.config, ensure_ascii=False)
        result_json = json.dumps(history.result, ensure_ascii=False) if history.result else None

        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO experiment_history (
                timestamp, config_file, config_name,
                num_matches, spectrum_utilization, execution_time, constraints_satisfied,
                config_json, result_json, success, error_message
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            history.timestamp,
            history.config_file,
            history.config_name,
            num_matches,
            spectrum_utilization,
            execution_time,
            constraints_satisfied,
            config_json,
            result_json,
            history.success,
            history.error_message
        ))

        self.conn.commit()
        return cursor.lastrowid

    def _row_to_history(self, row: sqlite3.Row) -> ExperimentHistory:
        """将数据库行转换为ExperimentHistory对象"""
        return ExperimentHistory(
            id=row['id'],
            timestamp=row['timestamp'],
            config_file=row['config_file'],
            config_name=row['config_name'],
            config=json.loads(row['config_json']),
            result=json.loads(row['result_json']) if row['result_json'] else None,
            success=bool(row['success']),
            error_message=row['error_message'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
        )

    def query_all(self, limit: int = 100, offset: int = 0) -> List[ExperimentHistory]:
        """
        查询所有记录

        Args:
            limit: 返回记录数上限
            offset: 偏移量

        Returns:
            List[ExperimentHistory]: 历史记录列表，按时间倒序
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM experiment_history
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """, (limit, offset))

        return [self._row_to_history(row) for row in cursor.fetchall()]

    def query_by_id(self, history_id: int) -> Optional[ExperimentHistory]:
        """
        根据ID查询记录

        Args:
            history_id: 历史记录ID

        Returns:
            Optional[ExperimentHistory]: 历史记录对象，不存在返回None
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM experiment_history WHERE id = ?
        """, (history_id,))

        row = cursor.fetchone()
        return self._row_to_history(row) if row else None

    def query_by_filter(self, **kwargs) -> List[ExperimentHistory]:
        """
        按条件查询记录

        Args:
            **kwargs: 查询条件
                - config_file: str (支持LIKE模糊匹配)
                - start_date: datetime
                - end_date: datetime
                - success: bool

        Returns:
            List[ExperimentHistory]: 匹配的历史记录列表
        """
        conditions = []
        params = []

        if 'config_file' in kwargs:
            conditions.append("config_file LIKE ?")
            params.append(f"%{kwargs['config_file']}%")

        if 'start_date' in kwargs:
            conditions.append("created_at >= ?")
            params.append(kwargs['start_date'].isoformat())

        if 'end_date' in kwargs:
            conditions.append("created_at <= ?")
            params.append(kwargs['end_date'].isoformat())

        if 'success' in kwargs:
            conditions.append("success = ?")
            params.append(int(kwargs['success']))

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        cursor = self.conn.cursor()
        cursor.execute(f"""
            SELECT * FROM experiment_history
            WHERE {where_clause}
            ORDER BY created_at DESC
        """, params)

        return [self._row_to_history(row) for row in cursor.fetchall()]

    def delete_by_id(self, history_id: int) -> bool:
        """
        删除记录

        Args:
            history_id: 历史记录ID

        Returns:
            bool: 是否成功删除
        """
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM experiment_history WHERE id = ?", (history_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    def delete_all(self) -> int:
        """
        删除所有记录

        Returns:
            int: 删除的记录数
        """
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM experiment_history")
        self.conn.commit()
        return cursor.rowcount

    def get_count(self) -> int:
        """
        获取记录总数

        Returns:
            int: 记录总数
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM experiment_history")
        return cursor.fetchone()[0]

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取统计信息

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
        cursor = self.conn.cursor()

        # 总数和成功/失败数
        cursor.execute("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as success,
                SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as failed
            FROM experiment_history
        """)
        row = cursor.fetchone()
        total_count = row[0]
        success_count = row[1] or 0
        failed_count = row[2] or 0

        # 平均指标（仅统计成功的实验）
        cursor.execute("""
            SELECT
                AVG(num_matches) as avg_matches,
                AVG(spectrum_utilization) as avg_utilization
            FROM experiment_history
            WHERE success = 1 AND num_matches IS NOT NULL
        """)
        row = cursor.fetchone()
        avg_matches = row[0] or 0.0
        avg_utilization = row[1] or 0.0

        return {
            "total_count": total_count,
            "success_count": success_count,
            "failed_count": failed_count,
            "avg_matches": round(avg_matches, 2),
            "avg_utilization": round(avg_utilization, 4)
        }
