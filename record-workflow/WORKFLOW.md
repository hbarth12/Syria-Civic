# Parliamentary Record draft agent

## Authorized scope
Find recordings of Syrian parliamentary meetings and prepare local bilingual website drafts for the editor. Never deploy or place new work in the public record collection without review. Local draft pages are not a security boundary: keep `dist/record-drafts` out of any hosting upload.

## Discover and track
Search Arabic and English for full recordings of مجلس الشعب hearings, plenary meetings, and committee meetings. Start with the broadcaster behind the existing Al-Souriya recording https://www.youtube.com/watch?v=ivR_t9PEJ6Q and verifiable official parliamentary or broadcaster channels. Verify channel identity from actual source pages, do not assume similarly named channels are official. Distinguish dates of meetings from upload dates, full sessions from clips, and studio commentary from proceedings. Do not claim every meeting has been found.

Keep `state.json` with source URL/video ID, meeting date, title, duration if available, discovery date, status, processing coverage, and blockers. Deduplicate by video ID and meeting identity, comparing `dist/content/parliamentary-record` and existing drafts. Resume partial work instead of starting over. Existing education hearing has English only: Arabic recovery is a backlog item, not a reason to overwrite its English transcript.

## Transcribe and translate
Use available source captions or an authorized transcription tool. Browser transcript export is an option when supported. If audio-only transcription cannot run with current tools, record `needs_transcription` and the exact missing capability; do not pretend to have listened or transcribed. Do not purchase tools or expose credentials.

Save untouched source captions with timestamps under `sources/<video-id>/`. Clean Arabic conservatively: punctuation, paragraph breaks, and caption joins only; preserve substantive repetition, qualifications, uncertainty, names, numbers, and votes. Never reconstruct missing speech. Mark inaudible/uncertain passages and unknown speakers explicitly. Translate the Arabic into English in aligned timestamped segments. Keep untranslated/unfinished segments clearly marked; never silently truncate a long session. Do not treat the existing English translation as the Arabic original.

Compare both versions for omissions and differences in names, numbers, dates, negation, and policy terminology. Record source coverage and review issues in `<slug>.review.md`. Label machine-assisted drafts and distinguish editorial speaker labels from those supplied by the source. Use `transcriptFormat: edited` for cleaned transcripts rather than claiming verbatim accuracy. No draft is complete until both languages cover all available source segments; partial drafts remain explicitly partial.

## Output
Write `drafts/<slug>.json` using the example schema. Do not alter published source records. Run `python3 scripts/build_records.py` from the project root. This renders `dist/record-drafts/index.html` and individual review pages without adding them to the public collection. Verify all local links, both RTL Arabic and English, source timestamps, and completeness. Notify the editor when a reviewable draft is ready or a new blocker requires action. Stay quiet for unchanged or duplicate discoveries.

Promotion to the public collection is an editor-authorized separate step. Copy approved JSON to `dist/content/parliamentary-record/`, remove draft status, and rebuild; never infer approval from elapsed time.
