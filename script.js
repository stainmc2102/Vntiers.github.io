
fetch("data/leaderboard.json")
  .then(res => res.json())
  .then(data => {
    const container = document.getElementById("tables-container");
    for (const section in data) {
      const players = data[section];
      const tableId = `table-${section}`;
      const title = document.createElement("h2");
      title.textContent = section.toUpperCase();
      container.appendChild(title);
      const table = document.createElement("table");
      table.id = tableId;
      table.className = "display";
      container.appendChild(table);

      let columns;
      if (section === "overall") {
        columns = [
          { title: "Rank", data: "rank" },
          { title: "Player", data: "mcName" },
          { title: "Overall", data: "overallScore" },
          { title: "Tier", data: "overallTier" },
          { title: "Nodebuff", data: "nodebuff" },
          { title: "Sumo", data: "sumo" },
          { title: "Axe", data: "axe" }
        ];
      } else {
        columns = [
          { title: "Rank", data: "rank" },
          { title: "Player", data: "mcName" },
          { title: "Tier", data: "tier" },
          { title: "Score", data: "score" },
          { title: "Tests", data: "testCount" }
        ];
      }

      const tierColumns = ["nodebuff", "sumo", "axe", "build", "tier", "overallTier"];
      columns.forEach(col => {
        if (tierColumns.includes(col.data)) {
          col.render = function (data) {
            return `<span class="tier ${data}">${data}</span>`;
          };
        }
      });

      $(`#${tableId}`).DataTable({
        data: players,
        columns: columns,
        paging: true,
        searching: true,
        info: false
      });
    }
  });
