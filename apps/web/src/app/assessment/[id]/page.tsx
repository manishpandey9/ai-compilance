"use client";

import { useParams } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

import { QuestionHelp } from "@/components/assessment/question-help";
import { OptionButton, RuleCitation } from "@/components/assessment/option-button";
import { SiteFooter } from "@/components/layout/footer";
import { AppShell, MarketingHeader, PageContainer } from "@/components/layout/shell";
import { Button } from "@/components/ui/button";
import { RiskTierCard } from "@/components/ui/card";
import { FormError } from "@/components/ui/input";
import { api, AssessmentResponse, ClassifyResponse, NextQuestion } from "@/lib/api";
import { loadAssessmentDraft, saveAssessmentDraft } from "@/lib/assessment-draft";
import { cn } from "@/lib/cn";
import { focusRingLight } from "@/lib/focus";

function MultiQuestion({
  question,
  initialValue,
  onAnswer,
  disabled,
}: {
  question: NextQuestion;
  initialValue?: unknown;
  onAnswer: (value: unknown) => void;
  disabled: boolean;
}) {
  const [selected, setSelected] = useState<string[]>(() =>
    Array.isArray(initialValue) ? (initialValue as string[]) : [],
  );

  useEffect(() => {
    setSelected(Array.isArray(initialValue) ? (initialValue as string[]) : []);
  }, [question.question_key, initialValue]);

  if (!question.options) return null;

  return (
    <div className="border-t border-zinc-200">
      {question.options.map((opt) => (
        <OptionButton
          key={opt.value}
          label={opt.label}
          selected={selected.includes(opt.value)}
          disabled={disabled}
          surface="light"
          onClick={() => setSelected((prev) => activeToggle(prev, opt.value))}
        />
      ))}
      <Button
        surface="light"
        disabled={disabled || selected.length === 0}
        onClick={() => onAnswer(selected)}
        className="mt-4"
      >
        Continue
      </Button>
    </div>
  );
}

function activeToggle(prev: string[], value: string): string[] {
  return prev.includes(value) ? prev.filter((v) => v !== value) : [...prev, value];
}

function QuestionField({
  question,
  initialValue,
  onAnswer,
  disabled,
}: {
  question: NextQuestion;
  initialValue?: unknown;
  onAnswer: (value: unknown) => void;
  disabled: boolean;
}) {
  const surface = "light" as const;

  if (question.type === "boolean") {
    const boolValue = typeof initialValue === "boolean" ? initialValue : undefined;
    return (
      <div className="flex gap-3" role="group" aria-label={question.label}>
        <Button
          variant={boolValue === true ? "primary" : "secondary"}
          surface="light"
          disabled={disabled}
          onClick={() => onAnswer(true)}
          className={cn(focusRingLight)}
        >
          Yes
        </Button>
        <Button
          variant={boolValue === false ? "primary" : "secondary"}
          surface="light"
          disabled={disabled}
          onClick={() => onAnswer(false)}
          className={cn(focusRingLight)}
        >
          No
        </Button>
      </div>
    );
  }

  if (question.type === "single" && question.options) {
    const selected = typeof initialValue === "string" ? initialValue : undefined;
    return (
      <div className="border-t border-zinc-200" role="radiogroup" aria-label={question.label}>
        {question.options.map((opt) => (
          <OptionButton
            key={opt.value}
            label={opt.label}
            selected={selected === opt.value}
            disabled={disabled}
            surface={surface}
            onClick={() => onAnswer(opt.value)}
          />
        ))}
      </div>
    );
  }

  if (question.type === "multi" && question.options) {
    return (
      <MultiQuestion
        question={question}
        initialValue={initialValue}
        onAnswer={onAnswer}
        disabled={disabled}
      />
    );
  }

  return null;
}

function ResultView({ result }: { result: ClassifyResponse }) {
  const tierLabel =
    result.risk_tier?.replace(/_/g, " ") ?? result.classification_status.replace(/_/g, " ");

  return (
    <PageContainer width="content" className="py-16">
      <main id="main-content">
        <h1 className="text-headline text-zinc-900">Your classification</h1>

        <div className="mt-8">
          <RiskTierCard
            tier={tierLabel}
            confidence={result.confidence}
            role={result.primary_actor_role}
            surface="light"
          />
        </div>

        <p className="text-mono-ui mt-4 text-sm text-zinc-500">
          Based on rule set v{result.rule_version} · legal sources {result.source_version}. Not legal
          advice.
        </p>

        {result.triggered_rules.length > 0 && (
          <div className="mt-10">
            <h2 className="text-title font-semibold text-zinc-900">Why this tier</h2>
            <ul className="mt-2 divide-y divide-zinc-200 border-y border-zinc-200">
              {result.triggered_rules.map((r) => (
                <RuleCitation
                  key={r.rule_code}
                  ruleCode={r.rule_code}
                  source={r.source}
                  rationale={r.rationale}
                  surface="light"
                />
              ))}
            </ul>
          </div>
        )}

        {result.free_preview && (
          <div className="mt-10">
            <h2 className="text-title font-semibold text-zinc-900">Obligations to plan for</h2>
            <ul className="mt-2 divide-y divide-zinc-200 border-y border-zinc-200 text-sm text-zinc-600">
              {result.free_preview.top_obligations.map((o) => (
                <li key={o} className="py-2.5">
                  {o}
                </li>
              ))}
            </ul>
          </div>
        )}

        <section className="mt-16 border-t border-zinc-200 pt-12">
          <h2 className="text-title font-semibold text-zinc-900">Downloadable documents</h2>
          <p className="mt-2 max-w-lg text-sm leading-relaxed text-zinc-600">
            Paid tiers generate editable files: risk memo, Annex IV outline, human oversight plan,
            obligation matrix, and evidence tracker.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <Button
              variant="secondary"
              surface="light"
              onClick={async () => {
                const { checkout_url } = await api.createCheckout(result.assessment_id, "starter_report");
                window.location.href = checkout_url;
              }}
            >
              Starter report ($199)
            </Button>
            <Button
              surface="light"
              onClick={async () => {
                const { checkout_url } = await api.createCheckout(result.assessment_id, "evidence_pack");
                window.location.href = checkout_url;
              }}
            >
              Evidence pack ($699)
            </Button>
          </div>
        </section>
      </main>
    </PageContainer>
  );
}

