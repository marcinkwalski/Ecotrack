document.addEventListener("DOMContentLoaded", () => {
    const categorySelect = document.getElementById("category");
    const subcategorySelect = document.getElementById("subcategory");
    const unitInput = document.getElementById("unit");
    if (!categorySelect || !subcategorySelect || !unitInput) {
        return;
    }

    const subcats = {
        transport: [
            ["walk", "Pieszo"],
            ["bike", "Rower"],
            ["escooter_electric", "Hulajnoga elektryczna"],
            ["scooter_petrol", "Hulajnoga spalinowa"],
            ["car_petrol", "Samochód (benzyna)"],
            ["car_diesel", "Samochód (diesel)"],
            ["car_hybrid", "Samochód (hybrydowy)"],
            ["car_ev", "Samochód (elektryczny)"],
            ["bus", "Autobus"],
            ["train", "Pociąg"],
            ["plane_short", "Samolot (krótki)"],
            ["plane_long", "Samolot (długi)"]
        ],
        food: [
            ["beef", "Wołowina"],
            ["lamb", "Jagnięcina"],
            ["cheese", "Ser"],
            ["pork", "Wieprzowina"],
            ["poultry", "Drób"],
            ["eggs", "Jajka"],
            ["fish", "Ryba"],
            ["vegetables", "Warzywa"],
            ["fruits", "Owoce"],
            ["grains", "Zboża"],
            ["nuts", "Orzechy"]
        ],
        energy: [
            ["electricity_pl", "Elektryczność (mix PL)"],
            ["electricity_green", "Elektryczność (OZE)"],
            ["gas", "Gaz"],
            ["lpg", "LPG"],
            ["coal", "Węgiel"]
        ],
        other: [
            ["electronics", "Elektronika"],
            ["clothing", "Odzież"],
            ["furniture", "Meble"]
        ]
    };

    const onCategoryChange = () => {
        const cat = categorySelect.value;
        subcategorySelect.innerHTML = "";
        const placeholder = document.createElement("option");
        placeholder.value = "";
        placeholder.textContent = "Wybierz podkategorię";
        placeholder.disabled = true;
        placeholder.selected = true;
        subcategorySelect.appendChild(placeholder);

        const entries = subcats[cat] || [];
        if (entries.length === 0) {
            const empty = document.createElement("option");
            empty.value = "";
            empty.textContent = "Brak podkategorii";
            subcategorySelect.appendChild(empty);
            subcategorySelect.disabled = true;
        } else {
            entries.forEach(([val, label]) => {
                const opt = document.createElement("option");
                opt.value = val;
                opt.textContent = label;
                subcategorySelect.appendChild(opt);
            });
            subcategorySelect.disabled = false;
        }

        if (cat === "transport") {
            unitInput.value = "km";
        } else if (cat === "food") {
            unitInput.value = "kg";
        } else if (cat === "energy") {
            unitInput.value = "kWh";
        } else {
            unitInput.value = "";
        }
    };

    categorySelect.addEventListener("change", onCategoryChange);
    onCategoryChange();
});
