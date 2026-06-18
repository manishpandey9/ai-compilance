/** Renders multi-paragraph help text from the API. */
export function QuestionHelp({ text }: { text: string }) {
  const blocks = text.split(/\n\n+/).filter(Boolean);

  return (
    <div className="mt-4 space-y-4 rounded-md border border-zinc-200 bg-zinc-50 px-4 py-3 text-sm leading-relaxed text-zinc-600">
      {blocks.map((block, blockIdx) => {
        const lines = block.split("\n").filter(Boolean);

        if (lines.length === 1) {
          return <p key={blockIdx}>{lines[0]}</p>;
        }

        return (
          <div key={blockIdx} className="space-y-2">
            {lines.map((line, lineIdx) => {
              const next = lines[lineIdx + 1];
              const isHeading =
                !line.startsWith("Example:") &&
                next !== undefined &&
                !next.startsWith("Example:") &&
                line.length <= 48 &&
                !line.endsWith(".");

              if (isHeading) {
                return (
                  <p key={lineIdx} className="font-medium text-zinc-900">
                    {line}
                  </p>
                );
              }

              if (line.startsWith("Example:")) {
                return (
                  <p
                    key={lineIdx}
                    className="border-l-2 border-zinc-300 pl-3 text-zinc-500"
                  >
                    {line}
                  </p>
                );
              }

              return <p key={lineIdx}>{line}</p>;
            })}
          </div>
        );
      })}
    </div>
  );
}
