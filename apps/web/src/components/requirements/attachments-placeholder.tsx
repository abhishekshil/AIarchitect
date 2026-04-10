/**
 * Reserved layout for Phase 14+ file uploads (PDF, docx, pasted specs).
 * Keeps a stable slot in the intake flow without wiring storage yet.
 */
export function AttachmentsPlaceholder() {
  return (
    <section
      aria-labelledby="attachments-heading"
      className="rounded-xl border border-dashed border-zinc-300 bg-zinc-50/50 p-5 dark:border-zinc-600 dark:bg-zinc-900/40"
    >
      <h2
        id="attachments-heading"
        className="text-sm font-semibold text-zinc-700 dark:text-zinc-200"
      >
        Attachments
      </h2>
      <p className="mt-1 text-xs text-zinc-500 dark:text-zinc-400">
        File uploads will attach supporting documents to this requirement. Not available yet — paste
        everything important into the text area for now.
      </p>
      <div className="mt-4 flex min-h-[88px] items-center justify-center rounded-lg border border-dashed border-zinc-200 bg-white/60 text-center text-xs text-zinc-400 dark:border-zinc-700 dark:bg-zinc-950/60 dark:text-zinc-500">
        Drop files here (coming soon)
      </div>
    </section>
  );
}
