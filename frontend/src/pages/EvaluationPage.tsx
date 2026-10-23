import { useState } from 'react';
import { ArrowLeft, BarChart3, CircleHelp, Play, Timer } from 'lucide-react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { compareModels } from '../lib/api';
import type { ModelComparison, ModelComparisonResult } from '../lib/types';
import { ThemeToggle } from '../components/ThemeToggle';

const exampleQueries = [
  { language: 'Hindi', query: 'गेहूं की फसल में सिंचाई कब करनी चाहिए?' },
  { language: 'Telugu', query: 'వరి పంటలో ఆకు ముడత తెగులు నివారణ ఎలా చేయాలి?' },
  { language: 'English', query: 'How do I control pests in mango trees?' },
];

function Metric({ label, value, lowerIsBetter = false, emptyLabel = 'Pending' }: { label: string; value?: number | null; lowerIsBetter?: boolean; emptyLabel?: string }) {
  return (
    <div className="rounded-xl border border-slate-200 dark:border-neutral-800 p-3">
      <div className="text-[10px] uppercase tracking-wide text-slate-500 dark:text-neutral-400">{label}</div>
      <div className="mt-1 text-lg font-bold text-slate-900 dark:text-white">
        {value === undefined || value === null ? emptyLabel : value.toFixed(3)}
      </div>
      {value !== undefined && value !== null && <div className="text-[9px] text-slate-400">{lowerIsBetter ? 'Lower is better' : 'Higher is better'}</div>}
    </div>
  );
}

function ModelCard({ model }: { model: ModelComparisonResult }) {
  return (
    <section className="rounded-2xl border border-slate-200 dark:border-neutral-800 bg-white dark:bg-neutral-900 p-5 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="text-xs font-semibold uppercase tracking-wider text-emerald-700 dark:text-emerald-300">{model.provider === 'qwen' ? 'GROQ · QWEN' : 'GROQ · GPT-OSS'}</div>
          <h3 className="mt-1 break-all text-sm font-bold text-slate-900 dark:text-white">{model.model}</h3>
        </div>
        <span className={`rounded-full px-2 py-1 text-[10px] font-bold ${model.status === 'ok' ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-200' : 'bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-200'}`}>
          {model.status === 'ok' ? 'Completed' : 'Unavailable'}
        </span>
      </div>

      <div className="mt-4 grid grid-cols-2 gap-2 sm:grid-cols-4">
        <div className="rounded-xl border border-slate-200 dark:border-neutral-800 p-3">
          <div className="flex items-center gap-1 text-[10px] uppercase tracking-wide text-slate-500"><Timer className="h-3 w-3" /> Generation</div>
          <div className="mt-1 text-lg font-bold text-slate-900 dark:text-white">{model.status === 'ok' ? `${model.generation_latency_ms.toLocaleString()} ms` : '—'}</div>
          <div className="text-[9px] text-slate-400">End-to-end call time</div>
        </div>
        <div className="rounded-xl border border-slate-200 dark:border-neutral-800 p-3">
          <div className="text-[10px] uppercase tracking-wide text-slate-500">Answer size</div>
          <div className="mt-1 text-lg font-bold text-slate-900 dark:text-white">{model.answer_characters?.toLocaleString() ?? '—'}</div>
          <div className="text-[9px] text-slate-400">Characters</div>
        </div>
        <Metric label="Semantic faithfulness*" value={model.metrics?.semantic_faithfulness} />
        <Metric label="Answer relevance*" value={model.metrics?.answer_relevance} />
      </div>
      {model.status === 'ok' ? (
        <div className="mt-4 rounded-xl bg-slate-50 dark:bg-neutral-950 p-3 text-sm leading-relaxed text-slate-700 dark:text-neutral-200 whitespace-pre-wrap">{model.answer}</div>
      ) : (
        <p className="mt-4 rounded-xl bg-rose-50 dark:bg-rose-950/40 p-3 text-xs text-rose-800 dark:text-rose-200">{model.error}</p>
      )}
      <div className="mt-3 grid gap-x-4 gap-y-1 text-xs text-amber-800 dark:text-amber-200 sm:grid-cols-2">
        {model.metrics?.unsupported_claim_rate !== null && model.metrics?.unsupported_claim_rate !== undefined
          ? <span>Unverified claim estimate: {(model.metrics.unsupported_claim_rate * 100).toFixed(1)}%</span>
          : <span>Unverified claim estimate: Pending judge</span>}
        {model.metrics?.contradicted_claim_rate !== null && model.metrics?.contradicted_claim_rate !== undefined
          ? <span>Contradicted claim estimate: {(model.metrics.contradicted_claim_rate * 100).toFixed(1)}%</span>
          : <span>Contradicted claim estimate: Pending judge</span>}
      </div>
      <div className="mt-2 text-xs text-slate-500 dark:text-neutral-400">
        <strong>Reference-based correctness:</strong>{' '}
        {model.metrics?.factual_correctness == null ? 'Not scored; add a reviewed reference answer.' : `${model.metrics.factual_correctness.toFixed(3)} (judge estimate)`}
      </div>
      {model.claim_reviews?.length ? (
        <details className="mt-3 rounded-xl border border-slate-200 dark:border-neutral-800 p-3">
          <summary className="cursor-pointer text-xs font-bold">Claim-level evidence review ({model.claim_reviews.length})</summary>
          <ul className="mt-2 space-y-2">
            {model.claim_reviews.map((review, index) => (
              <li key={`${index}-${review.claim}`} className="rounded-lg bg-slate-50 dark:bg-neutral-950 p-2 text-xs">
                <div className="font-semibold">{review.verdict.replace('_', ' ').toUpperCase()} · {review.claim}</div>
                <div className="mt-1 text-slate-500 dark:text-neutral-400">Sources: {review.source_ranks.length ? review.source_ranks.map((rank) => `Source ${rank}`).join(', ') : 'No supporting source identified'}</div>
                {review.rationale && <p className="mt-1 text-slate-600 dark:text-neutral-300">{review.rationale}</p>}
              </li>
            ))}
          </ul>
        </details>
      ) : null}
      <details className="mt-2 text-[10px] text-slate-500 dark:text-neutral-400">
        <summary className="cursor-pointer">Lexical overlap diagnostics</summary>
        <p className="mt-1">Evidence token coverage: {model.metrics?.evidence_token_coverage.toFixed(3) ?? '—'} · Question token coverage: {model.metrics?.question_token_coverage.toFixed(3) ?? '—'} · Unmatched token proxy: {model.metrics?.unmatched_token_share_proxy == null ? '—' : `${(model.metrics.unmatched_token_share_proxy * 100).toFixed(1)}%`}</p>
      </details>
    </section>
  );
}

