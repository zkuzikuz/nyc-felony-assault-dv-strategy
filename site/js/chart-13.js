/**
 * Chart 13 — DV / evidence-quality quadrant scatter.
 *
 * Ten programs plotted on (evidence quality, DV relevance). The top-right
 * quadrant — strong evidence and direct DV relevance — is faintly filled and
 * holds exactly two anchor programs (LAP, OFDVI), which are drawn larger and
 * labeled in bold orange. Quadrant divider rules sit at x=1.5 and y=1.5.
 */
(function () {
  "use strict";
  const figure = document.getElementById("chart-13-container");
  if (!figure) return;
  const T = window.NYCStrategyChart;
  if (!T) return;

  T.mountChart(figure, async function ({ width, Plot }) {
    const resp = await fetch("data/chart-13.json");
    if (!resp.ok) throw new Error("Failed to fetch chart-13 data");
    const data = await resp.json();

    // Map color keys (matching matplotlib palette in render_sketches.py)
    // to theme palette swatches.
    const colorMap = {
      assault: T.palette.orange,
      neutral: T.palette.neutral,
      light: "#bfbfbf", // a touch darker than palette.light so dot is visible
      dv: T.palette.magenta,
    };
    const fillFor = function (r) {
      return colorMap[r.color] || T.palette.neutral;
    };

    // Convert matplotlib `s` (point²-area) → SVG radius in pixels.
    // matplotlib: r_pt = sqrt(s/pi); 1pt ≈ 1.333px. Then divide by 2 to keep
    // the visual proportions modest in Plot's coordinate frame.
    const radiusFor = function (r) {
      const px = Math.sqrt(r.size / Math.PI) * 1.333;
      return Math.max(8, Math.min(20, px / 2 + 4));
    };

    const anchors = data.rows.filter(function (r) { return r.is_anchor; });
    const others = data.rows.filter(function (r) { return !r.is_anchor; });

    // Anchor the top-right annotation to the right edge so the full string
    // ("TOP RIGHT — DV-evaluated, strong evidence") fits inside the plot.
    const annotations = [
      { x: 3.35, y: 3.32, text: "TOP RIGHT — DV-evaluated, strong evidence",
        fill: T.palette.orange, weight: 700, anchor: "end" },
      { x: 0.05, y: 3.32, text: "DV-relevant but untested",
        fill: T.palette.magenta, weight: 700, anchor: "start" },
    ];

    return Plot.plot({
      width,
      height: 480,
      marginLeft: 60,
      marginRight: 30,
      marginTop: 20,
      marginBottom: 50,
      style: {
        background: "transparent",
        color: T.palette.ink,
        fontFamily: T.fonts.ui,
        fontSize: 12,
        overflow: "visible",
      },
      x: {
        domain: [0, 3.4],
        label: "Evidence quality (RCT > quasi-experimental > pre/post > null or untested)",
        labelAnchor: "center",
        labelOffset: 38,
        ticks: [0, 1, 2, 3],
        grid: false,
      },
      y: {
        domain: [0, 3.4],
        label: "DV relevance",
        labelAnchor: "center",
        labelOffset: 44,
        ticks: [0, 1, 2, 3],
        grid: false,
      },
      marks: [
        // Faint top-right quadrant fill.
        Plot.rect([{ x1: 1.5, x2: 3.4, y1: 1.5, y2: 3.4 }], {
          x1: "x1", x2: "x2", y1: "y1", y2: "y2",
          fill: T.palette.light,
          fillOpacity: 0.45,
        }),
        // Quadrant divider rules.
        Plot.ruleY([1.5], { stroke: T.palette.light, strokeWidth: 1 }),
        Plot.ruleX([1.5], { stroke: T.palette.light, strokeWidth: 1 }),

        // Non-anchor dots first (z-order).
        Plot.dot(others, {
          x: "x",
          y: "y",
          r: radiusFor,
          fill: fillFor,
          fillOpacity: 0.88,
          stroke: "white",
          strokeWidth: 2,
        }),
        // Non-anchor labels.
        Plot.text(others, {
          x: "x",
          y: "y",
          dx: 11,
          dy: -6, // SVG y is inverted; matplotlib offset (11, 6) = right + up
          textAnchor: "start",
          text: "label",
          fill: T.palette.neutral,
          fontSize: 11,
          fontWeight: 400,
        }),

        // Anchor dots on top.
        Plot.dot(anchors, {
          x: "x",
          y: "y",
          r: radiusFor,
          fill: fillFor,
          fillOpacity: 0.92,
          stroke: "white",
          strokeWidth: 2,
        }),
        // Anchor labels — bold, in their own color, slightly larger.
        Plot.text(anchors, {
          x: "x",
          y: "y",
          dx: 13,
          dy: -7,
          textAnchor: "start",
          text: "label",
          fill: fillFor,
          fontSize: 12,
          fontWeight: 700,
        }),

        // Corner annotations. Right one is right-anchored so it never clips
        // outside the plot frame; left one is left-anchored at the y-axis.
        Plot.text(annotations.filter(function (a) { return a.anchor === "end"; }), {
          x: "x", y: "y", text: "text",
          fill: function (d) { return d.fill; },
          fontWeight: function (d) { return d.weight; },
          fontSize: 12,
          textAnchor: "end",
        }),
        Plot.text(annotations.filter(function (a) { return a.anchor === "start"; }), {
          x: "x", y: "y", text: "text",
          fill: function (d) { return d.fill; },
          fontWeight: function (d) { return d.weight; },
          fontSize: 12,
          textAnchor: "start",
        }),
      ],
    });
  });
})();
