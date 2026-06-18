import Link from "next/link";
import type { ButtonHTMLAttributes, ReactNode } from "react";

import { cn } from "@/lib/cn";
import { focusRing, focusRingLight } from "@/lib/focus";

type ButtonVariant = "primary" | "secondary" | "text";
type ButtonSize = "md" | "lg";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: ButtonVariant;
  size?: ButtonSize;
  surface?: "dark" | "light";
};

const sizeClasses: Record<ButtonSize, string> = {
  md: "px-4 py-2 text-sm",
  lg: "px-5 py-2.5 text-sm",
};

export function Button({
  variant = "primary",
  size = "md",
  surface = "dark",
  className,
  disabled,
  children,
  type,
  ...props
}: ButtonProps) {
  const ring = surface === "light" ? focusRingLight : focusRing;

  return (
    <button
      type={type ?? "button"}
      disabled={disabled}
      className={cn(
        "rounded-md font-medium transition-colors disabled:cursor-not-allowed disabled:opacity-50",
        sizeClasses[size],
        variant === "primary" &&
          (surface === "light"
            ? "bg-zinc-900 text-white hover:bg-zinc-800"
            : "bg-white text-zinc-950 hover:bg-zinc-200"),
        variant === "secondary" &&
          (surface === "light"
            ? "border border-zinc-300 bg-transparent text-zinc-900 hover:border-zinc-500"
            : "border border-zinc-700 bg-transparent text-zinc-100 hover:border-zinc-500"),
        variant === "text" &&
          (surface === "light"
            ? "px-0 text-zinc-600 hover:text-zinc-900"
            : "px-0 text-zinc-400 hover:text-zinc-100"),
        variant === "text" && "hover:underline underline-offset-4",
        ring,
        className,
      )}
      {...props}
    >
      {children}
    </button>
  );
}

type ButtonLinkProps = {
  href: string;
  variant?: ButtonVariant;
  size?: ButtonSize;
  surface?: "dark" | "light";
  className?: string;
  children: ReactNode;
};

export function ButtonLink({
  href,
  variant = "primary",
  size = "md",
  surface = "dark",
  className,
  children,
}: ButtonLinkProps) {
  const ring = surface === "light" ? focusRingLight : focusRing;

  return (
    <Link
      href={href}
      className={cn(
        "inline-flex items-center justify-center rounded-md font-medium transition-colors",
        sizeClasses[size],
        variant === "primary" &&
          (surface === "light"
            ? "bg-zinc-900 text-white hover:bg-zinc-800"
            : "bg-white text-zinc-950 hover:bg-zinc-200"),
        variant === "secondary" &&
          (surface === "light"
            ? "border border-zinc-300 text-zinc-900 hover:border-zinc-500"
            : "border border-zinc-700 text-zinc-100 hover:border-zinc-500"),
        variant === "text" &&
          (surface === "light"
            ? "px-0 text-zinc-600 hover:text-zinc-900"
            : "px-0 text-zinc-400 hover:text-zinc-100"),
        variant === "text" && "hover:underline underline-offset-4",
        ring,
        className,
      )}
    >
      {children}
    </Link>
  );
}
