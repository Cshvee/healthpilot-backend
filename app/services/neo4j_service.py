"""
Neo4j 知识图谱服务
"""
from typing import List, Dict, Any, Optional
from neo4j import GraphDatabase, Driver
from app.config import get_settings

settings = get_settings()


class Neo4jService:
    """Neo4j 服务类"""
    
    _instance = None
    _driver: Optional[Driver] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._driver is None:
            self._driver = GraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
            )
    
    def close(self):
        """关闭连接"""
        if self._driver:
            self._driver.close()
            self._driver = None
            Neo4jService._instance = None
    
    def verify_connectivity(self) -> bool:
        """验证连接是否正常"""
        try:
            self._driver.verify_connectivity()
            return True
        except Exception:
            return False
    
    def query_by_keyword(self, keyword: str, limit: int = 25) -> List[Dict[str, Any]]:
        """
        按关键词查询实体
        
        Args:
            keyword: 搜索关键词
            limit: 返回结果数量限制
            
        Returns:
            查询结果列表
        """
        # 构建查询：匹配名称包含关键词的节点
        # 使用正则表达式进行模糊匹配
        query = """
        MATCH (n)
        WHERE n.name CONTAINS $keyword
        RETURN n, labels(n) as labels, n.name as name
        LIMIT $limit
        """
        
        try:
            with self._driver.session(database=settings.NEO4J_DATABASE) as session:
                result = session.run(query, keyword=keyword, limit=limit)
                
                records = []
                for record in result:
                    node = record["n"]
                    labels = record["labels"]
                    name = record["name"]
                    
                    # 将节点属性转换为字典
                    node_dict = dict(node)
                    
                    records.append({
                        "name": name,
                        "labels": labels,
                        "n": node_dict
                    })
                
                return records
        except Exception as e:
            print(f"Neo4j 查询错误: {e}")
            return []
    
    def get_node_count(self) -> int:
        """获取节点总数"""
        query = "MATCH (n) RETURN count(n) as count"
        try:
            with self._driver.session(database=settings.NEO4J_DATABASE) as session:
                result = session.run(query)
                record = result.single()
                return record["count"] if record else 0
        except Exception as e:
            print(f"Neo4j 计数错误: {e}")
            return 0


# 全局服务实例
neo4j_service = Neo4jService()


def get_neo4j_service() -> Neo4jService:
    """获取 Neo4j 服务实例"""
    return neo4j_service
