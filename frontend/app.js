const API_BASE_URL = 'http://localhost:8001';
let editingStudentId = null;

document.addEventListener('DOMContentLoaded', function() {
    checkAPIStatus();
    loadStudents();
    setupEventListeners();
});

function setupEventListeners() {
    document.getElementById('studentForm').addEventListener('submit', handleFormSubmit);
    document.getElementById('refreshBtn').addEventListener('click', loadStudents);
    document.getElementById('cancelBtn').addEventListener('click', cancelEdit);
    
    const modal = document.getElementById('modal');
    const closeBtn = modal.querySelector('.close');
    closeBtn.addEventListener('click', () => modal.style.display = 'none');
    
    window.addEventListener('click', (event) => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
}

async function checkAPIStatus() {
    const statusElement = document.getElementById('apiStatus');
    
    try {
        const response = await fetch(`${API_BASE_URL}/`);
        const data = await response.json();
        
        if (response.ok) {
            statusElement.textContent = '正常運行';
            statusElement.className = 'status-ok';
        } else {
            statusElement.textContent = '異常';
            statusElement.className = 'status-error';
        }
    } catch (error) {
        statusElement.textContent = '無法連接';
        statusElement.className = 'status-error';
        console.error('API 狀態檢查失敗:', error);
    }
}

async function loadStudents() {
    const studentsList = document.getElementById('studentsList');
    studentsList.innerHTML = '<div class="loading">載入中...</div>';
    
    try {
        const response = await fetch(`${API_BASE_URL}/students/`);
        const students = await response.json();
        
        if (response.ok) {
            displayStudents(students);
        } else {
            throw new Error('載入學生列表失敗');
        }
    } catch (error) {
        studentsList.innerHTML = '<div class="error">載入失敗: ' + error.message + '</div>';
        console.error('載入學生失敗:', error);
    }
}

function displayStudents(students) {
    const studentsList = document.getElementById('studentsList');
    
    if (students.length === 0) {
        studentsList.innerHTML = '<div class="empty">暫無學生資料</div>';
        return;
    }
    
    const studentsHTML = students.map(student => `
        <div class="student-card" data-id="${student.id}">
            <div class="student-info">
                <h3>${escapeHtml(student.name)}</h3>
                <p class="email">${escapeHtml(student.email)}</p>
                <p class="id">ID: ${student.id}</p>
            </div>
            <div class="student-actions">
                <button class="edit-btn" onclick="editStudent(${student.id})">編輯</button>
                <button class="delete-btn" onclick="deleteStudent(${student.id})">刪除</button>
            </div>
        </div>
    `).join('');
    
    studentsList.innerHTML = studentsHTML;
}

async function handleFormSubmit(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const studentData = {
        name: formData.get('name'),
        email: formData.get('email'),
        password: formData.get('password')
    };
    
    if (editingStudentId) {
        await updateStudent(editingStudentId, studentData);
    } else {
        await createStudent(studentData);
    }
}

async function createStudent(studentData) {
    try {
        const response = await fetch(`${API_BASE_URL}/students/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(studentData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showMessage('學生新增成功!', 'success');
            document.getElementById('studentForm').reset();
            loadStudents();
        } else {
            throw new Error(result.detail || '新增失敗');
        }
    } catch (error) {
        showMessage('新增失敗: ' + error.message, 'error');
        console.error('新增學生失敗:', error);
    }
}

async function editStudent(studentId) {
    try {
        const response = await fetch(`${API_BASE_URL}/students/${studentId}`);
        const student = await response.json();
        
        if (response.ok) {
            document.getElementById('name').value = student.name;
            document.getElementById('email').value = student.email;
            document.getElementById('password').value = '';
            
            editingStudentId = studentId;
            document.getElementById('submitBtn').textContent = '更新學生';
            document.getElementById('cancelBtn').style.display = 'inline-block';
            
            document.getElementById('studentForm').scrollIntoView({ behavior: 'smooth' });
        } else {
            throw new Error(student.detail || '載入學生資料失敗');
        }
    } catch (error) {
        showMessage('載入失敗: ' + error.message, 'error');
        console.error('載入學生資料失敗:', error);
    }
}

async function updateStudent(studentId, studentData) {
    try {
        const response = await fetch(`${API_BASE_URL}/students/${studentId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(studentData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showMessage('學生更新成功!', 'success');
            cancelEdit();
            loadStudents();
        } else {
            throw new Error(result.detail || '更新失敗');
        }
    } catch (error) {
        showMessage('更新失敗: ' + error.message, 'error');
        console.error('更新學生失敗:', error);
    }
}

async function deleteStudent(studentId) {
    if (!confirm('確定要刪除這個學生嗎？')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/students/${studentId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showMessage('學生刪除成功!', 'success');
            loadStudents();
        } else {
            const result = await response.json();
            throw new Error(result.detail || '刪除失敗');
        }
    } catch (error) {
        showMessage('刪除失敗: ' + error.message, 'error');
        console.error('刪除學生失敗:', error);
    }
}

function cancelEdit() {
    editingStudentId = null;
    document.getElementById('submitBtn').textContent = '新增學生';
    document.getElementById('cancelBtn').style.display = 'none';
    document.getElementById('studentForm').reset();
}

function showMessage(message, type) {
    const modal = document.getElementById('modal');
    const modalMessage = document.getElementById('modalMessage');
    
    modalMessage.textContent = message;
    modalMessage.className = type;
    modal.style.display = 'block';
    
    setTimeout(() => {
        modal.style.display = 'none';
    }, 3000);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}