# ========== App Config ==========
APP_TITLE = "Account Book API"
APP_VERSION = "2.0.0"
CORS_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]

# ========== Database ==========
DATA_DIR_NAME = "data"
DB_FILENAME = "account.db"

# ========== Date Formats ==========
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
MONTH_FORMAT = "%Y-%m"

# Supported date formats for CSV import (order matters: most specific first)
CSV_DATE_FORMATS = [
    "%Y-%m-%d %H:%M:%S",
    "%Y/%m/%d %H:%M:%S",
    "%Y-%m-%d",
    "%Y/%m/%d",
]

# ========== CSV ==========
CSV_ENCODING = "utf-8"
CSV_EXTENSION = ".csv"
EXPORT_FILENAME = "spending_export.csv"
EXPORT_HEADERS = ["品名", "一级分类", "二级分类", "金额", "日期"]

# ========== Special Category ==========
TOTAL_EXPENSE = "总支出"

# ========== Migration ==========
OLD_SPENDING_FILE = "spending.csv"
OLD_CLASSIFIER_FILE = "classifier.csv"


# ========== CSV Import Row Error Templates ==========
ERR_ROW_INSUFFICIENT_COLS = "第{row}行: 列数不足，需要 品名,一级分类,二级分类,金额"
ERR_ROW_CATEGORY_COLS = "第{row}行: 列数不足，需要 二级分类,一级分类"
ERR_ROW_EMPTY_NAME = "第{row}行: 分类名称不能为空"
ERR_ROW_AMOUNT_INVALID = "第{row}行: 金额格式错误"
ERR_ROW_DATE_INVALID = "第{row}行: 日期格式错误(支持YYYY-MM-DD/YYYY/MM/DD及含时分秒)，已使用今天日期"
ERR_ROW_CATEGORY_MISSING = "第{row}行: 分类'{name}'不存在，已跳过"
ERR_ROW_CATEGORY_DUPLICATE = "第{row}行: 二级分类'{second}'已存在于'{first}'下"
