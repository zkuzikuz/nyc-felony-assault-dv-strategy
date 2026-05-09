/**
 * Chart 09 — B-HEARD breakdown.
 *
 * A single horizontal flow bar split into three colored segments:
 *   - "Got a B-HEARD team"      (navy,    24,071 / 47%)
 *   - "In-hours, no B-HEARD"    (orange,  13,042 / 25%)
 *   - "Overnight (no service)"  (magenta, 14,200 / 28%)
 *
 * Inside each segment, three lines of white text. Below the bar, two
 * annotation blocks (HTML) with up-arrows pointing at segments 2 and 3,
 * calling out the two distinct fixes (cause-tracking for in-hours, hour
 * extension for overnight). The bar + x-axis live in a Plot SVG; annotations
 * are positioned over the SVG using percentage anchors so they stay aligned
 * with the segment centers when the figure resizes.
 */
(function () {
  "use strict";
  const figure = document.getElementById("chart-09-container");
  if (!figure) return;
  const T = window.NYCStrategyChart;
  if (!T) return;

  // Map the data's `color` keys to the shared palette.
  const colorKeyMap = {
    structural: T.palette.navy,
    assault: T.palette.orange,
    dv: T.palette.magenta,
  };

  T.mountChart(figure, async function ({ width, Plot }) {
    const resp = await fetch("data/chart-09.json");
    if (!resp.ok) throw new Error("Failed to fetch chart-09 data");
    const data = await resp.json();

    const segments = data.segments;
    const total = data.total;

    // Build long-format rows with cumulative x1/x2 per segment.
    let cursor = 0;
    const rows = segments.map(function (s) {
      const x1 = cursor;
      const x2 = cursor + s.value;
      cursor = x2;
      const pct = Math.round((s.value / total) * 100);
      return {
        row: "calls",
        label: s.label,
        value: s.value,
        x1: x1,
        x2: x2,
        center: (x1 + x2) / 2,
        fill: colorKeyMap[s.color] || T.palette.neutral,
        pct: pct,
      };
    });

    // The three lines that go inside each segment. We render each line as a
    // separate Plot.text mark so we can offset them vertically with dy.
    const innerLine0 = rows.map(function (r) { return { row: "calls", x: r.center, text: r.label }; });
    const innerLine1 = rows.map(function (r) { return { row: "calls", x: r.center, text: r.value.toLocaleString() + " calls" }; });
    const innerLine2 = rows.map(function (r) { return { row: "calls", x: r.center, text: "(" + r.pct + "%)" }; });

    // x-axis: 0 .. 51,000 with ticks every 10k up to 50k.
    const xMax = 51000;
    const xTicks = [0, 10000, 20000, 30000, 40000, 50000];

    const marginLeft = 30;
    const marginRight = 30;

    const svg = Plot.plot({
      width,
      height: 130,
      marginLeft: marginLeft,
      marginRight: marginRight,
      marginTop: 14,
      marginBottom: 50,
      style: {
        background: "transparent",
        color: T.palette.ink,
        fontFamily: T.fonts.ui,
        fontSize: 12,
        overflow: "visible",
      },
      x: {
        domain: [0, xMax],
        label: "Eligible mental-health 911 calls per year (FY24) →",
        labelAnchor: "center",
        labelOffset: 36,
        ticks: xTicks,
        tickFormat: function (d) { return d.toLocaleString(); },
        grid: false,
      },
      y: {
        domain: ["calls"],
        label: null,
        ticks: [],
        tickSize: 0,
      },
      color: { type: "identity" },
      marks: [
        // The three colored segments. White stroke gives the same hairline
        // separation the matplotlib version had.
        Plot.barX(rows, {
          x1: "x1",
          x2: "x2",
          y: "row",
          fill: "fill",
          stroke: "white",
          strokeWidth: 2,
          insetTop: 6,
          insetBottom: 6,
        }),
        // In-bar text — three centered white lines per segment, placed at
        // dy = -16 / 0 / +16 so they read top / middle / bottom.
        Plot.text(innerLine0, {
          x: "x", y: "row", dy: -16, text: "text",
          fill: "white", fontWeight: 700, fontSize: 12, textAnchor: "middle",
        }),
        Plot.text(innerLine1, {
          x: "x", y: "row", dy: 0, text: "text",
          fill: "white", fontWeight: 700, fontSize: 12, textAnchor: "middle",
        }),
        Plot.text(innerLine2, {
          x: "x", y: "row", dy: 16, text: "text",
          fill: "white", fontWeight: 700, fontSize: 12, textAnchor: "middle",
        }),
      ],
    });

    // Build wrapper: SVG on top, then HTML annotation blocks aligned to
    // segment centers via percentage left.
    const wrapper = document.createElement("div");
    wrapper.className = "chart-09-wrapper";

    const svgWrap = document.createElement("div");
    svgWrap.className = "chart-09-svg-wrap";
    svgWrap.appendChild(svg);
    wrapper.appendChild(svgWrap);

    function pctLeftFor(centerVal) {
      const drawWidth = width - marginLeft - marginRight;
      const innerPct = centerVal / xMax;
      const px = marginLeft + innerPct * drawWidth;
      return (px / width) * 100;
    }

    const annotationsWrap = document.createElement("div");
    annotationsWrap.className = "chart-09-annotations";

    const annotations = [
      {
        center: rows[1].center,
        color: T.palette.orange,
        lines: [
          "Why these calls go unmet",
          "is not tracked in the audit.",
          "Cause-tracking is the fix.",
        ],
      },
      {
        center: rows[2].center,
        color: T.palette.magenta,
        lines: [
          "Program does not operate overnight.",
          "Extending hours adds about 14,000",
          "reachable calls.",
        ],
      },
    ];

    annotations.forEach(function (a) {
      const block = document.createElement("div");
      block.className = "chart-09-annotation";
      block.style.left = pctLeftFor(a.center) + "%";
      block.style.color = a.color;

      const arrow = document.createElement("span");
      arrow.className = "chart-09-arrow";
      arrow.setAttribute("aria-hidden", "true");
      arrow.style.color = a.color;
      arrow.textContent = "↑";
      block.appendChild(arrow);

      a.lines.forEach(function (line) {
        const p = document.createElement("div");
        p.className = "chart-09-annotation-line";
        p.textContent = line;
        block.appendChild(p);
      });

      annotationsWrap.appendChild(block);
    });

    wrapper.appendChild(annotationsWrap);
    return wrapper;
  });
})();
