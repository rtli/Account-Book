"""
自定义异常模块。

所有业务异常统一继承自 fastapi.HTTPException，
按领域分组，便于集中管理错误码与提示信息。
"""

from fastapi import HTTPException

# ============================================================
#  Category 分类相关异常
# ============================================================


class CategoryNotFoundError(HTTPException):
    """查询或操作的分类不存在。"""

    def __init__(self) -> None:
        super().__init__(status_code=404, detail="分类不存在")


class CategoryDuplicateError(HTTPException):
    """同一父级下已存在同名分类。"""

    def __init__(self) -> None:
        super().__init__(status_code=400, detail="分类已存在")


class ParentCategoryNotFoundError(HTTPException):
    """创建二级分类时指定的父级分类不存在。"""

    def __init__(self) -> None:
        super().__init__(status_code=400, detail="父级分类不存在")


class CategoryHasSpendingsError(HTTPException):
    """分类下仍有关联的记账记录，无法删除。"""

    def __init__(self) -> None:
        super().__init__(status_code=400, detail="分类下存在记账记录，无法删除")


class CategoryHasChildrenError(HTTPException):
    """分类下仍有子分类，无法删除。"""

    def __init__(self) -> None:
        super().__init__(status_code=400, detail="分类下存在子分类，无法删除")


# ============================================================
#  Spending 账目相关异常
# ============================================================


class SpendingNotFoundError(HTTPException):
    """查询或操作的账目记录不存在。"""

    def __init__(self) -> None:
        super().__init__(status_code=404, detail="账目不存在")


# ============================================================
#  CSV 文件上传相关异常
# ============================================================


class CSVFileRequiredError(HTTPException):
    """上传的文件不是 CSV 格式。"""

    def __init__(self) -> None:
        super().__init__(status_code=400, detail="请上传CSV文件")
