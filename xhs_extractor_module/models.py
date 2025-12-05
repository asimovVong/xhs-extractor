# models.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid


@dataclass
class Note:
    """
    表示一篇小红书面经笔记（已经经过解析+OCR）
    """
    id: str                     # 你自己生成的 note_id，比如用小红书 noteId 或者 uuid
    url: str                    # 笔记链接
    title: str                  # 笔记标题
    text: str                   # 纯文本内容（正文 + 你认为有用的补充）
    ocr_text: str = ""          # 所有图片 OCR 文本合并
    images: List[str] = field(default_factory=list)  # 图片 URL 列表
    raw: Dict[str, Any] = field(default_factory=dict)  # 原始 JSON/HTML 解析结果，调试用


@dataclass
class InterviewQuestion:
    """
    从面经中抽取出的"标准化面试题"
    """
    id: str
    note_id: str
    source_url: str

    category: str              # "八股" | "手撕代码" | "项目"
    question: str
    answer: str

    company: Optional[str] = None      # 公司名称，如 "字节"、"阿里"、"美团"、"腾讯"
    position: Optional[str] = None     # 岗位名称，如 "后端"、"算法"、"大模型应用"、"前端"
    company_tag: Optional[str] = None  # 完整标签，e.g. "字节后端一面"（用于向后兼容）
    round_tag: Optional[str] = None    # 轮次，如 "一面"、"二面"、"三面"
    tags: List[str] = field(default_factory=list)  # ["操作系统", "进程线程"]
    difficulty: str = "medium"          # "easy"|"medium"|"hard"
    source_has_answer: bool = False
    language: Optional[str] = None      # 手撕代码题目的实现语言，如 "Python"、"Java"、"C++"、"Go" 等

    created_at: datetime = field(default_factory=datetime.utcnow)

    @staticmethod
    def new_id() -> str:
        return str(uuid.uuid4())
    
    def get_full_tag(self) -> str:
        """生成完整的标签字符串，如 '字节-后端-一面'"""
        parts = []
        if self.company:
            parts.append(self.company)
        if self.position:
            parts.append(self.position)
        if self.round_tag:
            parts.append(self.round_tag)
        return "-".join(parts) if parts else (self.company_tag or "")
