document.addEventListener("DOMContentLoaded", () => {
    const categorySelect = document.getElementById("category-select");
    const subcategorySelect = document.getElementById("subcategory-select");
    if (!categorySelect || !subcategorySelect) {
        return;
    }

    const SUBCATS = {
        transport: {
            walk: "Pieszo",
            bike: "Rower",
            escooter_electric: "Hulajnoga elektryczna",
            scooter_petrol: "Skuter spalinowy",
            car_petrol: "Samochód (benzyna)",
            car_diesel: "Samochód (diesel)",
            car_hybrid: "Samochód (hybrydowy)",
            car_ev: "Samochód (elektryczny)",
            bus: "Autobus",
            train: "Pociąg",
            plane_short: "Samolot (krótki lot)",
            plane_long: "Samolot (długi lot)"
        },
        food: {
            beef: "Wołowina",
            lamb: "Jagnięcina",
            cheese: "Ser",
            pork: "Wieprzowina",
            poultry: "Drób",
            eggs: "Jajka",
            fish: "Ryba",
            vegetables: "Warzywa",
            fruits: "Owoce",
            grains: "Zboża",
            nuts: "Orzechy"
        },
        energy: {
            electricity_pl: "Prąd (mix PL)",
            electricity_green: "Prąd (zielony)",
            gas: "Gaz",
            lpg: "LPG",
            coal: "Węgiel"
        },
        other: {
            electronics: "Elektronika",
            clothing: "Odzież",
            furniture: "Meble"
        }
    };

    const onCategoryChange = () => {
        const cat = categorySelect.value;
        const selected = subcategorySelect.dataset.selected || "";
        subcategorySelect.innerHTML = "";
        Object.entries(SUBCATS[cat] || {}).forEach(([key, label]) => {
            const opt = document.createElement("option");
            opt.value = key;
            opt.textContent = label;
            if (key === selected) {
                opt.selected = true;
            }
            subcategorySelect.appendChild(opt);
        });
    };

    categorySelect.addEventListener("change", onCategoryChange);
    onCategoryChange();
});
