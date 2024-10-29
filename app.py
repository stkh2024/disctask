import logging
import traceback
from flask import Flask, render_template, request, jsonify
from train import get_task_allocation
from datetime import datetime

# Thiết lập logging
logging.basicConfig(filename='app.log', level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder='templates', static_folder='static')

@app.route('/')
def index():
    try:
        logger.info('Truy cập trang chủ')
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Lỗi ở route index: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': 'Đã xảy ra lỗi không mong muốn'}), 500

@app.route('/allocate', methods=['POST'])
def allocate():
    try:
        data = request.json
        logger.debug(f"Nhận dữ liệu: {data}")
        name = data['name']
        disc_scores = data['discScores']
        task = data['task']
        deadline = data['deadline']
        
        logger.info(f'Nhận yêu cầu phân bổ cho {name} với điểm DISC {disc_scores}')
        
        deadline_obj = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
        formatted_deadline = deadline_obj.strftime("%H:%M %d/%m/%Y")
        
        allocation = get_task_allocation(name, disc_scores, task, formatted_deadline)
        logger.info(f'Hoàn thành phân bổ công việc cho {name}')
        return jsonify({'allocation': allocation})
    except KeyError as e:
        logger.error(f"Thiếu key trong dữ liệu yêu cầu: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': f'Thiếu trường bắt buộc: {str(e)}'}), 400
    except ValueError as e:
        logger.error(f"Định dạng dữ liệu không hợp lệ: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': f'Định dạng dữ liệu không hợp lệ: {str(e)}'}), 400
    except Exception as e:
        logger.error(f"Lỗi không mong muốn trong quá trình phân bổ: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': 'Đã xảy ra lỗi không mong muốn trong quá trình phân bổ công việc'}), 500

if __name__ == '__main__':
    logger.info('Khởi động ứng dụng Flask')
    app.run(host='0.0.0.0', debug=True, port=8080)