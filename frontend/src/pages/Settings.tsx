import { useEffect, useState } from "react";
import { getSettings, updateSettings, type SettingsResponse } from "../api/client";

export default function Settings() {
  const [settings, setSettings] = useState<SettingsResponse | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void getSettings()
      .then(setSettings)
      .catch((settingsError) => setError(String(settingsError)));
  }, []);

  async function saveSettings() {
    if (!settings) return;
    setMessage(null);
    setError(null);
    try {
      const updated = await updateSettings(settings);
      setSettings(updated);
      setMessage("Settings saved.");
    } catch (saveError) {
      setError(String(saveError));
    }
  }

  if (!settings) {
    return <p className="status">Loading settings...</p>;
  }

  return (
    <section className="card grid">
      <h2>Processing Settings</h2>
      <label>
        <input
          type="checkbox"
          checked={settings.llm_enabled}
          onChange={(event) => setSettings({ ...settings, llm_enabled: event.target.checked })}
        />{" "}
        Enable LLM backends (Ollama / OpenAI-compatible)
      </label>
      <div>
        <label htmlFor="llmBaseUrl">LLM base URL</label>
        <input
          id="llmBaseUrl"
          value={settings.llm_base_url}
          onChange={(event) => setSettings({ ...settings, llm_base_url: event.target.value })}
        />
      </div>
      <div>
        <label htmlFor="llmModel">LLM model</label>
        <input
          id="llmModel"
          value={settings.llm_model}
          onChange={(event) => setSettings({ ...settings, llm_model: event.target.value })}
        />
      </div>
      <div>
        <label htmlFor="threshold">LLM confidence threshold</label>
        <input
          id="threshold"
          type="number"
          min="0"
          max="1"
          step="0.05"
          value={settings.llm_confidence_threshold}
          onChange={(event) =>
            setSettings({
              ...settings,
              llm_confidence_threshold: Number(event.target.value),
            })
          }
        />
      </div>
      <div>
        <label htmlFor="ocrDpi">OCR DPI</label>
        <input
          id="ocrDpi"
          type="number"
          min="72"
          max="600"
          value={settings.ocr_dpi}
          onChange={(event) => setSettings({ ...settings, ocr_dpi: Number(event.target.value) })}
        />
      </div>
      <button onClick={() => void saveSettings()}>Save settings</button>
      {message && <p className="success">{message}</p>}
      {error && <p className="error">{error}</p>}
    </section>
  );
}
