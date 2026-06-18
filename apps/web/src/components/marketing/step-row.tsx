type StepRowProps = {
  index: string;
  title: string;
  body: string;
};

export function StepRow({ index, title, body }: StepRowProps) {
  return (
    <li className="grid gap-3 border-t border-slate-800 py-9 first:border-t-0 sm:grid-cols-[3.5rem_1fr] sm:gap-10">
      <span className="text-mono-ui pt-0.5 text-slate-600">{index}</span>
      <div>
        <h3 className="text-lg font-semibold tracking-tight text-slate-100">{title}</h3>
        <p className="mt-2 max-w-xl text-sm leading-relaxed text-slate-400">{body}</p>
      </div>
    </li>
  );
}
