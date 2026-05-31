type FindingListProps = {
  strengths: string[];
  risks: string[];
};

export function FindingList({ strengths, risks }: FindingListProps) {
  return (
    <section className="report-section">
      <header className="section-heading">
        <h2>优势与风险</h2>
      </header>
      <div className="finding-grid">
        <div>
          <h3>优势</h3>
          <ul>
            {strengths.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
        <div>
          <h3>风险</h3>
          <ul>
            {risks.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  );
}
