# Accessibility (A11y) Conformance

As part of the 35% milestone, fundamental accessibility practices have been implemented in the frontend.

## Key Features Implemented

1. **Semantic HTML Elements**:
   - The UI structure leverages standard `<main>`, `<nav>`, `<header>`, and `<section>` tags instead of generic `div` elements where appropriate.
   - Proper heading hierarchy (`<h1>` to `<h3>`) is maintained across all pages.

2. **Screen Reader Support**:
   - **ARIA Labels**: Interactive elements, specifically icon-only buttons (like the `RefreshCw` button on the Dashboard), are equipped with `aria-label` tags (e.g., `aria-label="Refresh Data"`).
   - **Hidden Elements**: Decorative icons use `aria-hidden="true"` to prevent screen readers from announcing meaningless visual clutter.
   - **Complex Visualizations**: The Recharts graphs have been wrapped in `div` containers with `tabIndex={0}` and descriptive `aria-label` properties (e.g., `aria-label="Line chart showing solar generation versus load over 24 hours"`), allowing keyboard navigation to focus on the chart and screen readers to explain its context.

3. **Keyboard Navigation**:
   - Focus rings (`focus:ring-2`, `focus:outline-none`) are implemented on buttons and interactive elements using Tailwind CSS.
   - Modals can be closed using standard keyboard commands, and input forms are fully tabbable.

4. **Color Contrast & Readability**:
   - The dark mode color palette (slate-900, slate-800, text-white) adheres to WCAG AA contrast ratios for text.
   - The localized Tamil fonts use system-default sans-serif stacks that render legibly on all modern OS environments.

## Future A11y Work (Post-35%)
- Granular data-table screen reader announcements for the interactive scheduler timeline.
- A dedicated high-contrast light mode toggle.
