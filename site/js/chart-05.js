/**
 * Chart 05 — Trajectories of NYC's four violent-felony categories, indexed to
 * 2017 = 1.0. Felony Assault is the focal series (orange, thick); Murder,
 * Robbery, and Rape render as faint grey peers. Endpoints are direct-labeled
 * on the right so no legend is needed. A faint horizontal rule at 1.0 anchors
 * the index, and a dotted vertical at 2020 marks COVID.
 */
(function () {
  "use strict";
  const figure = document.getElementById("chart-05-container");
  if (!figure) return;
  const T = window.NYCStrategyChart;
  if (!T) return;

  T.mountChart(figure, async function ({ width, Plot }) {
    const resp = await fetch("data/chart-05.json");
    if (!resp.ok) throw new Error("Failed to fetch chart-05 data");
    const data = await resp.json();

    const focalKey = data.focal; // "Felony Assault"
    const otherKeys = ["Murder", "Robbery", "Rape"];

    const focalSeries = data.series[focalKey];
    const otherSeries = otherKeys.map(function (k) {
      return { name: k, points: data.series[k] };
    });

    const otherLabel = "#888888";
    const otherStroke = "#aaaaaa";

    const marks = [
      // Reference rule at index = 1.0
      Plot.ruleY([1.0], {
        stroke: T.palette.mute,
        strokeOpacity: 0.4,
      }),
      // COVID vertical marker
      Plot.ruleX([2020], {
        stroke: T.palette.mute,
        strokeDasharray: "2 3",
        strokeOpacity: 0.35,
      }),
      Plot.text([{ year: 2020, label: "COVID" }], {
        x: "year",
        y: 0.55,
        text: "label",
        fill: T.palette.mute,
        fontSize: 11,
        textAnchor: "middle",
      }),
    ];

    // Other (light) series — line + endpoint label
    otherSeries.forEach(function (s) {
      marks.push(
        Plot.line(s.points, {
          x: "year",
          y: "value",
          stroke: otherStroke,
          strokeWidth: 1.4,
        })
      );
      const last = s.points[s.points.length - 1];
      marks.push(
        Plot.text([last], {
          x: "year",
          y: "value",
          dx: 6,
          textAnchor: "start",
          text: function () { return s.name; },
          fill: otherLabel,
          fontSize: 12,
        })
      );
    });

    // Focal series on top — thick orange line + bold label
    marks.push(
      Plot.line(focalSeries, {
        x: "year",
        y: "value",
        stroke: T.palette.orange,
        strokeWidth: 3,
      })
    );
    const focalLast = focalSeries[focalSeries.length - 1];
    marks.push(
      Plot.text([focalLast], {
        x: "year",
        y: "value",
        dx: 6,
        textAnchor: "start",
        text: function () { return "Felony Assault"; },
        fill: T.palette.orange,
        fontWeight: 700,
        fontSize: 13,
      })
    );

    return Plot.plot({
      width,
      height: 320,
      marginLeft: 56,
      marginRight: 140,
      marginTop: 24,
      marginBottom: 36,
      style: {
        background: "transparent",
        color: T.palette.ink,
        fontFamily: T.fonts.ui,
        fontSize: 13,
        overflow: "visible",
      },
      x: {
        domain: [2017, 2024],
        label: null,
        tickFormat: function (d) { return String(d); },
        ticks: [2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024],
      },
      y: {
        domain: [0.5, 1.8],
        label: "Index, 2017 = 1.0",
        labelArrow: "none",
        labelAnchor: "top",
        labelOffset: 44,
        grid: true,
        tickFormat: function (d) { return d.toFixed(1); },
      },
      marks: marks,
    });
  });
})();
