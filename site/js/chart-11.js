/**
 * Chart 11 — Pilot timeline.
 *
 * Horizontal Gantt: each row is a phase of the pilot, spanning a [start, end]
 * range in months from pilot start. Color encodes intent (active pilot vs.
 * neutral background vs. structural milestone). A dashed vertical at month 30
 * marks the binding sunset gate.
 */
(function () {
  "use strict";
  const figure = document.getElementById("chart-11-container");
  if (!figure) return;
  const T = window.NYCStrategyChart;
  if (!T) return;

  const COLOR_FOR = {
    assault: T.palette.orange,
    neutral: T.palette.neutral,
    light: T.palette.light,
    structural: T.palette.navy,
  };

  T.mountChart(figure, async function ({ width, Plot }) {
    const resp = await fetch("data/chart-11.json");
    if (!resp.ok) throw new Error("Failed to fetch chart-11 data");
    const payload = await resp.json();
    const rows = payload.rows;
    const sunsetAt = payload.sunset_at != null ? payload.sunset_at : 30;

    // y-axis order, top-to-bottom = order of rows in JSON.
    const order = rows.map(function (r) { return r.label; });

    const fillFor = function (d) {
      return COLOR_FOR[d.color] || T.palette.neutral;
    };

    const tickValues = [0, 6, 12, 18, 24, 30, 36];

    const svg = Plot.plot({
      width,
      height: 280,
      marginLeft: 320,
      marginRight: 100,
      marginTop: 10,
      marginBottom: 40,
      style: {
        background: "transparent",
        color: T.palette.ink,
        fontFamily: T.fonts.ui,
        fontSize: 13,
        overflow: "visible",
      },
      x: {
        domain: [-1, 38],
        label: "Months from pilot start",
        labelAnchor: "right",
        labelOffset: 32,
        ticks: tickValues,
        tickFormat: function (d) { return "M" + d; },
      },
      y: {
        domain: order,
        label: null,
        tickSize: 0,
        padding: 0.5,
      },
      marks: [
        Plot.barX(rows, {
          x1: "start",
          x2: "end",
          y: "label",
          fill: fillFor,
          fillOpacity: 0.9,
          insetTop: 4,
          insetBottom: 4,
        }),
        // Sunset gate — dashed vertical at month 30.
        Plot.ruleX([sunsetAt], {
          stroke: T.palette.neutral,
          strokeDasharray: "5 4",
          strokeWidth: 1.5,
        }),
        // Annotation to the right of the sunset line, top of plot.
        Plot.text([{ x: sunsetAt + 0.6, y: order[0], text: "Sunset clause\nbinding at M30" }], {
          x: "x",
          y: "y",
          text: "text",
          textAnchor: "start",
          dy: -2,
          lineAnchor: "top",
          fill: T.palette.neutral,
          fontWeight: 700,
          fontSize: 12,
        }),
      ],
    });

    return svg;
  });
})();
