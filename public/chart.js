const currentDay = new Date().toISOString().slice(0, 10);

const getSlots = async () => {
  const url = "https://s3.castelnuovo.dev/rsc.castelnuovo.dev/data.json";

  const slots = await fetch(url, { cache: "no-store" })
    .then((response) => response.json())
    .then((data) => {
      return data;
    })
    .catch((error) => {
      console.error(error);
    });

  return slots;
};

const attachGraph = (day, config) => {
  let graph = document.createElement("canvas");

  graph.id = day;
  graph.innerHTML = `<p>Je browser ondersteunt geen canvas.</p>`;

  document.querySelector("main > section").appendChild(graph);

  new Chart(document.getElementById(day), config);
};

const createGraph = (day, slots) => {
  const labels = slots.map((slot) => slot[0]);
  const data = slots.map((slot) => slot[1]);

  // Don't show graph with only last hour left
  if (labels.length < 2) {
    return;
  }

  const dateString = new Date(day).toLocaleDateString("nl-NL", {
    weekday: "long",
    month: "long",
    day: "numeric",
  });

  const config = {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Aantal reserveringen",
          backgroundColor: "#AF221E",
          borderColor: "#AF221E",
          data: data,
        },
      ],
    },
    options: {
      scales: {
        y: {
          max: 60,
          min: 0,
          ticks: {
            stepSize: 5,
          },
        },
      },
      plugins: {
        title: {
          display: true,
          text: dateString,
        },
      },
    },
  };

  attachGraph(day, config);
};

getSlots().then((slots) => {
  const keys = Object.keys(slots);

  keys.forEach((key) => {
    createGraph(key, slots[key]);
  });
});
