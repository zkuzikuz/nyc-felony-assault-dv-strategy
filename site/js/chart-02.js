/**
 * Chart 02 — Felony assault is NYC's largest violent-felony category.
 * Horizontal bars, descending. Felony Assault highlighted in orange; the
 * other three (Robbery, Rape, Murder) in light grey.
 */
(function () {
  "use strict";
  const figure = document.getElementById("chart-02-container");
  if (!figure) return;
  const T = window.NYCStrategyChart;
  if (!T) return;

  T.mountChart(figure, async function ({ width, Plot }) {
    const resp = await fetch("data/chart-02.json");
    if (!resp.ok) throw new Error("Failed to fetch chart-02 data");
    const data = await resp.json();

    const focal = "Felony Assault";
    const order = data.map(function (d) { return d.category; });

    // Domain padding so the rightmost label has room.
    const maxV = Math.max.apply(null, data.map(function (d) { return d.value; }));
    const xMax = maxV * 1.18;

    return Plot.plot({
      width,
      height: 280,
      marginLeft: 110,
      marginRight: 24,
      marginTop: 12,
      marginBottom: 36,
      style: {
        background: "transparent",
        color: T.palette.ink,
        fontFamily: T.fonts.ui,
        fontSize: 13,
        overflow: "visible",
      },
      x: {
        domain: [0, xMax],
        label: "Reports in 2024",
        labelAnchor: "right",
        labelOffset: 28,
        tickFormat: function (d) {
          if (d === 0) return "0";
          if (d >= 1000) return (d / 1000) + "k";
          return String(d);
        },
        grid: true,
      },
      y: {
        domain: order,
        label: null,
        tickSize: 0,
        padding: 0.4,
      },
      marks: [
        Plot.barX(data, {
          x: "value",
          y: "category",
          fill: function (d) {
            return d.category === focal ? T.palette.orange : T.palette.light;
          },
          insetTop: 4,
          insetBottom: 4,
        }),
        Plot.text(data, {
          x: "value",
          y: "category",
          dx: 8,
          textAnchor: "start",
          text: function (d) { return d.value.toLocaleString(); },
          fill: function (d) {
            return d.category === focal ? T.palette.orange : T.palette.neutral;
          },
          fontWeight: function (d) {
            return d.category === focal ? 700 : 500;
          },
          fontSize: 14,
        }),
        Plot.ruleX([0], { stroke: T.palette.mute, strokeOpacity: 0.4 }),
      ],
    });
  });
})();