export default function AssessmentWizardPage() {
  const params = useParams();
  const assessmentId = params.id as string;

  const [data, setData] = useState<AssessmentResponse | null>(null);
  const [result, setResult] = useState<ClassifyResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [prefill, setPrefill] = useState<Record<string, unknown>>({});

  const persistDraft = useCallback(
    (res: AssessmentResponse) => {
      const draft = loadAssessmentDraft();
      saveAssessmentDraft({
        company: draft.company || res.company_name || "",
        system: draft.system || res.system_name || "",
        assessmentId,
        answers: res.answers,
      });
    },
    [assessmentId],
  );

  const load = useCallback(async () => {
    const res = await api.getAssessment(assessmentId);
    setData(res);
    persistDraft(res);

    const draft = loadAssessmentDraft();
    if (draft.answers) {
      setPrefill((prev) => ({ ...draft.answers, ...prev }));
    }

    if (res.next_questions.length === 0 && res.status !== "completed") {
      setLoading(true);
      try {
        const classified = await api.classify(assessmentId);
        setResult(classified);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Classification failed");
      } finally {
        setLoading(false);
      }
    }
  }, [assessmentId, persistDraft]);

  useEffect(() => {
    load().catch((err) => setError(err instanceof Error ? err.message : "Load failed"));
  }, [load]);

  async function handleAnswer(value: unknown) {
    if (!data?.next_questions[0]) return;
    const key = data.next_questions[0].question_key;
    setLoading(true);
    setError(null);
    setPrefill((prev) => {
      const next = { ...prev };
      delete next[key];
      return next;
    });
    try {
      const res = await api.submitAnswers(assessmentId, [{ question_key: key, value }]);
      setData(res);
      persistDraft(res);
      if (res.next_questions.length === 0) {
        const classified = await api.classify(assessmentId);
        setResult(classified);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Submit failed");
    } finally {
      setLoading(false);
    }
  }

  async function handleBack() {
    if (!data?.next_questions[0]) return;
    const currentKey = data.next_questions[0].question_key;
    const order = data.question_order;
    const idx = order.indexOf(currentKey);
    if (idx <= 0) return;

    const prevKey = order[idx - 1];
    const prevValue = data.answers[prevKey] ?? prefill[prevKey];

    setLoading(true);
    setError(null);
    try {
      const res = await api.rewindAssessment(assessmentId, prevKey);
      if (prevValue !== undefined) {
        setPrefill((p) => ({ ...p, [prevKey]: prevValue }));
      }
      setData(res);
      persistDraft(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not go back");
    } finally {
      setLoading(false);
    }
  }

  if (result) {
    return (
      <AppShell variant="light" header={<MarketingHeader variant="light" />} footer={<SiteFooter variant="light" />}>
        <ResultView result={result} />
      </AppShell>
    );
  }

  const question = data?.next_questions[0];
  const canGoBack = question && (data?.question_order.indexOf(question.question_key) ?? 0) > 0;
  const initialValue =
    question &&
    (prefill[question.question_key] ?? data?.answers[question.question_key]);

  return (
    <AppShell variant="light" header={<MarketingHeader variant="light" />} footer={<SiteFooter variant="light" />}>
      <main id="main-content">
        <PageContainer width="form" className="py-16">
          {canGoBack ? (
            <button
              type="button"
              onClick={handleBack}
              disabled={loading}
              className="text-sm text-zinc-500 underline-offset-4 hover:text-zinc-800 hover:underline disabled:opacity-50"
            >
              ← Previous question
            </button>
          ) : (
            <a
              href="/eu-ai-act/compliance-checker"
              className="text-sm text-zinc-500 underline-offset-4 hover:text-zinc-800 hover:underline"
            >
              ← Edit company details
            </a>
          )}
          {data && (
            <p className="text-mono-ui mt-4 text-sm text-zinc-500" aria-live="polite">
              Question {data.progress.answered + 1} of ~{data.progress.answered + data.progress.remaining_estimate}
            </p>
          )}
          {question ? (
            <>
              <h1 className="text-headline mt-6 text-zinc-900">{question.label}</h1>
              {question.help && <QuestionHelp text={question.help} />}
              <div className="mt-8">
                <QuestionField
                  key={question.question_key}
                  question={question}
                  initialValue={initialValue}
                  onAnswer={handleAnswer}
                  disabled={loading}
                />
              </div>
            </>
          ) : (
            <p className="mt-8 text-zinc-600" aria-live="polite" aria-busy={loading}>
              {loading ? "Running classification…" : "Loading…"}
            </p>
          )}
          {error && <FormError message={error} className="mt-4" />}
        </PageContainer>
      </main>
    </AppShell>
  );
}
