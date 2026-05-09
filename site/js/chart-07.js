/**
 * Chart 07 — Bed capacity (Bridge to Home + Safe Haven) against the
 * Mayor's announced 2,000-person target.
 *
 * Two horizontal stacked bars. Today (existing) uses neutral greys to read
 * as "what exists"; Recommended uses the campaign orange to read as "what's
 * needed". A vertical dashed orange rule sits at the 2,000-bed target.
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
    const target = data.target;

    // y-domain in display order. Today on top, Recommended below.
    const order = rows.map(function (r) { return r.label; });

    // Per-row colour assignments. Index 0 = Today, 1 = Recommended.
    const colorBth = [T.palette.neutral, T.palette.orange];
    const colorSh  = [T.palette.light,   T.palette.orange];
    // Text colours.
    // BTH labels are anchored just right of the BTH segment (matching the
    // matplotlib reference) so they sit on the Safe Haven segment. On Today
    // that means dark text on a light background; on Recommended the BTH
    // text sits on orange so we use white.
    const bthTextColor = [T.palette.neutral, "white"];
    // Safe Haven labels are centered inside the Safe Haven segment.
    const shTextColor  = [T.palette.neutral, "white"];

    // Long-format rows for stacked bars: one row per segment with explicit
    // x1/x2 + fill, so colour is taken from the data literally.
    const segments = [];
    rows.forEach(function (r, i) {
      segments.push({
        label: r.label,
        segment: "bth",
        x1: 0,
        x2: r.bth,
        fill: colorBth[i],
      });
      segments.push({
        label: r.label,
        segment: "safehaven",
        x1: r.bth,
        x2: r.bth + r.safehaven,
        fill: colorSh[i],
      });
    });

    // x-axis: 0 .. 2500 with ticks every 500.
    const xMax = 2500;
    const xTicks = [0, 500, 1000, 1500, 2000, 2500];

    return Plot.plot({
      width,
      height: 240,
      marginLeft: 240,
      marginRight: 110,
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
        // Stacked segments — one bar per (row, segment) pair.
        Plot.barX(segments, {
          y: "label",
          x1: "x1",
          x2: "x2",
          fill: "fill",
          insetTop: 4,
          insetBottom: 4,
        }),
        // BTH label — Today row. The 100-bed segment is too narrow to hold
        // a label, so we anchor it at the right edge of the BTH bar and
        // lift it above the bar so it does not collide with the Safe Haven
        // label below.
        Plot.text([rows[0]], {
          x: function (d) { return d.bth; },
          y: "label",
          dx: 4,
          dy: -16,
          text: function (d) { return d.bth + " BTH"; },
          fill: bthTextColor[0],
          fontWeight: 700,
          fontSize: 11,
          textAnchor: "start",
        }),
        // BTH label — Recommended row. Both segments are orange, so we
        // anchor the label flush with the left edge of the bar and let it
        // read across the colour-uniform stack.
        Plot.text([rows[1]], {
          x: 0,
          y: "label",
          dx: 8,
          text: function (d) { return d.bth + " BTH"; },
          fill: bthTextColor[1],
          fontWeight: 700,
          fontSize: 11,
          textAnchor: "start",
        }),
        // Safe Haven labels — centered in the Safe Haven segment.
        Plot.text(rows, {
          x: function (d) { return d.bth + d.safehaven / 2; },
          y: "label",
          text: function (d) { return d.safehaven.toLocaleString() + " Safe Haven beds"; },
          fill: function (d, i) { return shTextColor[i]; },
          fontWeight: 700,
          fontSize: 12,
          textAnchor: "middle",
        }),
        // Total label, just outside the right edge of each bar.
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
        // Target rule + annotation.
        Plot.ruleX([target], {
          stroke: T.palette.orange,
          strokeWidth: 2,
          strokeDasharray: "4 4",
        }),
        // Target annotation, two lines, sitting just above the top bar and
        // immediately right of the dashed rule. Plot.text takes `dy` as a
        // constant only, so the two lines render as two marks.
        Plot.text([{ x: target, y: order[0] }], {
          x: "x",
          y: "y",
          text: function () { return "2,000-person"; },
          dx: 6,
          dy: -28,
          textAnchor: "start",
          fill: T.palette.orange,
          fontWeight: 700,
          fontSize: 11,
        }),
        Plot.text([{ x: target, y: order[0] }], {
          x: "x",
          y: "y",
          text: function () { return "announced target"; },
          dx: 6,
          dy: -14,
          textAnchor: "start",
          fill: T.palette.orange,
          fontWeight: 700,
          fontSize: 11,
        }),
        Plot.ruleX([0], { stroke: T.palette.mute, strokeOpacity: 0.4 }),
      ],
    });
  });
})();
