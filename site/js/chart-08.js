/**
 * Chart 08 — Distal driver. Two indexed time series on the same axis (2014 = 100):
 * NYC felony assault rises (orange, solid, four points), NY State inpatient
 * psychiatric beds fall (navy, dashed, two endpoints). Each dot is annotated
 * with its index value and raw count; fa labels sit above their dots, beds
 * labels below. A faint horizontal rule at 100 is the index baseline. A small
 * HTML legend renders above the SVG.
 */
(function () {
  "use strict";
  const figure = document.getElementById("chart-08-container");
  if (!figure) return;
  const T = window.NYCStrategyChart;
  if (!T) return;

  T.mountChart(figure, async function ({ width, Plot }) {
    const resp = await fetch("data/chart-08.json");
    if (!resp.ok) throw new Error("Failed to fetch chart-08 data");
    const data = await resp.json();

    const fa = data.fa;     // [{year, raw, index}]
    const beds = data.beds; // [{year, raw, index}]

    const fmt = function (raw) {
      return Number(raw).toLocaleString();
    };

    const svg = Plot.plot({
      width,
      height: 320,
      marginLeft: 60,
      marginRight: 90,
      marginTop: 30,
      marginBottom: 36,
      style: {
        background: "transparent",
        color: T.palette.ink,
        fontFamily: T.fonts.ui,
        fontSize: 13,
        overflow: "visible",
      },
      x: {
        domain: [2009, 2025],
        label: null,
        tickFormat: function (d) { return String(d); },
        ticks: [2010, 2012, 2014, 2016, 2018, 2020, 2022, 2024],
      },
      y: {
        domain: [60, 160],
        label: "Index — both series, 2014 = 100  ",
        labelArrow: "none",
        labelAnchor: "top",
        labelOffset: 44,
        grid: true,
        tickFormat: function (d) { return String(d); },
      },
      marks: [
        // Reference rule at index = 100 with right-edge label.
        Plot.ruleY([100], {
          stroke: T.palette.mute,
          strokeOpacity: 0.5,
          strokeWidth: 0.8,
        }),
        Plot.text([{ x: 2025, y: 100 }], {
          x: "x",
          y: "y",
          dx: 4,
          textAnchor: "start",
          text: function () { return "2014 = 100"; },
          fill: T.palette.neutral,
          fontSize: 11,
        }),

        // Beds — navy, dashed.
        Plot.line(beds, {
          x: "year",
          y: "index",
          stroke: T.palette.navy,
          strokeWidth: 2.6,
          strokeDasharray: "6 4",
        }),
        Plot.dot(beds, {
          x: "year",
          y: "index",
          r: 5,
          fill: T.palette.navy,
          stroke: T.palette.paper,
          strokeWidth: 1.5,
        }),
        // Beds annotations BELOW dots (two-line: index + raw).
        Plot.text(beds, {
          x: "year",
          y: "index",
          dy: 22,
          textAnchor: "middle",
          lineAnchor: "middle",
          text: function (d) {
            return d.index.toFixed(0) + "\n(" + fmt(d.raw) + ")";
          },
          fill: T.palette.navy,
          fontSize: 11,
          lineHeight: 1.15,
        }),

        // Felony assault — orange, solid, thicker.
        Plot.line(fa, {
          x: "year",
          y: "index",
          stroke: T.palette.orange,
          strokeWidth: 2.6,
        }),
        Plot.dot(fa, {
          x: "year",
          y: "index",
          r: 5,
          fill: T.palette.orange,
          stroke: T.palette.paper,
          strokeWidth: 1.5,
        }),
        // Felony assault annotations ABOVE dots.
        Plot.text(fa, {
          x: "year",
          y: "index",
          dy: -22,
          textAnchor: "middle",
          lineAnchor: "middle",
          text: function (d) {
            return d.index.toFixed(0) + "\n(" + fmt(d.raw) + ")";
          },
          fill: T.palette.orange,
          fontSize: 11,
          lineHeight: 1.15,
        }),
      ],
    });

    // HTML legend above the chart.
    const legend = document.createElement("div");
    legend.className = "chart-08-legend";
    legend.style.display = "flex";
    legend.style.flexWrap = "wrap";
    legend.style.gap = "18px";
    legend.style.fontFamily = T.fonts.ui;
    legend.style.fontSize = "13px";
    legend.style.color = T.palette.ink;
    legend.style.marginBottom = "6px";

    function legendItem(color, label) {
      const item = document.createElement("span");
      item.style.display = "inline-flex";
      item.style.alignItems = "center";
      item.style.gap = "6px";
      const sw = document.createElement("span");
      sw.style.display = "inline-block";
      sw.style.width = "14px";
      sw.style.height = "14px";
      sw.style.background = color;
      sw.style.borderRadius = "2px";
      const tx = document.createElement("span");
      tx.textContent = label;
      item.appendChild(sw);
      item.appendChild(tx);
      return item;
    }

    legend.appendChild(legendItem(T.palette.orange, "NYC felony assault"));
    legend.appendChild(legendItem(T.palette.navy, "NY State inpatient psychiatric beds"));

    const outer = document.createElement("div");
    outer.appendChild(legend);
    outer.appendChild(svg);
    return outer;
  });
})();
