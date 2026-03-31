# -*- coding: utf-8 -*-
"""
解析结果模型
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class ParseResult(Base):
    """解析结果表"""
    __tablename__ = "parse_results"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, comment="关联用户ID")
    pdf_name = Column(String(500), nullable=False, comment="PDF文件名")
    pdf_path = Column(String(1000), comment="PDF文件路径")
    device_type = Column(String(50), comment="器件类型")
    manufacturer = Column(String(100), comment="厂家")
    opn = Column(String(100), comment="器件型号")
    param_id = Column(Integer, ForeignKey("standard_params.id"), comment="关联标准参数ID")
    param_name = Column(String(100), comment="参数名")
    param_value = Column(String(200), comment="参数值")
    test_condition = Column(Text, comment="测试条件")
    parse_time = Column(DateTime, default=datetime.now, comment="解析时间")
    is_success = Column(Boolean, default=True, comment="是否提取成功")
    error_message = Column(Text, comment="错误信息")
    
    # 关联
    user = relationship("User", back_populates="parse_results")
    
    def __repr__(self):
        return f"<ParseResult(id={self.id}, pdf='{self.pdf_name}', param='{self.param_name}')>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "pdf_name": self.pdf_name,
            "device_type": self.device_type,
            "manufacturer": self.manufacturer,
            "opn": self.opn,
            "param_name": self.param_name,
            "param_value": self.param_value,
            "test_condition": self.test_condition,
            "parse_time": self.parse_time.isoformat() if self.parse_time else None,
            "is_success": self.is_success,
        }


class ParseLog(Base):
    """解析日志表"""
    __tablename__ = "parse_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    pdf_name = Column(String(500), comment="PDF文件名")
    log_type = Column(String(20), comment="日志类型(INFO/WARNING/ERROR/SUCCESS)")
    content = Column(Text, comment="日志内容")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    
    def __repr__(self):
        return f"<ParseLog(id={self.id}, type='{self.log_type}')>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "pdf_name": self.pdf_name,
            "log_type": self.log_type,
            "content": self.content,
            "create_time": self.create_time.isoformat() if self.create_time else None,
        }


class TableRecord(Base):
    """生成表格记录表"""
    __tablename__ = "table_records"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    table_name = Column(String(200), nullable=False, comment="表格文件名")
    device_type = Column(String(50), nullable=False, comment="器件类型")
    pdf_count = Column(Integer, default=0, comment="包含的PDF文件数量")
    pdf_list = Column(Text, comment="PDF文件列表(JSON格式)")
    file_path = Column(String(500), nullable=False, comment="表格文件路径")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    created_by = Column(String(50), comment="创建用户")
    
    def __repr__(self):
        return f"<TableRecord(id={self.id}, name='{self.table_name}')>"
    
    def to_dict(self):
        """转换为字典"""
        import json
        return {
            "id": self.id,
            "table_name": self.table_name,
            "device_type": self.device_type,
            "pdf_count": self.pdf_count,
            "pdf_list": json.loads(self.pdf_list) if self.pdf_list else [],
            "file_path": self.file_path,
            "create_time": self.create_time.isoformat() if self.create_time else None,
            "created_by": self.created_by,
        }
