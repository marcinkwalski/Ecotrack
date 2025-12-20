document.addEventListener("DOMContentLoaded", () => {
    const recordsEl = document.getElementById("records-data");
    let records = [];
    if (recordsEl && recordsEl.textContent) {
        try {
            records = JSON.parse(recordsEl.textContent);
        } catch {
            records = [];
        }
    }

    const SUBCATEGORIES = {
        transport: {
            walk: "Spacer",
            bike: "Rower",
            escooter_electric: "Hulajnoga elektryczna",
            scooter_petrol: "Skuter spalinowy",
            car_petrol: "Samochód benzynowy",
            car_diesel: "Samochód diesel",
            car_hybrid: "Samochód hybrydowy",
            car_ev: "Samochód elektryczny",
            bus: "Autobus",
            train: "Pociąg",
            plane_short: "Samolot (krótki lot)",
            plane_long: "Samolot (długi lot)"
        },
        food: {
            beef: "Wołowina",
            lamb: "Baranina",
            cheese: "Ser",
            pork: "Wieprzowina",
            poultry: "Drób",
            eggs: "Jajka",
            fish: "Ryby",
            vegetables: "Warzywa",
            fruits: "Owoce",
            grains: "Zboża",
            nuts: "Orzechy"
        },
        energy: {
            electricity_pl: "Energia (mix PL)",
            electricity_green: "Energia zielona",
            gas: "Gaz",
            lpg: "LPG",
            coal: "Węgiel"
        },
        other: {
            electronics: "Elektronika",
            clothing: "Ubrania",
            furniture: "Meble"
        }
    };

    const UNITS = {
        transport: "km",
        food: "kg",
        energy: "kWh",
        other: "szt"
    };

    const categorySelect = document.getElementById("category");
    const subcategorySelect = document.getElementById("subcategory");
    const unitInput = document.getElementById("unit");

    const updateSubcategories = () => {
        if (!categorySelect || !subcategorySelect || !unitInput) {
            return;
        }
        const cat = categorySelect.value;
        const items = SUBCATEGORIES[cat] || {};
        subcategorySelect.innerHTML = "";
        const placeholder = document.createElement("option");
        placeholder.value = "";
        placeholder.textContent = "Wybierz podkategorię";
        placeholder.disabled = true;
        placeholder.selected = true;
        subcategorySelect.appendChild(placeholder);
        const entries = Object.entries(items);
        if (entries.length === 0) {
            const empty = document.createElement("option");
            empty.value = "";
            empty.textContent = "Brak podkategorii";
            subcategorySelect.appendChild(empty);
            subcategorySelect.disabled = true;
        } else {
            entries.forEach(([key, label]) => {
                const opt = document.createElement("option");
                opt.value = key;
                opt.textContent = label;
                subcategorySelect.appendChild(opt);
            });
            subcategorySelect.disabled = false;
        }
        unitInput.value = UNITS[cat] || "";
    };

    if (categorySelect) {
        categorySelect.addEventListener("change", updateSubcategories);
        updateSubcategories();
    }

    const getDaily = (items) => {
        const sums = {};
        items.forEach((r) => {
            const d = r.created_at.split("T")[0];
            sums[d] = (sums[d] || 0) + Number(r.value);
        });
        return sums;
    };

    const filterRange = (daily, range) => {
        if (range === "all") {
            return daily;
        }
        const cutoff = new Date();
        cutoff.setDate(cutoff.getDate() - Number(range) + 1);
        const out = {};
        Object.keys(daily).forEach((d) => {
            if (new Date(d) >= cutoff) {
                out[d] = daily[d];
            }
        });
        return out;
    };

    const scaleCanvas = (cv, ctx) => {
        const ratio = window.devicePixelRatio || 1;
        const width = cv.clientWidth;
        const height = cv.clientHeight;
        cv.width = Math.floor(width * ratio);
        cv.height = Math.floor(height * ratio);
        ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
        return { width, height };
    };

    const lineEmpty = document.getElementById("line-empty");
    const pieEmpty = document.getElementById("pie-empty");
    const pieLegend = document.getElementById("pie-legend");
    const pieTooltip = document.getElementById("pie-tooltip");

    let currentChartType = localStorage.getItem("chartType") || "line";

    const drawLine = (items, range, chartType) => {
        const cv = document.getElementById("emissionChart");
        if (!cv) {
            return;
        }
        const ctx = cv.getContext("2d");
        const { width, height } = scaleCanvas(cv, ctx);

        let daily = getDaily(items);
        daily = filterRange(daily, range);

        const days = Object.keys(daily).sort();
        const values = days.map((d) => daily[d]);

        ctx.clearRect(0, 0, width, height);

        if (values.length === 0) {
            if (lineEmpty) {
                lineEmpty.classList.remove("d-none");
            }
            cv.classList.add("d-none");
            return;
        }

        if (lineEmpty) {
            lineEmpty.classList.add("d-none");
        }
        cv.classList.remove("d-none");

        const ML = 54;
        const MR = 16;
        const MT = 16;
        const MB = 36;
        const W = width - ML - MR;
        const H = height - MT - MB;
        const maxVal = Math.max(...values) * 1.2 || 1;
        const x = (i) => ML + (i / (values.length - 1 || 1)) * W;
        const y = (v) => MT + H - (v / maxVal) * H;

        ctx.strokeStyle = "rgba(231, 242, 236, 0.15)";
        ctx.lineWidth = 1;
        ctx.fillStyle = "rgba(197, 212, 203, 0.85)";
        ctx.font = "12px Poppins, sans-serif";

        for (let i = 0; i <= 4; i += 1) {
            const yy = MT + (H / 4) * i;
            ctx.beginPath();
            ctx.moveTo(ML, yy);
            ctx.lineTo(width - MR, yy);
            ctx.stroke();
            ctx.fillText((maxVal * (1 - i / 4)).toFixed(1), 8, yy + 4);
        }

        const points = values.map((v, i) => ({ x: x(i), y: y(v) }));

        if (chartType === "bar") {
            const barWidth = Math.max(6, W / (values.length * 1.6));
            ctx.fillStyle = "rgba(35, 193, 107, 0.5)";
            ctx.strokeStyle = "rgba(35, 193, 107, 0.9)";
            points.forEach((p) => {
                ctx.fillRect(p.x - barWidth / 2, p.y, barWidth, MT + H - p.y);
            });
            return;
        }

        ctx.beginPath();
        ctx.strokeStyle = "rgba(35, 193, 107, 0.95)";
        ctx.lineWidth = 2.5;
        ctx.moveTo(points[0].x, points[0].y);
        points.slice(1).forEach((p) => {
            ctx.lineTo(p.x, p.y);
        });
        ctx.stroke();

        if (chartType === "area") {
            ctx.lineTo(points[points.length - 1].x, MT + H);
            ctx.lineTo(points[0].x, MT + H);
            ctx.closePath();
            ctx.fillStyle = "rgba(35, 193, 107, 0.18)";
            ctx.fill();
        }

        ctx.fillStyle = "rgba(35, 193, 107, 0.95)";
        points.forEach((p) => {
            ctx.beginPath();
            ctx.arc(p.x, p.y, 3.5, 0, Math.PI * 2);
            ctx.fill();
        });
    };

    const drawPie = (items) => {
        const cv = document.getElementById("pieChart");
        if (!cv) {
            return;
        }
        const ctx = cv.getContext("2d");
        const { width, height } = scaleCanvas(cv, ctx);

        const sums = {};
        items.forEach((r) => {
            sums[r.category] = (sums[r.category] || 0) + r.value;
        });

        const total = Object.values(sums).reduce((a, b) => a + b, 0);
        if (!total) {
            if (pieEmpty) {
                pieEmpty.classList.remove("d-none");
            }
            cv.classList.add("d-none");
            if (pieLegend) {
                pieLegend.innerHTML = "";
            }
            return;
        }

        if (pieEmpty) {
            pieEmpty.classList.add("d-none");
        }
        cv.classList.remove("d-none");

        const colors = ["#23c16b", "#1ea35b", "#2bd579", "#12663b", "#7fd9a9"];
        const entries = Object.entries(sums);
        const cx = width / 2;
        const cy = height / 2;
        const outer = Math.min(cx, cy) - 8;
        const inner = outer * 0.62;
        let start = -Math.PI / 2;

        ctx.clearRect(0, 0, width, height);
        const slices = entries.map(([cat, val], i) => {
            const slice = (val / total) * 2 * Math.PI;
            const end = start + slice;
            ctx.beginPath();
            ctx.arc(cx, cy, outer, start, end);
            ctx.arc(cx, cy, inner, end, start, true);
            ctx.closePath();
            ctx.fillStyle = colors[i % colors.length];
            ctx.fill();
            const mid = (start + end) / 2;
            const lx = cx + Math.cos(mid) * (outer + inner) * 0.5;
            const ly = cy + Math.sin(mid) * (outer + inner) * 0.5;
            const percent = ((val / total) * 100).toFixed(1);
            const sliceInfo = { cat, val, percent, start, end, lx, ly };
            start = end;
            return sliceInfo;
        });

        ctx.beginPath();
        ctx.fillStyle = "rgba(12, 24, 16, 0.9)";
        ctx.arc(cx, cy, inner - 6, 0, Math.PI * 2);
        ctx.fill();

        if (pieLegend) {
            pieLegend.innerHTML = slices
                .map((slice, i) => {
                    return `<div class="legend-item"><span class="legend-swatch" style="background:${colors[i % colors.length]}"></span><span>${slice.cat} ${slice.percent}%</span></div>`;
                })
                .join("");
        }

        const handleMove = (event) => {
            if (!pieTooltip) {
                return;
            }
            const rect = cv.getBoundingClientRect();
            const xPos = event.clientX - rect.left;
            const yPos = event.clientY - rect.top;
            const dx = xPos - cx;
            const dy = yPos - cy;
            const dist = Math.sqrt(dx * dx + dy * dy);
            const angle = Math.atan2(dy, dx);
            let normAngle = angle;
            if (normAngle < -Math.PI / 2) {
                normAngle += Math.PI * 2;
            }
            if (dist < inner || dist > outer) {
                pieTooltip.style.opacity = 0;
                return;
            }
            const match = slices.find((s) => normAngle >= s.start && normAngle <= s.end);
            if (!match) {
                pieTooltip.style.opacity = 0;
                return;
            }
            pieTooltip.textContent = `${match.cat}: ${match.val.toFixed(2)} kg (${match.percent}%)`;
            pieTooltip.style.left = `${xPos}px`;
            pieTooltip.style.top = `${yPos}px`;
            pieTooltip.style.opacity = 1;
        };

        const handleLeave = () => {
            if (pieTooltip) {
                pieTooltip.style.opacity = 0;
            }
        };

        cv.onmousemove = handleMove;
        cv.onmouseleave = handleLeave;
    };

    const rangeSelect = document.getElementById("rangeSelect");
    const chartTypeButtons = document.querySelectorAll(".chart-type-btn");

    const setChartType = (type) => {
        currentChartType = type;
        localStorage.setItem("chartType", type);
        chartTypeButtons.forEach((btn) => {
            btn.classList.toggle("active", btn.dataset.chartType === type);
        });
    };

    const updateCharts = () => {
        if (!rangeSelect) {
            return;
        }
        drawLine(records, rangeSelect.value, currentChartType);
        drawPie(records);
    };

    if (chartTypeButtons.length > 0) {
        chartTypeButtons.forEach((btn) => {
            btn.addEventListener("click", () => {
                setChartType(btn.dataset.chartType);
                updateCharts();
            });
        });
        setChartType(currentChartType);
    }

    if (rangeSelect) {
        rangeSelect.addEventListener("change", updateCharts);
        window.addEventListener("resize", updateCharts);
        updateCharts();
    }

    const simCategory = document.getElementById("sim-category");
    const simSubcategory = document.getElementById("sim-subcategory");
    const simAmount = document.getElementById("sim-amount");
    const simRun = document.getElementById("sim-run");
    const simResult = document.getElementById("sim-result");

    const updateSimSub = () => {
        if (!simCategory || !simSubcategory) {
            return;
        }
        const cat = simCategory.value;
        simSubcategory.innerHTML = "";
        const placeholder = document.createElement("option");
        placeholder.value = "";
        placeholder.textContent = "Wybierz podkategorię";
        placeholder.disabled = true;
        placeholder.selected = true;
        simSubcategory.appendChild(placeholder);
        const items = SUBCATEGORIES[cat] || {};
        const entries = Object.entries(items);
        if (entries.length === 0) {
            const empty = document.createElement("option");
            empty.value = "";
            empty.textContent = "Brak podkategorii";
            simSubcategory.appendChild(empty);
            simSubcategory.disabled = true;
            return;
        }
        entries.forEach(([key, label]) => {
            const opt = document.createElement("option");
            opt.value = key;
            opt.textContent = label;
            simSubcategory.appendChild(opt);
        });
        simSubcategory.disabled = false;
    };

    if (simCategory) {
        simCategory.addEventListener("change", updateSimSub);
        updateSimSub();
    }

    const runSimulation = async () => {
        if (!simCategory || !simSubcategory || !simAmount || !simResult) {
            return;
        }
        const category = simCategory.value;
        const subcategory = simSubcategory.value;
        const amount = simAmount.value;
        if (!category || !subcategory || !amount) {
            simResult.classList.remove("d-none");
            simResult.innerHTML = "<div class='alert alert-danger mb-0'>Wypełnij wszystkie pola</div>";
            return;
        }

        const res = await fetch("/simulate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                category,
                subcategory,
                change: parseFloat(amount)
            })
        });

        const data = await res.json();
        simResult.classList.remove("d-none");
        if (data.error) {
            simResult.innerHTML = `<div class="alert alert-danger mb-0">${data.error}</div>`;
            return;
        }

        const label = SUBCATEGORIES[category]?.[subcategory] || subcategory;
        simResult.innerHTML = `
            <div class="card shadow-sm">
                <div class="card-header">Wynik symulacji</div>
                <div class="card-body">
                    <p><strong>Zmiana:</strong> ${amount} jednostek (${label})</p>
                    <ul class="mb-3">
                        <li><strong>Dziennie:</strong> ${data.daily} kg CO₂</li>
                        <li><strong>Miesięcznie:</strong> ${data.monthly} kg CO₂</li>
                        <li><strong>Rocznie:</strong> ${data.yearly} kg CO₂ (${data.yearly_tons} t)</li>
                    </ul>
                    <div class="section-title mb-2">To odpowiada:</div>
                    <ul class="mb-0">
                        <li>${data.equivalents.trees_absorbed} drzew (pochłanianie CO₂ przez rok)</li>
                        <li>${data.equivalents.car_km} km przejazdu samochodem</li>
                    </ul>
                </div>
            </div>
        `;
    };

    if (simRun) {
        simRun.addEventListener("click", runSimulation);
    }
});
