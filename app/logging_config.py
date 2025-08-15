import logging #Để tạo và quản lý các log
import sys #Cho phép log hiển thị trên console(màn hình)
from logging.handlers import TimedRotatingFileHandler #Tự động tạo một file log mới vào thời điểm được chỉ định (ví dụ, hàng ngày) và xóa các file log cũ để quản lý dung lượng.
from pathlib import Path #Lớp này giúp làm việc với các đường dẫn tệp tin và thư mục một cách dễ dàng và an toàn hơn, thay vì dùng chuỗi.
from datetime import datetime #Nhập lớp datetime để làm việc với ngày và giờ, được sử dụng để tạo tên tệp log có chứa ngày hiện tại.


def setup_logging( #Gói toàn bộ logic thiết lập
    logger_name: str = "AppLogger",
    log_dir: str = "logs",
    filename_prefix: str = "app",
    level: str = "INFO"
) -> logging.Logger:
    """
    Thiết lập logging đơn giản và tái sử dụng được.

    Parameters
    ----------
    logger_name : str
        Tên logger.
    log_dir : str
        Thư mục chứa file log.
    filename_prefix : str
        Tiền tố tên file log.
    level : str
        Mức độ log: DEBUG, INFO, WARNING, ERROR, CRITICAL.

    Returns
    -------
    logging.Logger
        Logger đã cấu hình sẵn.
    """

    #Xử lý đường dẫn và tên tệp log
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    file_name = f"{filename_prefix}_{today}.log"
    file_path = log_path / file_name

    #Cấu hình định dạng và cấp độ log
    log_level = getattr(logging, level.upper(), logging.INFO)
    log_format = (
        "%(asctime)s - %(levelname)s - %(name)s - "
        "%(filename)s:%(lineno)d - %(message)s"
    )
    formatter = logging.Formatter(log_format)

    #Tạo và cấu hình logger chính
    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)
    logger.propagate = False #Ngăn logger này chuyển tiếp các thông báo log của nó đến logger cha. Điều này giúp tránh việc một thông báo log bị ghi lại nhiều lần.
    if logger.hasHandlers():
        logger.handlers.clear()

    #Cấu hình và thêm handler cho console
    console_handler = logging.StreamHandler(sys.stdout) #Tạo một handler để ghi log ra console. sys.stdout đảm bảo log được in ra màn hình tiêu chuẩn.
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    #Cấu hình và thêm handler cho file
    file_handler = TimedRotatingFileHandler(
        filename=file_path,
        when="midnight", #Handler sẽ tạo một tệp log mới vào lúc nửa đêm mỗi ngày.
        interval=1, #Tần suất xoay tệp (1 ngày).
        backupCount=7, #Giữ lại 7 tệp log cũ nhất. Tệp thứ 8 sẽ bị xóa.
        encoding="utf-8"
    )
    file_handler.suffix = "%Y-%m-%d.log"
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logger.info("Logger initialized.")
    return logger

