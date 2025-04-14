from flask import Flask, request, jsonify, render_template
import joblib
import pandas as pd
import numpy as np
import os

# ✅ Khởi tạo Flask
app = Flask(__name__, template_folder="templates", static_folder="static")

# ✅ Định nghĩa đường dẫn mô hình & dataset
model_path = "C:/Users/ADMIN/Desktop/Khai thác dữ liệu/model/random_forest_best.pkl"  # 📌 Mô hình Random Forest tốt nhất
scaler_path = "C:/Users/ADMIN/Desktop/Khai thác dữ liệu/model/scaler.pkl"  # 📌 Bộ chuẩn hóa (nếu cần)
dataset_path = "C:/Users/ADMIN/Desktop/Khai thác dữ liệu/datasets/Nutrition_data/daily_food_nutrition_dataset.csv"

# ✅ Kiểm tra file tồn tại không
for path, name in [(model_path, "mô hình"), (scaler_path, "scaler"), (dataset_path, "dataset")]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ Không tìm thấy {name}: {path}")

# ✅ Tải mô hình và bộ scaler
rf_model = joblib.load(model_path)
scaler = joblib.load(scaler_path)

# ✅ Đọc dữ liệu dinh dưỡng
nutrition_data = pd.read_csv(dataset_path)

# ✅ Chuẩn hóa tên cột (nếu cần)
nutrition_data.columns = nutrition_data.columns.str.strip().str.replace(" ", "_").str.lower()

# ✅ Phân loại nhóm người dùng dựa trên giá trị dinh dưỡng
def classify_user(row):
    if row["calories_(kcal)"] >= 400 and row["protein_(g)"] >= 35 and row["carbohydrates_(g)"] >= 70:
        return "Vận động viên"
    elif row["calories_(kcal)"] <= 200 and row["sugars_(g)"] <= 15 and row["fat_(g)"] <= 15:
        return "Người ăn kiêng"
    elif row["calories_(kcal)"] >= 500 and row["fat_(g)"] >= 35 and row["carbohydrates_(g)"] >= 80:
        return "Người cần tăng cân"
    elif row["cholesterol_(mg)"] >= 200 and row["sodium_(mg)"] >= 700:
        return "Người mắc bệnh tim mạch"
    else:
        return "Khác"

# ✅ Áp dụng phân nhóm vào dữ liệu
nutrition_data["user_group"] = nutrition_data.apply(classify_user, axis=1)

# ✅ Mapping nhóm người dùng
label_mapping = {
    "Vận động viên": 0, 
    "Người ăn kiêng": 1, 
    "Người cần tăng cân": 2, 
    "Người mắc bệnh tim mạch": 3, 
    "Khác": 4
}
label_mapping_reverse = {v: k for k, v in label_mapping.items()}

# ✅ Hàm gợi ý thực đơn
def recommend_meal_group(features, max_items=10):
    user_group_pred = rf_model.predict([features])[0]
    user_group_name = label_mapping_reverse.get(user_group_pred, "Không xác định")

    recommended_meals = nutrition_data[nutrition_data["user_group"] == user_group_name]

    meal_plan = {
        meal_type: recommended_meals[recommended_meals["meal_type"] == meal_type]["food_item"]
        .sample(n=min(max_items, len(recommended_meals)), random_state=42).tolist()
        for meal_type in ["Breakfast", "Lunch", "Dinner", "Snack"]
    }

    return user_group_name, meal_plan

# ✅ Route trang chủ
@app.route("/")
def home():
    return render_template("index.html")

# ✅ API gợi ý thực đơn
@app.route("/recommend", methods=["POST"])
def recommend():
    try:
        data = request.json
        features = np.array(data.get("features", [])).reshape(1, -1)

        # 📌 Kiểm tra dữ liệu đầu vào
        if features.shape[1] != len(scaler.mean_):
            return jsonify({"error": "❌ Dữ liệu đầu vào không đúng kích thước!"}), 400

        # ✅ Chuẩn hóa input trước khi predict
        features_scaled = scaler.transform(features)

        # ✅ Dự đoán nhóm người dùng
        user_group, meal_plan = recommend_meal_group(features_scaled[0])

        return jsonify({"user_group": user_group, "meal_plan": meal_plan})

    except Exception as e:
        return jsonify({"error": str(e)}), 400

# ✅ Chạy Flask App
if __name__ == "__main__":
    app.run(debug=True)
