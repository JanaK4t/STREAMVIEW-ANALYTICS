// python -m http.server
// http://localhost:8000
d3.csv("data/movies_limpio.csv").then(data => {
    data.forEach(d => {
        d.budget = +d.budget || +d.presupuesto || 0;
        d.revenue = +d.revenue || +d.ingresos || 0;
        d.release_year = +d.release_year || 0;
        d.vote_average = +d.vote_average || 0;
        d.type = d.type || "Movie";
        
        d.genresList = d.genres ? d.genres.split(",").map(g => g.trim()) : [];
        
        d.countriesList = d.country ? d.country.split(",").map(c => c.trim()) : [];
    });

    function populateDropdown(id, key) {
        let values;
        if (key === "genresList" || key === "countriesList") {
            values = Array.from(new Set(data.flatMap(d => d[key]))).filter(Boolean).sort();
        } else {
            values = Array.from(new Set(data.map(d => d[key]))).filter(Boolean).sort();
        }
        
        const select = d3.select(id);
        values.forEach(val => {
            select.append("option").text(val).property("value", val);
        });
    }

    populateDropdown("#filter-genre", "genresList");
    populateDropdown("#filter-country", "countriesList");
    populateDropdown("#filter-language", "language");
    populateDropdown("#filter-rating", "rating");

    function updateDashboard() {
        const fGenre = d3.select("#filter-genre").property("value");
        const fCountry = d3.select("#filter-country").property("value");
        const fLang = d3.select("#filter-language").property("value");
        const fRating = d3.select("#filter-rating").property("value");
        const yMin = +d3.select("#filter-year-min").property("value");
        const yMax = +d3.select("#filter-year-max").property("value");

        let filtered = data.filter(d => {
            return (fGenre === "All" || d.genresList.includes(fGenre)) &&
                   (fCountry === "All" || d.countriesList.includes(fCountry)) &&
                   (fLang === "All" || d.language === fLang) &&
                   (fRating === "All" || d.rating === fRating) &&
                   (d.release_year >= yMin && d.release_year <= yMax);
        });

        let financialValid = filtered.filter(d => d.budget > 0 && d.revenue > 0);
        
        financialValid.forEach(d => {
            d.roi = ((d.revenue - d.budget) / d.budget) * 100;
        });

        const totBudget = d3.sum(financialValid, d => d.budget);
        const totRevenue = d3.sum(financialValid, d => d.revenue);
        const avgBudget = financialValid.length ? totBudget / financialValid.length : 0;
        const avgRoi = financialValid.length ? d3.mean(financialValid, d => d.roi) : 0;

        d3.select("#kpi-budget").text("\$" + totBudget.toLocaleString());
        d3.select("#kpi-revenue").text("\$" + totRevenue.toLocaleString());
        d3.select("#kpi-avg-budget").text("\$" + avgBudget.toLocaleString());
        d3.select("#kpi-roi").text(avgRoi.toFixed(1) + "%");

        renderBarChart(financialValid);
        renderScatterPlot(financialValid);
    }

    function renderScatterPlot(validData) {
        d3.select("#scatter-chart").html("");
        const margin = {top: 20, right: 30, bottom: 40, left: 80},
              width = 700 - margin.left - margin.right,
              height = 350 - margin.top - margin.bottom;

        const svg = d3.select("#scatter-chart").append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform", `translate(${margin.left},${margin.top})`);

        const x = d3.scaleLinear()
            .domain([0, d3.max(validData, d => d.budget) || 100])
            .range([0, width]);

        svg.append("g").attr("transform", `translate(0,${height})`).call(d3.axisBottom(x).ticks(5));

        const y = d3.scaleLinear()
            .domain([0, d3.max(validData, d => d.revenue) || 100])
            .range([height, 0]);

        svg.append("g").call(d3.axisLeft(y));

        svg.selectAll("circle")
            .data(validData)
            .enter()
            .append("circle")
            .attr("cx", d => x(d.budget))
            .attr("cy", d => y(d.revenue))
            .attr("r", 5)
            .style("fill", "#3b82f6")
            .style("opacity", 0.7)
            .append("title")
            .text(d => `${d.title}\nPresupuesto: $${d.budget}\nIngresos: $${d.revenue}`);
    }

    function renderBarChart(validData) {
        d3.select("#bar-chart").html("");
        const topData = [...validData].sort((a, b) => b.revenue - a.revenue).slice(0, 10);

        const margin = {top: 10, right: 30, bottom: 30, left: 120},
              width = 700 - margin.left - margin.right,
              height = 300 - margin.top - margin.bottom;

        const svg = d3.select("#bar-chart").append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform", `translate(${margin.left},${margin.top})`);

        const x = d3.scaleLinear()
            .domain([0, d3.max(topData, d => d.revenue) || 100])
            .range([0, width]);

        svg.append("g").attr("transform", `translate(0,${height})`).call(d3.axisBottom(x).ticks(5));

        const y = d3.scaleBand()
            .domain(topData.map(d => d.title))
            .range([0, height])
            .padding(0.1);

        svg.append("g").call(d3.axisLeft(y));

        svg.selectAll("rect")
            .data(topData)
            .enter()
            .append("rect")
            .attr("x", x(0))
            .attr("y", d => y(d.title))
            .attr("width", d => x(d.revenue))
            .attr("height", y.bandwidth())
            .attr("fill", "#69b3a2");
    }

    d3.selectAll("select, input").on("change input", updateDashboard);
    updateDashboard();
});