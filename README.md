# AgriVision AI

A work-in-progress computer-vision project exploring plant-health analysis from images.

## Project components

- `apps/farmer_mobile/` — Flutter mobile application.
- `backend/` — FastAPI service.
- `apps/admin_web/` — Arabic ASP.NET Core 9 admin dashboard that consumes the FastAPI service. It provides an overview, live database/API diagnostics, 14-day analysis activity and result summaries, user/crop/model controls, and a CSV summary report.
- `ai/`, `research/`, and `scripts/` — model and engineering code.

## Current limits

The plant classifier is experimental and has not been validated for field diagnosis. Pest detection, severity estimation, treatment advice, and live camera monitoring are not available as validated capabilities. The admin dashboard is an initial implementation; it requires a running FastAPI service, an administrator account, and a configured database, and still needs broader operational review before production use.

Detailed run outputs, datasets, personal reports, social-post drafts, and internal roadmaps are kept outside this public repository.

## License

See [LICENSE](LICENSE).
