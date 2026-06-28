// Numbered progress stepper for the loan-application wizard.
// Pattern drawn from Upstart / LendingClub / SoFi personal-loan flows:
// a horizontal row of numbered nodes with a connecting rail, the current
// step highlighted and completed steps shown as done.

export interface Step {
  n: number;
  label: string;
}

export default function Stepper({
  steps,
  current,
}: {
  steps: Step[];
  current: number;
}) {
  return (
    <ol className="stepper" aria-label="Application progress">
      {steps.map((s) => {
        const state =
          s.n < current ? "done" : s.n === current ? "active" : "todo";
        return (
          <li key={s.n} className={`step step-${state}`}>
            <span className="step-node" aria-hidden>
              {state === "done" ? "✓" : s.n}
            </span>
            <span className="step-label">{s.label}</span>
          </li>
        );
      })}
    </ol>
  );
}