export function EvaluationPage() {
  const navigate = useNavigate();
  const [query, setQuery] = useState(exampleQueries[0].query);
  const [referenceAnswer, setReferenceAnswer] = useState('');
  const [result, setResult] = useState<ModelComparison | null>(null);
  const [error, setError] = useState('');
  const [running, setRunning] = useState(false);

  const runComparison = async () => {
    if (!query.trim()) return;
    setRunning(true);
    setError('');
    setResult(null);
    try {
      setResult(await compareModels(query.trim(), referenceAnswer));
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'The comparison request failed.');
    } finally {
      setRunning(false);
    }
  };

  return (
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }} className="min-h-screen bg-slate-50 dark:bg-black text-slate-900 dark:text-white pb-28">
      <header className="sticky top-0 z-10 flex items-center justify-between border-b border-slate-200 dark:border-neutral-800 bg-white/90 dark:bg-black/90 px-4 py-3 backdrop-blur">
        <button onClick={() => navigate('/')} className="inline-flex items-center gap-2 text-sm font-semibold"><ArrowLeft className="h-4 w-4" /> AgriGenius</button>
        <ThemeToggle />
      </header>
      <main className="mx-auto max-w-6xl px-4 py-7 sm:px-8 sm:py-10">
        <div className="max-w-3xl">
          <div className="inline-flex items-center gap-2 rounded-full border border-emerald-200 dark:border-neutral-700 bg-white dark:bg-neutral-900 px-3 py-1 text-[11px] font-bold text-emerald-800 dark:text-emerald-200"><BarChart3 className="h-3.5 w-3.5" /> Three-generator comparison</div>
          <h1 className="mt-4 text-3xl font-extrabold tracking-tight sm:text-4xl">LLM testing and quality</h1>
          <p className="mt-3 text-sm leading-relaxed text-slate-600 dark:text-neutral-400">Qwen 3.8 27B, GPT-OSS 20B, and GPT-OSS 120B receive the same retrieved KCC passages. One Gemini 3.5 Flash-Lite call reviews their claims against those passages; RAGAS is not used. Judge scores are estimates, not ground truth.</p>
        </div>

        <section className="mt-7 rounded-2xl border border-slate-200 dark:border-neutral-800 bg-white dark:bg-neutral-900 p-4 shadow-sm sm:p-6">
          <label htmlFor="eval-query" className="text-sm font-bold">Question to evaluate</label>
          <textarea id="eval-query" value={query} onChange={(event) => setQuery(event.target.value)} rows={3} className="mt-2 w-full resize-y rounded-xl border border-slate-300 dark:border-neutral-700 bg-white dark:bg-neutral-950 px-3 py-2.5 text-sm outline-none focus:border-emerald-500" />
          <label htmlFor="eval-reference" className="mt-4 block text-sm font-bold">Reviewed reference answer <span className="font-normal text-slate-500">(optional; enables reference-based correctness estimate)</span></label>
          <textarea id="eval-reference" value={referenceAnswer} onChange={(event) => setReferenceAnswer(event.target.value)} rows={2} className="mt-2 w-full resize-y rounded-xl border border-slate-300 dark:border-neutral-700 bg-white dark:bg-neutral-950 px-3 py-2.5 text-sm outline-none focus:border-emerald-500" placeholder="Enter an expert-reviewed answer for this exact question" />
          <div className="mt-2 flex flex-wrap gap-2">
            {exampleQueries.map((example) => (
              <button key={example.language} type="button" onClick={() => setQuery(example.query)} className="rounded-full border border-slate-200 dark:border-neutral-700 px-3 py-1.5 text-[10px] font-semibold text-slate-600 dark:text-neutral-300 hover:border-emerald-500">{example.language} example</button>
            ))}
          </div>
          <button type="button" disabled={running || !query.trim()} onClick={runComparison} className="mt-4 inline-flex items-center gap-2 rounded-xl bg-emerald-700 px-4 py-2.5 text-xs font-bold text-white disabled:cursor-wait disabled:opacity-60">
            <Play className="h-3.5 w-3.5" /> {running ? 'Running 3 generators and judge…' : 'Run 3-model evaluation'}
          </button>
          {error && <p className="mt-3 rounded-lg bg-rose-50 dark:bg-rose-950/40 p-3 text-xs text-rose-800 dark:text-rose-200">{error}</p>}
        </section>

        {result && <>
          <div className="mt-6 rounded-xl border border-sky-200 dark:border-neutral-800 bg-sky-50 dark:bg-neutral-900 p-4 text-xs leading-relaxed text-sky-900 dark:text-neutral-200">
            <div className="flex items-center gap-2 font-bold"><CircleHelp className="h-4 w-4" /> Test run details</div>
            <p className="mt-1">Retrieved passages: {result.source_count}. Judge: {result.evaluation.judge_model}. Status: {result.evaluation.status}{result.evaluation.judge_latency_ms ? ` (${result.evaluation.judge_latency_ms.toLocaleString()} ms)` : ''}. {result.evaluation.note}</p>
            {result.evaluation.error && <p className="mt-1 text-amber-800 dark:text-amber-200">Judge unavailable: {result.evaluation.error}. Lexical diagnostics remain available, but semantic scores are pending.</p>}
            {result.evaluation.status === 'skipped_no_context' && <p className="mt-1">No passages were retrieved, so context-based quality scores were skipped.</p>}
            {result.evaluation.status === 'skipped_no_successful_generation' && <p className="mt-1">No model returned an answer, so scoring was skipped.</p>}
          </div>
          <div className="mt-5 grid gap-4 lg:grid-cols-2 2xl:grid-cols-3">
            {result.models.map((model) => <ModelCard key={model.provider} model={model} />)}
          </div>
          <section className="mt-5 rounded-2xl border border-slate-200 dark:border-neutral-800 bg-white dark:bg-neutral-900 p-5">
            <h2 className="text-sm font-bold">Shared retrieved evidence ({result.sources.length})</h2>
            <div className="mt-3 space-y-3">
              {result.sources.map((source) => (
                <article key={source.rank} className="rounded-xl bg-slate-50 dark:bg-neutral-950 p-3">
                  <div className="text-[10px] font-bold text-emerald-700 dark:text-emerald-300">Source {source.rank} · {source.metadata.Crop || 'Crop unspecified'} · {source.metadata.QueryType || 'Category unspecified'}</div>
                  <p className="mt-1 text-xs leading-relaxed text-slate-700 dark:text-neutral-300">{source.text}</p>
                </article>
              ))}
            </div>
          </section>
        </>}

        <section className="mt-8 rounded-2xl border border-slate-200 dark:border-neutral-800 bg-white dark:bg-neutral-900 p-5 sm:p-6">
          <h2 className="text-lg font-bold">How to read these scores</h2>
          <dl className="mt-4 grid gap-4 text-xs leading-relaxed sm:grid-cols-2 xl:grid-cols-4">
            <div><dt className="font-bold">Semantic faithfulness estimate</dt><dd className="mt-1 text-slate-600 dark:text-neutral-400">Supported material claims divided by reviewed material claims, as judged by Gemini against retrieved passages. The judge can make mistakes.</dd></div>
            <div><dt className="font-bold">Answer relevance estimate</dt><dd className="mt-1 text-slate-600 dark:text-neutral-400">Gemini’s 0–1 judgment of whether the answer addresses the question. It is not factual validation.</dd></div>
            <div><dt className="font-bold">Unverified / contradicted claims</dt><dd className="mt-1 text-slate-600 dark:text-neutral-400">Claims marked not found or contradicted by retrieved evidence. This is a source-grounding estimate, not a definitive hallucination detector.</dd></div>
            <div><dt className="font-bold">Reference-based correctness</dt><dd className="mt-1 text-slate-600 dark:text-neutral-400">Only scored when you provide an expert-reviewed reference answer. It measures judge-estimated alignment with that reference, not objective truth.</dd></div>
          </dl>
          <p className="mt-4 border-t border-slate-100 dark:border-neutral-800 pt-3 text-[10px] text-slate-500 dark:text-neutral-400">* Gemini 3.5 Flash-Lite is a model-based evaluator, independent of RAGAS. It uses one bounded call for all three answers. Claim rationales are explanations of judge decisions, not faithful explanations of the generators’ internal reasoning. Keep human agronomic review for safety-sensitive advice. LIME on source cards remains the model-attribution explanation for the BGE reranker.</p>
        </section>
      </main>
    </motion.div>
  );
}
