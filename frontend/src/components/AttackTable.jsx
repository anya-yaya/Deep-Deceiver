function AttackTable({ events }) {

  const threats = events
    .filter((event) => event.intent === "prompt_injection")
    .slice(0, 10);

  const formatTime = (timestamp) => {
    if (!timestamp) return "-";

    return new Date(timestamp).toLocaleString();
  };

  const formatCategory = (category) => {
    if (!category) return "-";

    return category
      .replaceAll("_", " ")
      .replace(/\b\w/g, (char) => char.toUpperCase());
  };

  return (
    <div className="attack-table-container">

      <div className="section-header">
        <div>
          <h3>Recent Threats</h3>
          <p>Latest detected prompt injection events</p>
        </div>
      </div>

      {threats.length === 0 ? (

        <div className="empty-state">
          No threats detected in the selected time range.
        </div>

      ) : (

        <div className="table-wrapper">

          <table className="attack-table">

            <thead>
              <tr>
                <th>Time</th>
                <th>Category</th>
                <th>Risk</th>
                <th>Route</th>
                <th>Action</th>
              </tr>
            </thead>

            <tbody>

              {threats.map((event, index) => (

                <tr key={`${event.session_id}-${index}`}>

                  <td>
                    {formatTime(event.timestamp)}
                  </td>

                  <td>
                    <span className="category-badge">
                      {formatCategory(event.attack_category)}
                    </span>
                  </td>

                  <td>
                    <span className="risk-value">
                      {(event.final_risk_score * 100).toFixed(1)}%
                    </span>
                  </td>

                  <td>
                    <span className="route-badge shadow">
                      {event.route}
                    </span>
                  </td>

                  <td>
                    <span className="action-badge">
                      {event.action}
                    </span>
                  </td>

                </tr>

              ))}

            </tbody>

          </table>

        </div>

      )}

    </div>
  );
}

export default AttackTable;