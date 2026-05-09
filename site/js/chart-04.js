/**
 * Chart 04 — Felony-assault sub-categories, 2010 to 2024.
 *
 * Stacked column chart with five layers per year. Bars are 1.2 years wide for
 * visual breathing room, so x is treated as a numeric (linear) axis with
 * explicit ticks at the four data years. A horizontal dashed rule marks the
 * 2010 baseline (annotated on the right). A small inline annotation near the
 * 2010 column explains that Strangulation 1st is a statutory reclassification.
 *
 * Layer order (bottom → top):
 *   1. dv_in_catchall      magenta   "DV-driven (catch-all, ~39% share)"
 *   2. other_in_catchall   orange    "Other Assault 2/1/Unclassified"
 *   3. police_assault      neutral   "Assault on Police/Peace Officer"
 *   4. strangulation       navy      "Strangulation 1st (created Nov 2010)"
 *   5. other_subcats       light     "Other new sub-categories"
 *
 * Legend lives in HTML below the SVG so it can wrap into 2-3 columns.
 */
(function () {
  "use strict";
  const figure = document.getElementById("chart-04-container");
  if (!figure) return;
  const T = window.NYCStrategyChart;
  if (!T) return;

  T.mountChart(figure, async function ({ width, Plot }) {
    const resp = await fetch("data/chart-04.json");
    if (!resp.ok) throw new Error("Failed to fetch chart-04 data");
    const data = await resp.json();

    const baseline = data.baseline_2010;
    const rows = data.rows;

    // Layer definitions in stacking order (bottom → top).
    const layers = [
      { key: "dv_in_catchall",    label: "DV-driven (catch-all, ~39% share)",     color: T.palette.magenta },
      { key: "other_in_catchall", label: "Other Assault 2/1/Unclassified",        color: T.palette.orange },
      { key: "police_assault",    label: "Assault on Police/Peace Officer",       color: T.palette.neutral },
      { key: "strangulation",     label: "Strangulation 1st (created Nov 2010)",  color: T.palette.navy },
      { key: "other_subcats",     label: "Other new sub-categories",              color: T.palette.light },
    ];

    // Flatten to long format with explicit y1/y2 stacks. Computing the stack
    // ourselves (rather than using Plot.stackY) keeps the layer order locked
    // and avoids any tie-breaking surprises with the categorical fill scale.
    const segments = [];
    rows.forEach(function (r) {
      let cursor = 0;
      layers.forEach(function (lyr) {
        const v = r[lyr.key] || 0;
        if (v <= 0) {
          // Skip empty layers so we don't render zero-height rects.
          return;
        }
        segments.push({
          year: r.year,
          layer: lyr.label,
          value: v,
          y1: cursor,
          y2: cursor + v,
        });
        cursor += v;
      });
    });

    const yMax = 36000;
    const xDomain = [2008.5, 2026.5];
    const ticks = [2010, 2014, 2019, 2024];

    // Annotation placement — text near 2011, y ~ 30000; arrow toward the 2010
    // column at roughly the baseline.
    const annoText =
      "Strangulation acts existed before 2010\n" +
      "but were charged under Assault 2nd\n" +
      "or as a misdemeanor — the new class\n" +
      "is statutory reclassification.";
    const annoX = 2011.5;
    const annoY = 30500;
    const annoTargetX = 2010.6;
    const annoTargetY = baseline + 700;

    const marks = [
      // Stacked column layers. We use rectY with x1/x2 so each column is 1.2
      // years wide regardless of axis spacing — Plot.barY would coerce x to
      // a band scale, which fights the linear year axis we want.
      Plot.rectY(segments, {
        x1: function (d) { return d.year - 0.6; },
        x2: function (d) { return d.year + 0.6; },
        y1: "y1",
        y2: "y2",
        fill: "layer",
        stroke: "white",
        strokeWidth: 0.75,
      }),
      // 2010 baseline rule.
      Plot.ruleY([baseline], {
        stroke: T.palette.neutral,
        strokeDasharray: "4 4",
        strokeOpacity: 0.7,
        strokeWidth: 1,
      }),
      // Right-edge baseline label.
      Plot.text([{ x: 2025.2, y: baseline }], {
        x: "x",
        y: "y",
        textAnchor: "start",
        lineAnchor: "middle",
        dx: 4,
        text: function () {
          return "2010 baseline\n" + baseline.toLocaleString();
        },
        fill: T.palette.neutral,
        fontSize: 11,
        lineHeight: 1.2,
      }),
      // Annotation text (upper-left).
      Plot.text([{ x: annoX, y: annoY }], {
        x: "x",
        y: "y",
        textAnchor: "start",
        lineAnchor: "top",
        text: function () { return annoText; },
        fill: T.palette.navy,
        fontSize: 10.5,
        lineHeight: 1.3,
      }),
    ];

    // Plot.arrow exists in 0.6.x; fall back gracefully if a future build drops it.
    if (typeof Plot.arrow === "function") {
      marks.push(
        Plot.arrow([{ x1: annoX, y1: annoY, x2: annoTargetX, y2: annoTargetY }], {
          x1: "x1",
          y1: "y1",
          x2: "x2",
          y2: "y2",
          stroke: T.palette.navy,
          strokeWidth: 1,
          headLength: 6,
          bend: 0,
        })
      );
    }

    const svg = Plot.plot({
      width,
      height: 400,
      marginLeft: 70,
      marginRight: 80,
      marginTop: 30,
      marginBottom: 60,
      style: {
        background: "transparent",
        color: T.palette.ink,
        fontFamily: T.fonts.ui,
        fontSize: 12,
        overflow: "visible",
      },
      x: {
        type: "linear",
        domain: xDomain,
        ticks: ticks,
        // Explicit String() — Plot's default numeric formatter inserts a
        // thousands separator (2,010), which is wrong for years.
        tickFormat: function (d) { return String(d); },
        label: null,
      },
      y: {
        domain: [0, yMax],
        label: "Annual count",
        labelAnchor: "top",
        labelOffset: 50,
        grid: true,
        tickFormat: function (d) { return d ? (d / 1000) + "k" : "0"; },
      },
      color: {
        domain: layers.map(function (l) { return l.label; }),
        range: layers.map(function (l) { return l.color; }),
      },
      marks: marks,
    });

    // ---- HTML legend below the SVG. 2 columns on narrow viewports, 3 wider. ----
    const legend = document.createElement("ul");
    legend.className = "chart-04-legend";
    layers.forEach(function (lyr) {
      const li = document.createElement("li");
      li.className = "chart-04-legend-item";
      const sw = document.createElement("span");
      sw.className = "chart-04-swatch";
      sw.style.background = lyr.color;
      const lbl = document.createElement("span");
      lbl.className = "chart-04-legend-label";
      lbl.textContent = lyr.label;
      li.appendChild(sw);
      li.appendChild(lbl);
      legend.appendChild(li);
    });

    const outer = document.createElement("div");
    outer.appendChild(svg);
    outer.appendChild(legend);
    return outer;
  });
})();
