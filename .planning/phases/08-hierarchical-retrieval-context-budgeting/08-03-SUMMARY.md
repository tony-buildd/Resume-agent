# Summary 08-03

## Outcome

Moved blueprint evidence selection onto explicit budget policy instead of fixed small caps:

- blueprint assembly now consumes a configurable evidence budget policy covering roles, stories, and bullets
- blueprint artifacts include both `selectionTraces` and `budgetPolicy`
- runtime blueprint review now uses budgeted canonical context rather than replaying the full raw session context

## Verification

- API smoke for blueprint artifact budget policy and trace payloads
- backend blueprint helper smoke for policy-respecting section limits
