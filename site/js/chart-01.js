/**
 * Chart 01 — Hero. The +72% headline overstates how much NYC felony assault
 * has actually grown; strip the 2010 strangulation reclassification and the
 * real behavioral rise is +47%.
 *
 * Two-panel layout:
 *   Left  — big-number callout in HTML (struck-through naive % over the
 *           orange adjusted %), drawn with an absolute-positioned bar so the
 *           strikethrough sits ABOVE the digits, not through them.
 *   Right — sparkline (Plot.line) of the naive total (light) and the
 *           strangulation-excluded total (orange), with dots on real data
 *           years and value annotations.
 */
(function () {
  "use strict";
  const figure = document.getElementById("chart-01-container");
  if (!figure) return;
  const T = window.NYCStrategyChart;
  if (!T) return;

  T.mountChart(figure, async function ({ width, Plot }) {
    const resp = await fetch("data/chart-01.json");
    if (!resp.ok) throw new Error("Failed to fetch chart-01 data");
    const data = await resp.json();

    const fmtInt = function (n) { return Math.round(n).toLocaleString(); };

    // ---- Outer two-column wrapper ----
    const outer = document.createElement("div");
    outer.className = "chart-01-grid";

    // ---------------- LEFT: big-number callout ----------------
    const left = document.createElement("div");
    left.className = "chart-01-bignum";

    // Row 1: struck-through naive headline (light grey)
    const naiveRow = document.createElement("div");
    naiveRow.className = "chart-01-naive";
    const naiveNum = document.createElement("span");
    naiveNum.className = "chart-01-naive-num";
    naiveNum.textContent = "+" + Math.round(data.headline_pct) + "%";
    const strike = document.createElement("span");
    strike.className = "chart-01-strike";
    strike.setAttribute("aria-hidden", "true");
    naiveRow.appendChild(naiveNum);
    naiveRow.appendChild(strike);

    // Row 2: adjusted figure (orange)
    const adjRow = document.createElement("div");
    adjRow.className = "chart-01-adj";
    adjRow.textContent = "+" + Math.round(data.adjusted_pct) + "%";

    // Caption + parenthetical
    const cap = document.createElement("div");
    cap.className = "chart-01-cap";
    cap.textContent = "real behavioral rise, 2010 to 2024";

    const sub = document.createElement("div");
    sub.className = "chart-01-cap-sub";
    sub.textContent = "(strangulation reclassification removed)";

    left.appendChild(naiveRow);
    left.appendChild(adjRow);
    left.appendChild(cap);
    left.appendChild(sub);

    // ---------------- RIGHT: sparkline ----------------
    const right = document.createElement("div");
    right.className = "chart-01-spark";

    // Title above the plot
    const sparkTitle = document.createElement("div");
    sparkTitle.className = "chart-01-spark-title";
    sparkTitle.textContent = "Annual felony-assault count, 2010–2024";

    // Tiny legend
    const legend = document.createElement("div");
    legend.className = "chart-01-legend";
    legend.innerHTML =
      '<span class="chart-01-legend-item">' +
        '<span class="chart-01-swatch" style="background:' + T.palette.light + '"></span>' +
        'as officially reported (+' + Math.round(data.headline_pct) + '%)' +
      '</span>' +
      '<span class="chart-01-legend-item">' +
        '<span class="chart-01-swatch" style="background:' + T.palette.orange + '"></span>' +
        'reclassification removed (+' + Math.round(data.adjusted_pct) + '%)' +
      '</span>';

    // Plot width: when stacked, fill full figure width; when side-by-side,
    // use roughly half. We let the right panel measure itself by reserving
    // a rough budget here and overriding via the responsive resize below.
    const isWide = width >= 600;
    const plotWidth = isWide ? Math.max(320, Math.round(width * 0.52) - 24) : Math.max(280, width - 8);

    const series = data.series;
    const dataYearRows = series.filter(function (d) { return d.is_data_year; });

    const yMax = Math.max.apply(null, series.map(function (d) {
      return Math.max(d.naive, d.adjusted);
    }));
    const yMin = Math.min.apply(null, series.map(function (d) {
      return Math.min(d.naive, d.adjusted);
    }));
    // Pad domain so annotation text sits within the SVG.
    const yPad = (yMax - yMin) * 0.18;

    const svg = Plot.plot({
      width: plotWidth,
      height: 280,
      marginLeft: 56,
      marginRight: 18,
      marginTop: 22,
      marginBottom: 32,
      style: {
        background: "transparent",
        color: T.palette.ink,
        fontFamily: T.fonts.ui,
        fontSize: 12,
        overflow: "visible",
      },
      x: {
        label: null,
        tickFormat: function (d) { return String(d); },
        ticks: [2010, 2012, 2014, 2016, 2018, 2020, 2022, 2024],
        domain: [2009.6, 2024.4],
      },
      y: {
        label: "Reports per year",
        labelAnchor: "top",
        labelOffset: 44,
        domain: [Math.max(0, yMin - yPad * 0.4), yMax + yPad],
        grid: true,
        tickFormat: function (d) {
          if (d >= 1000) return (d / 1000).toFixed(0) + "k";
          return String(d);
        },
      },
      marks: [
        // Naive total — light grey background line
        Plot.line(series, {
          x: "year",
          y: "naive",
          stroke: T.palette.light,
          strokeWidth: 2.0,
          curve: "linear",
        }),
        // Excluding Strangulation 1st — focal orange line, thicker
        Plot.line(series, {
          x: "year",
          y: "adjusted",
          stroke: T.palette.orange,
          strokeWidth: 3.0,
          curve: "linear",
        }),
        // Dots on real data years — naive
        Plot.dot(dataYearRows, {
          x: "year",
          y: "naive",
          r: 4.5,
          fill: T.palette.light,
          stroke: "white",
          strokeWidth: 1.2,
        }),
        // Dots on real data years — adjusted
        Plot.dot(dataYearRows, {
          x: "year",
          y: "adjusted",
          r: 5,
          fill: T.palette.orange,
          stroke: "white",
          strokeWidth: 1.2,
        }),
        // Annotate naive counts above the naive dots
        Plot.text(dataYearRows, {
          x: "year",
          y: "naive",
          text: function (d) { return fmtInt(d.naive); },
          dy: -10,
          fontSize: 10.5,
          fill: T.palette.neutral,
          textAnchor: "middle",
        }),
        // Gap connector at 2024 — the reclassification, drawn between the lines
        Plot.ruleX(dataYearRows.filter(function (d) { return d.year === 2024; }), {
          x: "year",
          y1: "adjusted",
          y2: "naive",
          stroke: T.palette.neutral,
          strokeWidth: 1.2,
          strokeDasharray: "3 3",
        }),
        // Annotate the adjusted (orange) endpoint below its dot, so +47% is legible
        Plot.text(dataYearRows.filter(function (d) { return d.year === 2024; }), {
          x: "year",
          y: "adjusted",
          text: function (d) { return fmtInt(d.adjusted); },
          dy: 16,
          fontSize: 10.5,
          fill: T.palette.orange,
          fontWeight: 700,
          textAnchor: "middle",
        }),
        // In-chart explanation, placed in the empty mid-left. Rendered as three
        // single-line marks because this Plot setup does not honor "\n" in text.
        Plot.text([{ x: 2010.3, y: yMin + (yMax - yMin) * 0.74 }], {
          x: "x", y: "y", dy: 0,
          text: function () { return "Gap between the lines = the 2010"; },
          textAnchor: "start", fontSize: 10.5, fill: T.palette.neutral,
        }),
        Plot.text([{ x: 2010.3, y: yMin + (yMax - yMin) * 0.74 }], {
          x: "x", y: "y", dy: 14,
          text: function () { return "strangulation reclassification"; },
          textAnchor: "start", fontSize: 10.5, fill: T.palette.neutral,
        }),
        Plot.text([{ x: 2010.3, y: yMin + (yMax - yMin) * 0.74 }], {
          x: "x", y: "y", dy: 28,
          text: function () { return "(a law change, not new behavior)"; },
          textAnchor: "start", fontSize: 10.5, fill: T.palette.neutral,
        }),
      ],
    });

    right.appendChild(sparkTitle);
    right.appendChild(legend);
    right.appendChild(svg);

    outer.appendChild(left);
    outer.appendChild(right);
    return outer;
  });
})();
