document.addEventListener("DOMContentLoaded", () => {
    const drawGlobal = () => {
        const c = document.getElementById("chartGlobal");
        if (!c) {
            return;
        }
        const x = c.getContext("2d");
        c.width = c.clientWidth;
        c.height = c.clientHeight;

        const years = [1850, 1900, 1950, 1970, 1990, 2000, 2010, 2020, 2023];
        const vals = [2, 3, 6, 15, 22, 25, 30, 34, 36.8];

        const ML = 50;
        const MR = 20;
        const MT = 20;
        const MB = 30;
        const W = c.width - ML - MR;
        const H = c.height - MT - MB;
        const max = Math.max(...vals) * 1.2;

        const xx = (i) => ML + (i / (vals.length - 1)) * W;
        const yy = (v) => MT + H - (v / max) * H;

        x.clearRect(0, 0, c.width, c.height);
        x.strokeStyle = "#ccc";
        for (let i = 0; i < 5; i += 1) {
            const yy2 = MT + H * (i / 4);
            x.beginPath();
            x.moveTo(ML, yy2);
            x.lineTo(ML + W, yy2);
            x.stroke();
        }

        x.strokeStyle = "#2b8a3e";
        x.lineWidth = 3;
        x.beginPath();
        x.moveTo(xx(0), yy(vals[0]));
        for (let i = 1; i < vals.length; i += 1) {
            x.lineTo(xx(i), yy(vals[i]));
        }
        x.stroke();

        vals.forEach((v, i) => {
            x.beginPath();
            x.arc(xx(i), yy(v), 5, 0, Math.PI * 2);
            x.fillStyle = "#2b8a3e";
            x.fill();
            x.fillStyle = "#222";
            x.fillText(years[i], xx(i) - 10, c.height - 5);
        });
    };

    const drawSectors = () => {
        const c = document.getElementById("chartSectors");
        if (!c) {
            return;
        }
        const x = c.getContext("2d");
        c.width = c.clientWidth;
        c.height = c.clientHeight;

        const data = {
            Energia: 40,
            Transport: 20,
            Przemysł: 15,
            Rolnictwo: 12,
            Budynki: 6,
            Odpady: 2
        };
        const entries = Object.entries(data);
        const max = 40;
        const barW = c.width / entries.length - 20;

        x.clearRect(0, 0, c.width, c.height);
        entries.forEach((e, i) => {
            const h = (e[1] / max) * (c.height - 50);
            x.fillStyle = "#2b8a3e";
            x.fillRect(10 + i * (barW + 15), c.height - 30 - h, barW, h);
            x.fillStyle = "#222";
            x.fillText(e[0], 10 + i * (barW + 15), c.height - 10);
        });
    };

    const drawPolandEU = () => {
        const c = document.getElementById("chartPolandEU");
        if (!c) {
            return;
        }
        const x = c.getContext("2d");
        c.width = c.clientWidth;
        c.height = c.clientHeight;

        const lab = ["USA", "Australia", "Polska", "UE", "Świat"];
        const val = [14, 16, 8, 6.4, 4.7];
        const max = 16;
        const barW = c.width / lab.length - 20;

        x.clearRect(0, 0, c.width, c.height);
        lab.forEach((l, i) => {
            const h = (val[i] / max) * (c.height - 50);
            x.fillStyle = "#2b8a3e";
            x.fillRect(10 + i * (barW + 15), c.height - 30 - h, barW, h);
            x.fillStyle = "#222";
            x.fillText(l, 10 + i * (barW + 15), c.height - 10);
        });
    };

    const drawEnergyMix = () => {
        const c = document.getElementById("chartEnergyMix");
        if (!c) {
            return;
        }
        const x = c.getContext("2d");
        c.width = c.clientWidth;
        c.height = c.clientHeight;

        const data = { "Węgiel": 64, Gaz: 17, OZE: 19 };
        const max = 64;
        const entries = Object.entries(data);
        const barW = c.width / entries.length - 30;

        x.clearRect(0, 0, c.width, c.height);
        entries.forEach((e, i) => {
            const h = (e[1] / max) * (c.height - 50);
            x.fillStyle = "#2b8a3e";
            x.fillRect(15 + i * (barW + 25), c.height - 30 - h, barW, h);
            x.fillStyle = "#222";
            x.fillText(e[0], 15 + i * (barW + 25), c.height - 10);
        });
    };

    const drawTransport = () => {
        const c = document.getElementById("chartTransport");
        if (!c) {
            return;
        }
        const x = c.getContext("2d");
        c.width = c.clientWidth;
        c.height = c.clientHeight;

        const data = { Samolot: 255, Samochód: 180, Autobus: 105, Pociąg: 41, Rower: 0 };
        const max = 255;
        const entries = Object.entries(data);
        const barW = c.width / entries.length - 20;

        x.clearRect(0, 0, c.width, c.height);
        entries.forEach((e, i) => {
            const h = (e[1] / max) * (c.height - 50);
            x.fillStyle = "#2b8a3e";
            x.fillRect(10 + i * (barW + 15), c.height - 30 - h, barW, h);
            x.fillStyle = "#222";
            x.fillText(e[0], 10 + i * (barW + 15), c.height - 10);
        });
    };

    const drawFood = () => {
        const c = document.getElementById("chartFood");
        if (!c) {
            return;
        }
        const x = c.getContext("2d");
        c.width = c.clientWidth;
        c.height = c.clientHeight;

        const foods = { Wołowina: 27, Wieprzowina: 12, Drób: 7, Ryby: 5, Warzywa: 2 };
        const max = 27;
        const entries = Object.entries(foods);
        const barW = c.width / entries.length - 20;

        x.clearRect(0, 0, c.width, c.height);
        entries.forEach((e, i) => {
            const h = (e[1] / max) * (c.height - 50);
            x.fillStyle = "#2b8a3e";
            x.fillRect(10 + i * (barW + 15), c.height - 30 - h, barW, h);
            x.fillStyle = "#222";
            x.fillText(e[0], 10 + i * (barW + 15), c.height - 10);
        });
    };

    const drawGlobalEnergy = () => {
        const c = document.getElementById("chartGlobalEnergy");
        if (!c) {
            return;
        }
        const x = c.getContext("2d");
        c.width = c.clientWidth;
        c.height = c.clientHeight;

        const data = { "Węgiel": 36, Gaz: 22, Ropa: 28, OZE: 12, Atom: 4 };
        const entries = Object.entries(data);
        const max = 36;
        const barW = c.width / entries.length - 25;

        x.clearRect(0, 0, c.width, c.height);
        entries.forEach((e, i) => {
            const h = (e[1] / max) * (c.height - 50);
            x.fillStyle = "#2b8a3e";
            x.fillRect(10 + i * (barW + 15), c.height - 30 - h, barW, h);
            x.fillStyle = "#222";
            x.fillText(e[0], 10 + i * (barW + 15), c.height - 10);
        });
    };

    const redrawAll = () => {
        drawGlobal();
        drawSectors();
        drawPolandEU();
        drawEnergyMix();
        drawTransport();
        drawFood();
        drawGlobalEnergy();
    };

    redrawAll();
    window.addEventListener("resize", redrawAll);

    const tabButtons = document.querySelectorAll('#infoTabs button[data-bs-toggle="pill"]');
    tabButtons.forEach((btn) => {
        btn.addEventListener("shown.bs.tab", redrawAll);
    });
});
