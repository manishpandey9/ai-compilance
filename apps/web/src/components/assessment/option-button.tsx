import { cn } from "@/lib/cn";
import { focusRing, focusRingLight } from "@/lib/focus";

type OptionButtonProps = {
  label: string;
  selected?: boolean;
  disabled?: boolean;
  onClick: () => void;
  surface?: "dark" | "light";
};

export function OptionButton({
  label,
  selected,
  disabled,
  onClick,
  surface = "light",
}: OptionButtonProps) {
  const ring = surface === "light" ? focusRingLight : focusRing;
  const isLight = surface === "light";

  return (
    <button
      type="button"
      disabled={disabled}
      aria-pressed={selected}
      onClick={onClick}
      className={cn(
        "block w-full border-b py-3.5 text-left text-sm transition-colors",
        isLight ? "border-zinc-200" : "border-zinc-800",
        "disabled:cursor-not-allowed disabled:opacity-50",
        selected
          ? cn("font-medium", isLight ? "text-zinc-900" : "text-white")
          : isLight
            ? "text-zinc-600 hover:text-zinc-900"
            : "text-zinc-300 hover:text-zinc-100",
        ring,
      )}
    >
      {label}
    </button>
  );
}

type RuleCitationProps = {
  ruleCode: string;
  source: string;
  rationale: string;
  surface?: "dark" | "light";
};

export function RuleCitation({ ruleCode, source, rationale, surface = "light" }: RuleCitationProps) {
  const isLight = surface === "light";

  return (
    <li className="py-4 text-sm">
      <p className={cn("text-mono-ui", isLight ? "text-zinc-800" : "text-zinc-300")}>{ruleCode}</p>
      <p className={cn("mt-1", isLight ? "text-zinc-500" : "text-zinc-500")}>{source}</p>
      <p className={cn("mt-2", isLight ? "text-zinc-600" : "text-zinc-400")}>{rationale}</p>
    </li>
  );
}
