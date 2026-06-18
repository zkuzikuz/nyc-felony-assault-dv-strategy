/**
 * Chart 03 — DV split.
 *
 * Two-panel composition. Left: growth rates 2017→2024 for "Domestic + elder
 * assault" (+73%, magenta) vs "Other felony assault" (+40%, neutral) as a
 * small horizontal bar chart with bold right-edge value labels. Right: a
 * single-row stacked bar showing the 2024 share — DV / household at 39%
 * (11,505 cases) in magenta, Other at 61% (17,996 cases) in light grey,
 * with inline labels inside each segment.
 *
 * Each panel is its own Plot.plot() SVG, paired with a small italic panel
 * title in HTML. Both are placed in a CSS grid that collapses to a single
 * column on narrow viewports.
 */
(function () {
  "use strict";
  const figure = document.getElementById("chart-03-container");
  if (!figure) return;
  const T = window.NYCStrategyChart;
  if (!T) return;

  T.mountChart(figure, async function ({ width, Plot }) {
    const resp = await fetch("data/chart-03.json");
    if (!resp.ok) throw new Error("Failed to fetch chart-03 data");
    const data = await resp.json();

    // Layout — match the CSS grid (1.2fr / 1fr) so each Plot sizes itself.
    const isNarrow = width < 600;
    const gap = 24;
    const leftFrac = 1.2 / 2.2;
    const rightFrac = 1 / 2.2;
    const leftWidth = isNarrow
      ? width
      : Math.max(260, Math.floor(width * leftFrac - gap / 2));
    const rightWidth = isNarrow
      ? width
      : Math.max(220, Math.floor(width * rightFrac - gap / 2));

    // ---- Left panel: growth rates ----
    const growth = data.growth.map(function (d) {
      return {
        label: d.label,
        pct: d.pct,
        color: d.color === "dv" ? T.palette.magenta : T.palette.neutral,
      };
    });
    const growthOrder = growth.map(function (d) { return d.label; });

    const leftSvg = Plot.plot({
      width: leftWidth,
      height: 200,
      marginLeft: 165,
      marginRight: 60,
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
        domain: [0, 100],
        label: "Growth, 2017 to 2024",
        labelAnchor: "right",
        labelOffset: 32,
        grid: true,
        tickFormat: function (d) { return d + "%"; },
      },
      y: {
        domain: growthOrder,
        label: null,
        tickSize: 0,
        padding: 0.45,
      },
      marks: [
        Plot.barX(growth, {
          x: "pct",
          y: "label",
          fill: function (d) { return d.color; },
          insetTop: 4,
          insetBottom: 4,
        }),
        Plot.text(growth, {
          x: "pct",
          y: "label",
          dx: 8,
          textAnchor: "start",
          text: function (d) { return "+" + d.pct + "%"; },
          fill: function (d) { return d.color; },
          fontWeight: 700,
          fontSize: 18,
        }),
        Plot.ruleX([0], { stroke: T.palette.mute, strokeOpacity: 0.4 }),
      ],
    });

    // ---- Right panel: 2024 share (single-row stacked bar) ----
    const share = data.share;
    const segments = [
      {
        key: "dv",
        label: "DV / household",
        count: share.dv_count,
        pct: share.dv_share_pct,
        color: T.palette.magenta,
        textColor: "#ffffff",
      },
      {
        key: "other",
        label: "Other felony assault",
        count: share.other_count,
        pct: 100 - share.dv_share_pct,
        color: T.palette.light,
        textColor: T.palette.ink,
      },
    ];
    // Compute x ranges for stacking.
    let cursor = 0;
    segments.forEach(function (s) {
      s.x1 = cursor;
      s.x2 = cursor + s.count;
      s.mid = (s.x1 + s.x2) / 2;
      cursor = s.x2;
    });
    const total = cursor;

    const rightSvg = Plot.plot({
      width: rightWidth,
      height: 200,
      marginLeft: 8,
      marginRight: 8,
      marginTop: 24,
      marginBottom: 40,
      style: {
        background: "transparent",
        color: T.palette.ink,
        fontFamily: T.fonts.ui,
        fontSize: 13,
        overflow: "visible",
      },
      x: {
        domain: [0, total],
        axis: null,
      },
      y: {
        domain: ["share"],
        axis: null,
        padding: 0.05,
      },
      marks: [
        Plot.barX(segments, {
          x1: "x1",
          x2: "x2",
          y: function () { return "share"; },
          fill: function (d) { return d.color; },
        }),
        Plot.text(segments, {
          x: "mid",
          y: function () { return "share"; },
          textAnchor: "middle",
          lineAnchor: "middle",
          fill: function (d) { return d.textColor; },
          fontWeight: 700,
          fontSize: 11,
          lineHeight: 1.3,
          text: function (d) {
            return d.label + "\n" + d.count.toLocaleString() + " cases\n(~" + d.pct + "%)";
          },
        }),
      ],
    });

    // ---- Compose: two panels (each = title + svg) inside a grid wrapper. ----
    const outer = document.createElement("div");
    outer.className = "chart-03-grid";

    const leftPanel = document.createElement("div");
    leftPanel.className = "chart-03-panel";
    const leftTitle = document.createElement("p");
    leftTitle.className = "panel-title";
    leftTitle.textContent = "Growth rates, 2017 to 2024";
    leftPanel.appendChild(leftTitle);
    leftPanel.appendChild(leftSvg);

    const rightPanel = document.createElement("div");
    rightPanel.className = "chart-03-panel";
    const rightTitle = document.createElement("p");
    rightTitle.className = "panel-title";
    rightTitle.textContent =
      "2025 share of all " + share.total_2025.toLocaleString() + " felony assaults";
    rightPanel.appendChild(rightTitle);
    rightPanel.appendChild(rightSvg);

    outer.appendChild(leftPanel);
    outer.appendChild(rightPanel);
    return outer;
  });
})();
