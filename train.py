import os
import logging
from typing import Dict, List
from openai import OpenAI
from datetime import datetime

# Thiết lập logging
logging.basicConfig(filename='train.log', level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Đọc API key và Organization ID từ biến môi trường
api_key = os.getenv("OPENAI_API_KEY")
org_id = os.getenv("OPENAI_ORG_ID")

# Kiểm tra xem API key có tồn tại không
if not api_key:
    logger.error("OPENAI_API_KEY không được thiết lập trong biến môi trường.")
    raise ValueError("OPENAI_API_KEY không được thiết lập trong biến môi trường.")

# Khởi tạo client OpenAI
client = OpenAI(api_key=api_key, organization=org_id)   

# Định nghĩa cấu trúc dữ liệu cho tính cách DISC
DISC_PROFILES: Dict[str, Dict[str, List[str]]] = {
    "D": {
        "traits": ["quyết đoán", "định hướng kết quả", "thích thách thức"],
        "suitable_tasks": ["lãnh đạo dự án", "đàm phán", "ra quyết định chiến lược"]
    },
    "I": {
        "traits": ["nhiệt tình", "giao tiếp tốt", "lạc quan"],
        "suitable_tasks": ["bán hàng", "thuyết trình", "xây dựng mối quan hệ"]
    },
    "S": {
        "traits": ["kiên nhẫn", "đáng tin cậy", "hỗ trợ"],
        "suitable_tasks": ["hỗ trợ khách hàng", "quản lý nhóm", "điều phối dự án"]
    },
    "C": {
        "traits": ["chính xác", "phân tích", "cẩn thận"],
        "suitable_tasks": ["phân tích dữ liệu", "kiểm soát chất lượng", "lập kế hoạch chi tiết"]
    }
}

def time_remaining(deadline_str):
    """Tính thời gian còn lại trước deadline"""
    current_time = datetime.now()
    deadline = datetime.strptime(deadline_str, "%H:%M %d/%m/%Y")
    time_remaining = deadline - current_time
    
    if time_remaining.total_seconds() > 0:
        days = time_remaining.days
        hours, remainder = divmod(time_remaining.seconds, 3600)
        minutes = remainder // 60
        return f"Còn lại {days} ngày, {hours} giờ, {minutes} phút"
    else:
        time_remaining = current_time - deadline 
        days = time_remaining.days
        hours, remainder = divmod(time_remaining.seconds, 3600)
        minutes = remainder // 60
        return f"Đã trễ hạn {days} ngày, {hours} giờ, {minutes} phút"

def log_chatgpt_interaction(request: str, response: str):
    """Ghi log tương tác giữa người dùng và ChatGPT theo định dạng dễ đọc"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"""
{'='*50}
Thời gian: {timestamp}
{'='*50}
Yêu cầu:
{request}
{'-'*50}
Phản hồi:
{response}
{'='*50}
"""
    with open('chatgpt_interactions.log', 'a', encoding='utf-8') as log_file:
        log_file.write(log_entry)

def get_task_allocation(name: str, disc_scores: Dict[str, int], task: str, deadline: str) -> str:
    logger.info(f"Đang phân bổ công việc cho {name} với điểm DISC {disc_scores}")
    
    # Tính toán đặc điểm tính cách nổi bật nhất

    try:
        dominant_trait = max(disc_scores, key=disc_scores.get)
    except (TypeError, ValueError):
        print('Run Exept')
        disc_scores = {key: int(value) for key, value in disc_scores.items()}
        dominant_trait = max(disc_scores, key=disc_scores.get)

    
    prompt = f"""
    Hãy phân bổ công việc dựa trên điểm tính cách DISC cho:
    Tên: {name}
    Điểm DISC: D:{disc_scores['D']}, I:{disc_scores['I']}, S:{disc_scores['S']}, C:{disc_scores['C']}
    Đặc điểm nổi bật nhất: {dominant_trait}
    Nhiệm vụ: {task}
    Deadline: {time_remaining(deadline)}

    Yêu cầu:
    1. Phân tích tính phù hợp của nhiệm vụ dựa trên điểm DISC và đặc điểm nổi bật nhất.
    2. Đề xuất cách tiếp cận nhiệm vụ phù hợp với hồ sơ tính cách.
    3. Liệt kê các bước cụ thể để hoàn thành nhiệm vụ.
    4. Đề xuất các nguồn lực hoặc công cụ hỗ trợ.
    5. Xác định các thách thức tiềm ẩn và cách khắc phục.
    6. Xác định mức độ ảnh hưởng của thời gian còn lại cho đến deadline.
    7. Đánh giá chính xác tỉ lệ % khả năng hoàn thành nhiệm vụ.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        allocation = response.choices[0].message.content
        logger.info(f"Đã hoàn thành phân bổ công việc cho {name}")
        
        # Ghi log tương tác
        log_chatgpt_interaction(prompt, allocation)
        
        return allocation
    except Exception as e:
        logger.error(f"Lỗi khi gọi API OpenAI: {str(e)}", exc_info=True)
        return f"Đã xảy ra lỗi khi gọi API OpenAI: {str(e)}"

def main():
    logger.info("Bắt đầu hàm main")
    name = input("Nhập tên người: ")
    print("Nhập điểm DISC (0-100):")
    disc_scores = {
        'D': int(input("Điểm Dominance (D): ")),
        'I': int(input("Điểm Influence (I): ")),
        'S': int(input("Điểm Steadiness (S): ")),
        'C': int(input("Điểm Conscientiousness (C): "))
    }
    task = input("Nhập tên nhiệm vụ: ")
    deadline = input("Nhập deadline (HH:MM DD/MM/YYYY): ")
    
    allocation = get_task_allocation(name, disc_scores, task, deadline)
    print("\nPhân bổ công việc:\n", allocation)
    logger.info("Hàm main đã hoàn thành")

if __name__ == "__main__":
    main()