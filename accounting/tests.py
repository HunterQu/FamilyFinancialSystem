from django.db.models import Sum, Q
from .models import HistoryRecord, Category

# 假设'饮食'类别的名称是"饮食"
food_category_name = "饮食"

# 1. 获取支出类别的所有记录
expense_records = HistoryRecord.objects.filter(category__category_type="expense")

# 2. 获取总支出金额
total_expense = expense_records.aggregate(total=Sum('amount'))['total'] or 0

# 3. 获取饮食类别的所有支出记录
food_expense_records = expense_records.filter(Q(category__name=food_category_name) | Q(sub_category__parent__name=food_category_name))

# 4. 获取饮食支出的总金额
food_expense_total = food_expense_records.aggregate(total=Sum('amount'))['total'] or 0

# 5. 计算饮食支出占总支出的比例
if total_expense > 0:
    food_expense_ratio = (food_expense_total / total_expense) * 100
else:
    food_expense_ratio = 0

print(f"饮食支出占总支出的比例为: {food_expense_ratio:.2f}%")