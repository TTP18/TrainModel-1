document.getElementById("nutrition-form").addEventListener("submit", function (event) {
    event.preventDefault();

    const inputData = {
        features: [
            parseFloat(document.getElementById("calories").value),
            parseFloat(document.getElementById("protein").value),
            parseFloat(document.getElementById("carbs").value),
            parseFloat(document.getElementById("fat").value),
            parseFloat(document.getElementById("cholesterol").value),
            parseFloat(document.getElementById("sodium").value)
        ]
    };

    console.log("📤 Gửi dữ liệu:", inputData);

    fetch("/recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(inputData)
    })
    .then(response => response.json())
    .then(data => {
        console.log("📥 Kết quả:", data);
        document.getElementById("result").innerHTML = `
            <h3>Nhóm người dùng: <b>${data.user_group}</b></h3>
            <h4>🍽️ Gợi ý thực đơn:</h4>
            <ul>
                <li><b>Bữa sáng:</b> ${data.meal_plan.Breakfast.join(", ")}</li>
                <li><b>Bữa trưa:</b> ${data.meal_plan.Lunch.join(", ")}</li>
                <li><b>Bữa tối:</b> ${data.meal_plan.Dinner.join(", ")}</li>
                <li><b>Ăn nhẹ:</b> ${data.meal_plan.Snack.join(", ")}</li>
            </ul>
        `;
    })
    .catch(error => console.error("❌ Lỗi:", error));
});
