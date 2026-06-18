/**
 * Chart 07 — Announced supportive-housing capacity (Bridge to Home + Safe Haven).
 *
 * A single horizontal stacked bar showing the announced ~1,000-bed plan:
 * about 100 Bridge to Home beds plus 900 Safe Haven beds. Neutral greys read
 * as "what has been announced." There is no fabricated 2,000-bed target — the
 * plan is the plan; the recommendation is to operationalize and prioritize,
 * not to chase a higher bed count.
 */
(function () {
  "use strict";
  const figure = document.getElementById("chart-07-container");
  if (!figure) return;
  const T = window.NYCStrategyChart;
  if (!T) return;

  T.mountChart(figure, async function ({ width, Plot }) {
    const resp = await fetch("data/chart-07.json");
    if (!resp.ok) throw new Error("Failed to fetch chart-07 data");
    const data = await resp.json();

    const rows = data.rows;
    const order = rows.map(function (r) { return r.label; });

    // Long-format rows for the stacked bar: one row per segment.
    const segments = [];
    rows.forEach(function (r) {
      segments.push({ label: r.label, segment: "bth", x1: 0, x2: r.bth, fill: T.palette.neutral });
      segments.push({ label: r.label, segment: "safehaven", x1: r.bth, x2: r.bth + r.safehaven, fill: T.palette.light });
    });

    // x-axis: a little headroom past the 1,000-bed plan.
    const xMax = 1200;
    const xTicks = [0, 300, 600, 900, 1200];

    return Plot.plot({
      width,
      height: 180,
      marginLeft: 150,
      marginRight: 150,
      marginTop: 36,
      marginBottom: 44,
      style: {
        background: "transparent",
        color: T.palette.ink,
        fontFamily: T.fonts.ui,
        fontSize: 13,
        overflow: "visible",
      },
      x: {
        domain: [0, xMax],
        label: "Beds",
        labelAnchor: "center",
        labelOffset: 32,
        ticks: xTicks,
        tickFormat: function (d) { return d.toLocaleString(); },
        grid: false,
      },
      y: {
        domain: order,
        label: null,
        tickSize: 0,
        padding: 0.4,
        grid: false,
      },
      color: { type: "identity" },
      marks: [
        // Stacked segments.
        Plot.barX(segments, {
          y: "label",
          x1: "x1",
          x2: "x2",
          fill: "fill",
          insetTop: 4,
          insetBottom: 4,
        }),
        // BTH label — the 100-bed segment is too narrow to hold a label, so
        // anchor it at the right edge of the BTH bar and lift it above.
        Plot.text(rows, {
          x: function (d) { return d.bth; },
          y: "label",
          dx: 4,
          dy: -16,
          text: function (d) { return d.bth + " Bridge to Home"; },
          fill: T.palette.neutral,
          fontWeight: 700,
          fontSize: 11,
          textAnchor: "start",
        }),
        // Safe Haven label — centered in the Safe Haven segment.
        Plot.text(rows, {
          x: function (d) { return d.bth + d.safehaven / 2; },
          y: "label",
          text: function (d) { return d.safehaven.toLocaleString() + " Safe Haven beds"; },
          fill: T.palette.neutral,
          fontWeight: 700,
          fontSize: 12,
          textAnchor: "middle",
        }),
        // Total label, just outside the right edge of the bar.
        Plot.text(rows, {
          x: function (d) { return d.total; },
          y: "label",
          dx: 8,
          textAnchor: "start",
          text: function (d) { return "= " + d.total.toLocaleString() + " beds total"; },
          fill: T.palette.neutral,
          fontWeight: 500,
          fontSize: 12,
        }),
        Plot.ruleX([0], { stroke: T.palette.mute, strokeOpacity: 0.4 }),
      ],
    });
  });
})();
