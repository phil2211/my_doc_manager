import { useState } from 'react';

export default function ReviewScreen({ document, onSave }) {
  const [metadata, setMetadata] = useState(document?.metadata || {});

  return (
    <div className="p-4 border rounded shadow">
      <h2 className="text-xl mb-2">Review Document</h2>
      <div className="flex flex-col gap-2">
        <input 
          value={metadata.date || ''} 
          onChange={e => setMetadata({...metadata, date: e.target.value})}
          placeholder="Date (YYYY-MM-DD)"
          className="border p-1"
        />
        <input 
          value={metadata.sender || ''} 
          onChange={e => setMetadata({...metadata, sender: e.target.value})}
          placeholder="Sender"
          className="border p-1"
        />
        <input 
          value={metadata.category || ''} 
          onChange={e => setMetadata({...metadata, category: e.target.value})}
          placeholder="Category"
          className="border p-1"
        />
        <button onClick={() => onSave(metadata)} className="bg-green-500 text-white px-4 py-2 rounded">
          Confirm & Save
        </button>
      </div>
    </div>
  );
}