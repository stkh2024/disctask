function taskAllocation() {
    return {
        name: '',
        discScores: { D: 0, I: 0, S: 0, C: 0 },
        task: '',
        deadline: '',
        loading: false,
        allocation: '',
        showDISCIntro: false,  // Thêm biến này để kiểm soát hiển thị phần giới thiệu DISC
        allocateTask() {
            if (this.validateInputs()) {
                this.loading = true;
                // Gửi yêu cầu đến server
                fetch('/allocate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        name: this.name,
                        discScores: this.discScores,
                        task: this.task,
                        deadline: this.deadline
                    }),
                })
                .then(response => response.json())
                .then(data => {
                    this.loading = false;
                    if (data.error) {
                        alert(data.error);
                    } else {
                        this.allocation = data.allocation;
                    }
                })
                .catch((error) => {
                    this.loading = false;
                    console.error('Error:', error);
                    alert('Đã xảy ra lỗi khi phân bổ công việc');
                });
            }
        },
        validateInputs() {
            if (!this.name || !this.task || !this.deadline) {
                alert('Vui lòng điền đầy đủ thông tin');
                return false;
            }
            for (let score in this.discScores) {
                let value = parseInt(this.discScores[score]);
                if (isNaN(value) || value < 0 || value > 100) {
                    alert(`Điểm ${score} phải là số từ 0 đến 100`);
                    return false;
                }
            }
            return true;
        }
    }
}