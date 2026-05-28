"""Generate sample PDF fixtures for manual and integration testing."""

from __future__ import annotations

from pathlib import Path

import fitz

OUTPUT_DIR = Path(__file__).resolve().parent / "pdfs"


def _save(doc: fitz.Document, filename: str) -> Path:
    path = OUTPUT_DIR / filename
    doc.save(path)
    doc.close()
    return path


def _add_page(doc: fitz.Document, text: str, *, fontsize: float = 11) -> fitz.Page:
    page = doc.new_page()
    page.insert_text((72, 72), text, fontsize=fontsize)
    return page


def bill_invoice_de() -> None:
    doc = fitz.open()
    _add_page(
        doc,
        "ACME GmbH\nMusterstrasse 1\n8000 Zürich\n\n"
        "Rechnung Nr. 2024-12345\nDatum: 15.03.2024\n\n"
        "Kundennummer: K-9876\n\n"
        "Leistungsbeschreibung          Betrag\n"
        "Beratungsleistung              CHF 250.00\n"
        "MWST 8.1%                      CHF 20.25\n\n"
        "Total                          CHF 270.25\n\n"
        "Zahlbar bis: 15.04.2024",
    )
    _save(doc, "bill_invoice_de.pdf")


def bill_invoice_en() -> None:
    doc = fitz.open()
    _add_page(
        doc,
        "TechCorp Inc.\n123 Market Street\nSan Francisco, CA 94105\n\n"
        "Invoice Number: INV-2024-789\nDate: March 20, 2024\n\n"
        "Bill To: Example Customer\n\n"
        "Description                    Amount\n"
        "Software license (annual)      $1,200.00\n"
        "Support package                $300.00\n\n"
        "Total                          $1,500.00\n\n"
        "Payment due within 30 days.",
    )
    _save(doc, "bill_invoice_en.pdf")


def contract_mietvertrag_de() -> None:
    doc = fitz.open()
    _add_page(
        doc,
        "Immobilien AG\n\nMietvertrag\n\n"
        "Zwischen den Parteien:\n"
        "Vermieter: Immobilien AG\n"
        "Mieter: Max Mustermann\n\n"
        "Objekt: Wohnung, Bahnhofstrasse 10, 8001 Zürich\n"
        "Laufzeit: 01.06.2024 bis 31.05.2027\n\n"
        "Monatliche Miete: CHF 1,800.00\n\n"
        "Unterschrift Vermieter: _______________\n"
        "Unterschrift Mieter:    _______________",
    )
    _save(doc, "contract_mietvertrag_de.pdf")


def contract_agreement_en() -> None:
    doc = fitz.open()
    _add_page(
        doc,
        "Global Services Ltd.\n\nService Agreement\n\n"
        "This agreement is entered into between Global Services Ltd. "
        "and the Client named below.\n\n"
        "Term: January 1, 2024 through December 31, 2024\n\n"
        "Scope of work as described in Appendix A.\n\n"
        "Signed by authorized representatives of both parties.",
    )
    _save(doc, "contract_agreement_en.pdf")


def commercial_angebot_de() -> None:
    doc = fitz.open()
    _add_page(
        doc,
        "Elektro Markt AG\n\n"
        "Angebot – Frühlingsaktion 2024\n\n"
        "Exklusives Angebot für unsere Kunden!\n"
        "Rabatt bis 30% auf ausgewählte Produkte.\n\n"
        "Aktion gültig vom 01.04.2024 bis 30.04.2024\n\n"
        "Newsletter-Anmeldung: www.elektro-markt.example/promotion",
    )
    _save(doc, "commercial_angebot_de.pdf")


def information_mitteilung_de() -> None:
    doc = fitz.open()
    _add_page(
        doc,
        "Stadtverwaltung Bern\n\n"
        "Information / Mitteilung\n\n"
        "Betreff: Änderung der Öffnungszeiten\n\n"
        "Sehr geehrte Damen und Herren,\n\n"
        "Wir möchten Sie hiermit informieren, dass ab dem 01.05.2024 "
        "neue Öffnungszeiten gelten.\n\n"
        "Montag–Freitag: 08:00–17:00 Uhr\n\n"
        "Mit freundlichen Grüssen\nStadtverwaltung Bern",
    )
    _save(doc, "information_mitteilung_de.pdf")


def other_memo() -> None:
    doc = fitz.open()
    _add_page(
        doc,
        "Team Update\n\n"
        "Hi everyone,\n\n"
        "Reminder that our weekly sync is moved to Thursday at 10:00.\n"
        "Please bring your notes from last sprint.\n\n"
        "Thanks,\nAlex",
    )
    _save(doc, "other_memo.pdf")


def multipage_invoice_de() -> None:
    doc = fitz.open()
    _add_page(
        doc,
        "Swiss Telecom AG\n\nRechnung Nr. ST-556677\nDatum: 01.02.2024\n\n"
        "Kundennummer: 445566\n\n"
        "Übersicht der Leistungen – Seite 1 von 2",
    )
    _add_page(
        doc,
        "Swiss Telecom AG – Rechnung ST-556677\n\n"
        "Detailpositionen:\n"
        "Mobilfunk-Abo                   CHF 45.00\n"
        "Internet Flat                   CHF 59.00\n"
        "Geräteversicherung              CHF 9.90\n\n"
        "Total                           CHF 113.90\n\n"
        "Seite 2 von 2",
    )
    _save(doc, "multipage_invoice_de.pdf")


def multipage_two_bills_blank() -> None:
    doc = fitz.open()
    _add_page(
        doc,
        "Bäckerei Müller\n\nRechnung Nr. 1001\nDatum: 10.01.2024\n\n"
        "Brötchen, Kaffee                  CHF 12.50\n"
        "Total                             CHF 12.50",
    )
    _add_page(doc, "")
    _add_page(
        doc,
        "Garage Meier\n\nRechnung Nr. 2002\nDatum: 11.01.2024\n\n"
        "Ölwechsel, Filter                 CHF 189.00\n"
        "Total                             CHF 189.00",
    )
    _save(doc, "multipage_two_bills_blank.pdf")


def multipage_two_docs_page_pattern() -> None:
    doc = fitz.open()
    _add_page(
        doc,
        "Versicherung Plus\n\nRechnung Nr. VP-9001\nDatum: 05.06.2024\n\n"
        "Prämie Halbjahr                   CHF 420.00\n"
        "Total                             CHF 420.00",
    )
    _add_page(
        doc,
        "Seite 1 von 3\n\n"
        "Consulting Partners\n\nMietvertrag – Büroräume\n\n"
        "Vereinbarung zwischen Consulting Partners und Mieter GmbH.\n"
        "Laufzeit ab 01.07.2024.\n\n"
        "Unterschrift: _______________",
    )
    _save(doc, "multipage_two_docs_page_pattern.pdf")


def bill_minimal() -> None:
    doc = fitz.open()
    _add_page(
        doc,
        "Quick Shop\nRechnung\nDatum: 28.05.2024\nBetrag CHF 9.90",
        fontsize=12,
    )
    _save(doc, "bill_minimal.pdf")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    generators = [
        bill_invoice_de,
        bill_invoice_en,
        contract_mietvertrag_de,
        contract_agreement_en,
        commercial_angebot_de,
        information_mitteilung_de,
        other_memo,
        multipage_invoice_de,
        multipage_two_bills_blank,
        multipage_two_docs_page_pattern,
        bill_minimal,
    ]
    for gen in generators:
        gen()
    print(f"Created {len(generators)} PDFs in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
