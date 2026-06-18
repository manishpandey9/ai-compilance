import { cn } from "@/lib/cn";

type RiskTierCardProps = {
  tier: string;
  confidence?: string;
  role?: string;
  surface?: "dark" | "light";
};

/** Result block — typography only */
export function RiskTierCard({ tier, confidence, role, surface = "light" }: RiskTierCardProps) {
  const isLight = surface === "light";

  return (
    <div className={isLight ? "border-t border-zinc-200 pt-8" : "border-t border-zinc-800 pt-8"}>
      <p className="text-mono-ui text-zinc-500">Risk tier</p>
      <p
        className={cn(
          "mt-2 text-3xl font-semibold capitalize tracking-tight",
          isLight ? "text-zinc-900" : "text-zinc-50",
        )}
      >
        {tier}
      </p>
      {confidence && (
        <p className={cn("mt-3 text-sm", isLight ? "text-zinc-600" : "text-zinc-400")}>
          Confidence: {confidence}
        </p>
      )}
      {role && (
        <p className={cn("mt-1 text-sm", isLight ? "text-zinc-600" : "text-zinc-400")}>
          Role: {role.replace(/_/g, " ")}
        </p>
      )}
    </div>
  );
}
