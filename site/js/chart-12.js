/**
 * Chart 12 — DV intervention rank.
 *
 * Range bars (lo → hi effect-size). Recommended programs (LAP, OFDVI) in
 * orange; others muted. Untested rows render a flat "—" tick at zero with the
 * label "untested or null". Cost annotations live in a small HTML grid below
 * the chart so the SVG stays clean and the page reflows responsively.
 */
(function () {
  "use strict";
  const figure = document.getElementById("chart-12-container");
  if (!figure) return;
  const T = window.NYCStrategyChart;
  if (!T) return;

  T.mountChart(figure, async function ({ width, Plot }) {
    const resp = await fetch("data/chart-12.json");
    if (!resp.ok) throw new Error("Failed to fetch chart-12 data");
    const rows = await resp.json();

    const order = rows.map(function (r) { return r.label; });
    const ranged = rows.filter(function (r) { return !r.untested; });
    const untested = rows.filter(function (r) { return r.untested; });

    const colorFor = function (r) {
      return r.recommended ? T.palette.orange : T.palette.neutral;
    };

    const svg = Plot.plot({
      width,
      height: 300,
      marginLeft: 280,
      marginRight: 90,
      marginTop: 12,
      marginBottom: 40,
      style: {
        background: "transparent",
        color: T.palette.ink,
        fontFamily: T.fonts.ui,
        fontSize: 13,
        overflow: "visible",
      },
      x: {
        domain: [-10, 50],
        label: "Effect on DV outcomes (% reduction)",
        labelAnchor: "right",
        labelOffset: 32,
        grid: true,
        tickFormat: function (d) { return d > 0 ? "+" + d + "%" : d + "%"; },
      },
      y: {
        domain: order,
        label: null,
        tickSize: 0,
        padding: 0.5,
      },
      marks: [
        Plot.ruleX([0], { stroke: T.palette.mute, strokeOpacity: 0.5 }),
        // Range bars for non-untested rows.
        Plot.barX(ranged, {
          x1: "lo",
          x2: "hi",
          y: "label",
          fill: colorFor,
          fillOpacity: 0.85,
          insetTop: 6,
          insetBottom: 6,
        }),
        // Midpoint dot for emphasis.
        Plot.dot(ranged, {
          x: "mid",
          y: "label",
          r: 4,
          fill: colorFor,
          stroke: T.palette.paper,
          strokeWidth: 1.5,
        }),
        // Right-edge value label, e.g. "35-45%".
        Plot.text(ranged, {
          x: "hi",
          y: "label",
          dx: 8,
          textAnchor: "start",
          text: function (d) { return d.lo + "-" + d.hi + "%"; },
          fill: colorFor,
          fontWeight: 700,
          fontSize: 13,
        }),
        // Untested rows: show "untested or null" near zero.
        Plot.text(untested, {
          x: 0,
          y: "label",
          dx: 8,
          textAnchor: "start",
          text: function () { return "untested or null"; },
          fill: T.palette.mute,
          fontStyle: "italic",
          fontSize: 13,
        }),
      ],
    });

    // Detail grid below the chart for cost + mechanism, keyed by short name.
    const grid = document.createElement("dl");
    grid.className = "chart-12-detail";
    rows.forEach(function (r) {
      const dt = document.createElement("dt");
      dt.textContent = r.short;
      if (r.recommended) dt.classList.add("is-recommended");
      const dd = document.createElement("dd");
      const cost = document.createElement("span");
      cost.className = "detail-cost";
      cost.textContent = r.cost;
      const desc = document.createElement("span");
      desc.className = "detail-desc";
      desc.textContent = r.description;
      dd.appendChild(cost);
      dd.appendChild(desc);
      grid.appendChild(dt);
      grid.appendChild(dd);
    });

    const outer = document.createElement("div");
    outer.appendChild(svg);
    outer.appendChild(grid);
    return outer;
  });
})();
