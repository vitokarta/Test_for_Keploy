"""
學生管理系統的工具函數
這些函數可以被 Keploy 用來生成單元測試
"""

def calculate_gpa(scores: list) -> float:
    """
    計算學生的 GPA (Grade Point Average)
    Args:
        scores: 分數列表，範圍 0-100
    Returns:
        GPA 值，範圍 0.0-4.0
    """
    if not scores:
        return 0.0
    
    if not all(isinstance(score, (int, float)) for score in scores):
        raise TypeError("所有分數必須是數字")
    
    if not all(0 <= score <= 100 for score in scores):
        raise ValueError("分數必須在 0-100 範圍內")
    
    total_gpa = 0.0
    for score in scores:
        if score >= 97:
            gpa = 4.0
        elif score >= 93:
            gpa = 3.7
        elif score >= 90:
            gpa = 3.3
        elif score >= 87:
            gpa = 3.0
        elif score >= 83:
            gpa = 2.7
        elif score >= 80:
            gpa = 2.3
        elif score >= 77:
            gpa = 2.0
        elif score >= 73:
            gpa = 1.7
        elif score >= 70:
            gpa = 1.3
        elif score >= 67:
            gpa = 1.0
        elif score >= 65:
            gpa = 0.7
        else:
            gpa = 0.0
        
        total_gpa += gpa
    
    return round(total_gpa / len(scores), 2)


def validate_student_age(age: int) -> bool:
    """
    驗證學生年齡是否合理
    Args:
        age: 學生年齡
    Returns:
        True 如果年齡有效，否則 False
    """
    if not isinstance(age, int):
        return False
    
    return 16 <= age <= 100


def get_grade_level(score: float) -> str:
    """
    根據分數獲取等級
    Args:
        score: 分數 (0-100)
    Returns:
        等級字串 (A+, A, B+, B, C+, C, D, F)
    """
    if not isinstance(score, (int, float)):
        raise TypeError("分數必須是數字")

    if not 0 <= score <= 100:
        raise ValueError("分數必須在 0-100 範圍內")

    if score >= 97:
        return "A+"
    elif score >= 93:
        return "A"
    elif score >= 90:
        return "B+"
    elif score >= 87:
        return "B"
    elif score >= 83:
        return "C+"
    elif score >= 80:
        return "C"
    elif score >= 70:
        return "D"
    else:
        return "F"


def calculate_average(numbers: list) -> float:
    """
    計算數字列表的平均值
    Args:
        numbers: 數字列表
    Returns:
        平均值
    """
    if not numbers:
        return 0

    if not all(isinstance(n, (int, float)) for n in numbers):
        raise TypeError("所有元素必須是數字")

    return sum(numbers) / len(numbers)