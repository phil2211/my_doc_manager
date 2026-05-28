# Test PDF fixtures

Sample PDFs for manual upload testing and future integration tests.

Regenerate all files:

```bash
cd backend && source .venv/bin/activate
python tests/fixtures/generate_test_pdfs.py
```

## Files

| File | Pages | Expected type | Notes |
|------|-------|---------------|-------|
| `bill_invoice_de.pdf` | 1 | bill | German invoice, ACME GmbH, date 2024-03-15 |
| `bill_invoice_en.pdf` | 1 | bill | English invoice, TechCorp Inc. |
| `bill_minimal.pdf` | 1 | bill | Minimal invoice for quick smoke tests |
| `contract_mietvertrag_de.pdf` | 1 | contract | German rental contract |
| `contract_agreement_en.pdf` | 1 | contract | English service agreement |
| `commercial_angebot_de.pdf` | 1 | commercial | German promotion/offer |
| `information_mitteilung_de.pdf` | 1 | information | City notice / Mitteilung |
| `other_memo.pdf` | 1 | other | Internal memo, no doc-type keywords |
| `multipage_invoice_de.pdf` | 2 | bill | Single invoice spanning two pages |
| `multipage_two_bills_blank.pdf` | 3 | bill (×2) | Two invoices separated by a blank page |
| `multipage_two_docs_page_pattern.pdf` | 2 | bill + contract | Bill then contract starting with "Seite 1 von 3" |
