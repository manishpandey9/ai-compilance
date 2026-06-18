import type { InputHTMLAttributes, LabelHTMLAttributes, ReactNode } from "react";

import { cn } from "@/lib/cn";
import { focusRing, focusRingLight } from "@/lib/focus";

type InputProps = InputHTMLAttributes<HTMLInputElement> & {
  surface?: "dark" | "light";
};

export function Input({ className, surface = "dark", ...props }: InputProps) {
  const ring = surface === "light" ? focusRingLight : focusRing;

  return (
    <input
      className={cn(
        "mt-1 w-full rounded-md border px-4 py-2 focus:outline-none",
        surface === "light"
          ? "border-zinc-300 bg-white text-zinc-900 placeholder:text-zinc-400 focus:border-zinc-500"
          : "border-zinc-700 bg-zinc-900 text-zinc-100 placeholder:text-zinc-500 focus:border-zinc-400",
        ring,
        className,
      )}
      {...props}
    />
  );
}

type FieldProps = {
  label: string;
  htmlFor?: string;
  children: ReactNode;
  error?: string | null;
  surface?: "dark" | "light";
};

export function Field({ label, htmlFor, children, error, surface = "dark" }: FieldProps) {
  return (
    <label className="block" htmlFor={htmlFor}>
      <span className={cn("text-sm", surface === "light" ? "text-zinc-700" : "text-zinc-300")}>
        {label}
      </span>
      {children}
      {error && (
        <p className="mt-1 text-sm text-red-500" role="alert">
          {error}
        </p>
      )}
    </label>
  );
}

type FormErrorProps = LabelHTMLAttributes<HTMLParagraphElement> & {
  message: string;
};

export function FormError({ message, className, ...props }: FormErrorProps) {
  return (
    <p className={cn("text-sm text-red-500", className)} role="alert" {...props}>
      {message}
    </p>
  );
}
